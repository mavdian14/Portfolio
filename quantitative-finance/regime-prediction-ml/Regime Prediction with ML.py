# Databricks notebook source
!pip install cvxpy

# COMMAND ----------

!pip install pandas_datareader

# COMMAND ----------

!pip install yfinance

# COMMAND ----------

!pip install xgboost

# COMMAND ----------

import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt
import datetime as dt
import cvxpy as cp

from scipy.optimize import minimize
from pandas_datareader import data 
import yfinance as yf
from statsmodels.tsa.stattools import adfuller #to check unit root in time series 

import xgboost as xgb

from sklearn import model_selection, preprocessing
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelBinarizer
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet, LogisticRegression
from sklearn.model_selection import KFold, GridSearchCV, TimeSeriesSplit
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score, roc_curve, auc

import warnings
warnings.filterwarnings('ignore')

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC %matplotlib inline

# COMMAND ----------

# using seaborn style (type plt.style.available to see available styles)
plt.style.use("seaborn-dark")

# COMMAND ----------

bigmacro = pd.read_csv("current.csv")
bigmacro = bigmacro.rename(columns={'sasdate':'Date'})
bigmacro = bigmacro.set_index(keys="Date")
#.to_period() converts a dateTimeArray to a periodArray
bigmacro = bigmacro.drop('Transform:')
bigmacro

# COMMAND ----------

# manually put the dates in datetime format. Note that directly using pd.to_datetime does not work fine 
# because up to 1968 (/68 in the index) year are parsed as years of the 21st century, i.g., 1/1/59 -> 2059-01.
years  = np.arange(1959,2022+1,1)
months = np.arange(1,12+1,1)
strdate = []
for y in years:
    for m in months:
        strdate.append( str(y) + "-" + str(m)  )
        if y==2022 and m==7:
            break
# now parse dates
bigmacro.index = pd.to_datetime(strdate, format="%Y-%m", infer_datetime_format=True).to_period("M") 
bigmacro.index.rename("Date", inplace=True)
bigmacro

# COMMAND ----------

#Lets drop NAN rows at the empty month of 7
bigmacro = bigmacro.drop('2022-07')
bigmacro

# COMMAND ----------

# load regimes classifications
recession_periods = pd.read_csv('Recession_Periods.csv')["Regime"]
# and insert them into bigmacro dataframe
bigmacro.insert(loc=0, column="Regime", value=recession_periods.values)
bigmacro

# COMMAND ----------

bigmacro["Regime"].value_counts()

# COMMAND ----------

# dates of normal and recession regimes
normal_dates     = bigmacro[bigmacro["Regime"] == "Normal"].index
recessions_dates = bigmacro[bigmacro["Regime"] == "Recession"].index

# COMMAND ----------

# find indices of recession regimes
#zero_like() returns an array of zeros with the same shape as the input array
rec_idx = np.zeros_like(recessions_dates)
rec_idx[0] = 1
for i, date in enumerate(recessions_dates):
    prev_date = date - 1
    if prev_date not in recessions_dates:
        rec_idx[i] = 1
        rec_idx[i-1] = 1
rec_idx = np.array([False if i==0 else True for i in rec_idx])
recessions_dates[rec_idx]

# COMMAND ----------

# loading the S&P500 index for the current set of dates that we have 
ticker = "^GSPC"
sp500 = yf.download(ticker)
sp500 = sp500['1959-01-01': '2022-06-01']
sp500.insert(loc=0, column="idx", value=np.arange(0,sp500.shape[0]))
sp500 = sp500[["idx","Adj Close"]]
sp500

# COMMAND ----------

# S&P500 are daily data, then we have to find the right recession dates 
rr = []
for date in recessions_dates[rec_idx]:
    rr.append( sp500[str(date)].iloc[0,:]["idx"] ) 
rr = np.array(rr)
rr

# COMMAND ----------

# index of starting recession periods
x1 = np.array(rr)[:-1:2]
# index of ending recession periods
x2 = np.array(rr)[1::2]

fig, ax = plt.subplots(1,1,figsize=(16,10))
#semilogy(x,y) plots x,y on a linear scale on the x-axis & base-10 log scale on the y
ax.semilogy(sp500["Adj Close"].values, label="S&P500")
#axvspan() adds a vertical span across the axes
ax.axvspan(x1[0], x2[0], alpha=0.5, color='gray', label="recession")
for i in range(1,len(x1)):
    ax.axvspan(x1[i], x2[i], alpha=0.5, color='gray')
