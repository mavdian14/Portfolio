# Databricks notebook source
#necessary imports
import numpy as np
import pandas as pd
import os, sys
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# COMMAND ----------

#DataFlair - Read the data
df=pd.read_csv('D:\\DataFlair\\parkinsons.data')
df.head()

# COMMAND ----------

#DataFlair - Get the features and labels
features=df.loc[:,df.columns!='status'].values[:,1:]
labels=df.loc[:,'status'].values

# COMMAND ----------

#DataFlair - Get the count of each label (0 and 1) in labels
print(labels[labels==1].shape[0], labels[labels==0].shape[0])

# COMMAND ----------

#DataFlair - Scale the features to between -1 and 1
scaler=MinMaxScaler((-1,1))
x=scaler.fit_transform(features)
y=labels

# COMMAND ----------

#DataFlair - Split the dataset
x_train,x_test,y_train,y_test=train_test_split(x, y, test_size=0.2, random_state=7)

# COMMAND ----------

#DataFlair - Train the model
model=XGBClassifier()
model.fit(x_train,y_train)

# COMMAND ----------

# DataFlair - Calculate the accuracy
y_pred=model.predict(x_test)
print(accuracy_score(y_test, y_pred)*100)

# COMMAND ----------


