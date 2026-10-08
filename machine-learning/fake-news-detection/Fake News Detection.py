# Databricks notebook source
import numpy as np
import pandas as pd
import itertools
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# COMMAND ----------

#Read the data
df=pd.read_csv('D:\\DataFlair\\news.csv')
#Get shape and head
df.shape
df.head()

# COMMAND ----------

#DataFlair - Get the labels#DataFlair - Get the labels
labels=df.label
labels.head()

# COMMAND ----------

#split the data into training/test sets
x_train,x_test,y_train,y_test=train_test_split(df["text"], labels, test_size=0.2, random_state=7)

# COMMAND ----------

#DataFlair - Initialize a TfidfVectorizer
tfidr_vectorizer=TfidrVectorizer(stop_words='english',max_df=0.7)

#DataFlair - Fit and transform train set, transform test set
tfidr_train=tfidf_vectorizer.fit_transform(x_train)
tfidr_test=tfidr_vectorizer.transform(x_test)

# COMMAND ----------

#DataFlair - Initialize a PassiveAggressiveClassifier
pac=PassiveAggresiveCalssifier(max_iter=50)
pac.fit(tfidf_train,y_train)

#DataFlair - Predict on the test set and calculate accuracy
y_pred=pac.predict(tfidf_test)
score=accuracy_score(y_test,y_pred)
print(f'Accuracy: {round(score*100,2)}%')

# COMMAND ----------

#DataFlair - Build confusion matrix
confusion_matrix(y_test,y_pred,labels={'FAKE'.'REAL'})