ax.legend()
ax.grid()
plt.show()

# COMMAND ----------

# S&P Drawdowns
previous_peaks = sp500["Adj Close"].cummax()
drawdowns      = (sp500["Adj Close"] - previous_peaks ) / previous_peaks
drawdowns.plot(grid=True, figsize=(11,5), title="Max drawdonw: {:.2f}% on {}".format(drawdowns.min(),str(drawdowns.idxmin()).split()[0]))
plt.show()

# COMMAND ----------

#Pre-processing the dataset
# compute the NaN (missing values) per columns and eliminate columns with more than 10 missing values
nan_per_col = bigmacro.isnull().sum()
cols_tobe_removed = nan_per_col[ nan_per_col > 10 ].index
bigmacro = bigmacro.drop(columns=cols_tobe_removed, axis=1)

# and now remove those row containing Nan (i.e. belonging to those columns with less than 10 NaNs)
bigmacro = bigmacro.dropna(axis=0)
bigmacro.shape

# COMMAND ----------

for col in bigmacro.columns[1:]:
    for n in [3,6,9,12,18]:
        bigmacro['{} {}M lag'.format(col, n)] = bigmacro[col].shift(n).ffill().values
        
# 1 month ahead prediction
bigmacro["Regime"] = bigmacro["Regime"].shift(-1)

# remove NaN on rows
bigmacro = bigmacro.dropna(axis=0)
bigmacro.head()

# COMMAND ----------

bigmacro.shape

# COMMAND ----------

#Looking for stationarity
significance_level = 0.01 
for col in bigmacro.columns[1:]:
    #adfuller() function returns a tuple of stats from the ADF test
    p_value_adf = adfuller( bigmacro[col] )[1] # 1 to select the p-value
    if p_value_adf > significance_level:
        bigmacro[col] = bigmacro[col].diff()
        
bigmacro = bigmacro.dropna(axis=0)  

# COMMAND ----------

# repeat
for col in bigmacro.columns[1:]:
    p_value_adf = adfuller( bigmacro[col] )[1]
    if p_value_adf > significance_level:
        bigmacro[col] = bigmacro[col].diff()

bigmacro = bigmacro.dropna(axis=0)  

# COMMAND ----------

# repeat 
print("Remaining non stationary series:")
for col in bigmacro.columns[1:]:
    p_value_adf = adfuller( bigmacro[col] )[1] # 1 to select the p-value
    if p_value_adf > significance_level:
        print(col)
bigmacro = bigmacro.dropna(axis=0)  

# COMMAND ----------

# repeat
for col in bigmacro.columns[1:]:
    p_value_adf = adfuller( bigmacro[col] )[1]
    if p_value_adf > significance_level:
        bigmacro[col] = bigmacro[col].diff()

bigmacro = bigmacro.dropna(axis=0) 

# COMMAND ----------

# repeat 
print("Remaining non stationary series:")
for col in bigmacro.columns[1:]:
    p_value_adf = adfuller( bigmacro[col] )[1] # 1 to select the p-value
    if p_value_adf > significance_level:
        print(col)
bigmacro = bigmacro.dropna(axis=0)  

# COMMAND ----------

features  = bigmacro.drop(["Regime"],axis=1)
col_names = features.columns

# Standardize
#standardScaler() removes the mean & scales each feature/variable to unit variance
scaler = StandardScaler()
scaler.fit(features)
standardized_features = scaler.transform(features)

df = pd.DataFrame(data=standardized_features, columns=col_names)
df.insert(loc=0, column="Regime", value=bigmacro["Regime"].values )
df.index = bigmacro.index
df.shape

# COMMAND ----------

df

# COMMAND ----------

#apply() allows you to apply a function along one of the axis of the df
label = df["Regime"].apply(lambda regime: 0 if regime == "Normal" else 1)
df.insert(loc=1, column="label", value=label.values)
df

# COMMAND ----------

# Separate the features from the targets
df_targets  = df["label"].values
df_features = df.iloc[:,2:]
df_features.shape, df_targets.shape

# COMMAND ----------

#Feature Selection using logistic Regression
scoring = "roc_auc"
#timeSeriesSplit() provides train/test indices to split time series data samples that're observed at fixed time intervals, in train/test sets
kfold   = model_selection.TimeSeriesSplit(n_splits=4)
seed    = 8
max_iter = 10000
penalty = "l1"

X = df_features
y = df_targets

# COMMAND ----------

# create regularization hyperparameter space
C = 1 / np.array([0.00000001, 0.00000005, 0.0000001, 0.0000005, 0.000001, 0.000005, 0.00001, 0.00005, 
                  0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000, 5000])

# create hyperparameter options
#hyperparameters = 

# select the estimator
model = LogisticRegression(max_iter=max_iter, penalty=penalty, solver='liblinear')

# perform grid-searchCV to tune the pearameters (GridSearchCV is a technique for finding the optimal parameter values from a given set of parameters in a grid)
lr_gscv = GridSearchCV(estimator=model, param_grid= dict(C=C), 
                       cv=kfold, scoring=scoring).fit(X = X, y = y)

#best_estimator() stores the model that was refit on the whole training data, and is the model that is used when calling predict & score 
lr_gscv_best = lr_gscv.best_estimator_
lr_gscv_best

# COMMAND ----------

# now that we have the best estimator do the penalized linear regression 
lr_l1 = LogisticRegression(C=lr_gscv_best.C, max_iter=lr_gscv_best.max_iter, penalty=penalty,solver='liblinear').fit(X=X, y=y)

# COMMAND ----------

# features selection. SelectFromModel() define model by default value which applied median method to set the threshhold values & fit the model on & y data
model = SelectFromModel(lr_l1, prefit=True)

# COMMAND ----------

# features (columns) that have been selected
#get_support() gets a mask, or integer index, of the features selected
features_idx  = model.get_support()
features_name = df_features.columns[features_idx]

# finally reduce actual dataset to the selected features
df_reduced = model.transform(df_features)
df_reduced = pd.DataFrame(df_reduced, index=df_features.index, columns=features_name)
df_reduced.shape

# COMMAND ----------

# look at the selected features 
features_name, len(features_name)

# COMMAND ----------

# look at the correlation matrix 
df_reduced_corr = df_reduced.corr()
fig, ax = plt.subplots(1,1,figsize=(20, 12))
sns.heatmap(df_reduced_corr, ax=ax, mask=np.zeros_like(df_reduced_corr, dtype=np.bool), 
            cmap=sns.diverging_palette(220, 10, as_cmap=True), square=True)
plt.show()
#diverging_palette() pairs sequential schemes based on 2 different hues so that they diverge from a shared light color

# COMMAND ----------

#Training the Algorithms
split_1 = "2000-11"
split_2 = "2000-12"
df_train_features = df_reduced[:split_1]
df_test_features  = df_reduced[split_2:]

df_train_targets = df["label"][:split_1]
df_test_targets  = df["label"][split_2:] 

print( df_train_features.shape, df_train_targets.shape )
print( df_test_features.shape, df_test_targets.shape )

# COMMAND ----------

# collect models 
models   = []
models.append( ('LR', LogisticRegression(C=1e09)) )
models.append( ('LR_L1', LogisticRegression(penalty='l1',solver='liblinear')) )
models.append( ('LR_L2', LogisticRegression(penalty='l2')) )
#linear discriminant analysis is a linear classification ML algo
models.append( ('LDA', LinearDiscriminantAnalysis()) )
#KNeighborsClassifier() is for K nearest neighbor; by default looks for the 5 nearest neighbors
models.append( ('KNN', KNeighborsClassifier()) )
#GradientBoostingClassifier() is an additive model in a forward stage-wise fashion; it allows for the optimization of arbitrary differentiable loss functions
models.append( ('GB', GradientBoostingClassifier()) )
#adaBoostClassifier() combines multiple classifiers in order to increase the accuracy of classifiers
models.append( ('ABC', AdaBoostClassifier()) )
models.append( ('RF', RandomForestClassifier()) )
models.append( ('XGB', xgb.XGBClassifier()) )

# COMMAND ----------

seed     = 8
scoring  = "roc_auc" 
n_splits = 6
kfold    = model_selection.TimeSeriesSplit(n_splits=n_splits)

# COMMAND ----------

cv_res = []
names  = []

fig, ax = plt.subplots(1,2,figsize=(20,12))
#print("        CV mean CV std")

for name, model in models:
    # train current model
    model.fit(df_train_features, df_train_targets)
    #predict_proba() returns an array of lists containing the class probabilities
    #for the input data points
    y_score = model.predict_proba(df_train_features)[:,1]

    # compute roc curve
    #roc_curve() is used to evaluate binary class classification specific metrics
    fpr, tpr, thresholds = roc_curve(df_train_targets, y_score)
    
    # roc_auc_curve() computes the area under the ROC curve
    auc = roc_auc_score(df_train_targets, y_score)
    
    # cross-; returns a list of scores calculated for each fold of cross-validation
    cv_results = model_selection.cross_val_score(estimator=model, cv=kfold, scoring=scoring,
                                                 X = df_train_features, 
                                                 y = LabelBinarizer().fit_transform(df_train_targets)) 

    ax[0].plot(fpr, tpr, label="{} ROC (AUC={:.4f})".format(name,auc) )
    #print( "{}:\t{:.4f}\t({:.4f})".format(name,cv_results.mean(),cv_results.std()))

    cv_res.append(cv_results)
    names.append(name)
    
ax[0].plot([0, 1], [0, 1], color="gray", linestyle="--")
ax[0].set_xlim([-0.05, 1.0])
ax[0].set_ylim([0.0, 1.05])
ax[0].set_xlabel('false positive rate')
ax[0].set_ylabel('true positive rate')
ax[0].set_title('Receiver Operating Characteristic (ROC)')
ax[0].legend()
ax[0].grid()

ax[1].plot(cv_res)
#ax[1].set_xticklabels(names)
ax[1].set_title('algorithm comparison based on Cross Validation Scores')
ax[1].grid()

plt.show()

# COMMAND ----------

# dates of normal and recession regimes
df_targets = pd.Series(df_targets, index=df_features.index)
normal_dates     = df_targets[df_targets==0.0].index
recessions_dates = df_targets[df_targets==1.0].index

# find indices of recession regimes 
rec_idx = np.zeros_like(recessions_dates)
rec_idx[0] = 1
for i, date in enumerate(recessions_dates):
    prev_date = date - 1
    if prev_date not in recessions_dates:
        rec_idx[i] = 1
        rec_idx[i-1] = 1
rec_idx = np.array([False if i==0 else True for i in rec_idx])
#recessions_dates[rec_idx]

# index of starting recession periods
x1 = np.array( recessions_dates[rec_idx] )[:-1:2]
# index of ending recession periods
x2 = np.array( recessions_dates[rec_idx] )[1::2]

# COMMAND ----------

fig, ax = plt.subplots(len(models),1,figsize=(25,30))

for i,model in enumerate(models):
    model_fit = model[1].fit(df_train_features, df_train_targets)

    # prediction on the train set
    train_preds = pd.Series( model_fit.predict(df_train_features), index=df_train_targets.index, name="preds")
    # classes probabilities train set
    train_prob_preds = pd.DataFrame( model_fit.predict_proba(df_train_features), index=df_train_targets.index, columns=["Normal","Recession"])
    train_preds = pd.concat([train_preds, train_prob_preds], axis=1)

    # prediction on the test set
    test_preds = pd.Series( model_fit.predict(df_test_features), index=df_test_targets.index, name="preds")
    # classes probabilities test set
    test_prob_preds = pd.DataFrame( model_fit.predict_proba(df_test_features), index=df_test_targets.index, columns=["Normal","Recession"])
    test_preds  = pd.concat([test_preds, test_prob_preds], axis=1)

    # concat train and test prediction
    total_preds = pd.concat([train_preds,test_preds], axis=0)
    
    # plot
    total_preds["preds"].plot(ax=ax[i], grid=True)
    ax[i].axvspan(x1[0], x2[0], alpha=0.5, color='gray', label="recession")
    for j in range(1,len(x1)):
        ax[i].axvspan(x1[j], x2[j], alpha=0.2, color='gray')
    #ax.axvline(x=300, linestyle="--", color="r")
    ax[i].set_title("Regime prediction using {}".format(model[0]))
    ax[i].legend()
    ax[i].set_yticks([0,0.5,1]) #labels(names)

plt.show()
