# Databricks notebook source
import pandas as pd
import numpy as np
import seaborn as sns #visualisation
import matplotlib.pyplot as plt #visualisation
%matplotlib inline 
sns.set(color_codes=True)

# COMMAND ----------

df = pd.read_csv("data.csv")
#To display the top 5 rows
df.head(5)

# COMMAND ----------

#display bottom 5 rows
df.tail(5)

# COMMAND ----------

# Checking the data type
df.dtypes

# COMMAND ----------

#Dropping irrelevant columns
df = df.drop(["Engine Fuel Type", "Market Category", "Vehicle Style", "Popularity", "Number of Doors", "Vehicle Size", axis=1])
df.head(5)

# COMMAND ----------

# Renaming the column names
df = df.rename(columns={“Engine HP”: “HP”, “Engine Cylinders”: “Cylinders”, “Transmission Type”: “Transmission”, “Driven_Wheels”: “Drive Mode”,”highway MPG”: “MPG-H”, “city mpg”: “MPG-C”, “MSRP”: “Price” })
df.head(5)

# COMMAND ----------

# Total number of rows and columns
df.shape
(11914, 10)
# Rows containing duplicate data
duplicate_rows_df = df[df.duplicated()]
print(“number of duplicate rows: “, duplicate_rows_df.shape)

# COMMAND ----------

# Dropping the duplicates 
df = df.drop_duplicates()
df.head(5)

# COMMAND ----------

# Finding the null values.
print(df.isnull().sum())
# Dropping the missing values.
df = df.dropna() 

# COMMAND ----------

#Detecting/Removing Outlier Data using IQR score technique
sns.boxplot(x=df[‘Price’])
sns.boxplot(x=df[‘HP’])
sns.boxplot(x=df['Cylinders'])
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 — Q1
print(IQR)

# COMMAND ----------

#above continued
df = df[~((df < (Q1-1.5*IQR)) | (df > (Q3 + 1.5*IQR))).any(axis=1)]
df.shape

# COMMAND ----------

# Plotting a Histogram
#value_counts() gives the count of unique values
df.Make.value_counts().nlargest(40).plot(kind=’bar’, figsize=(10,5))
plt.title(“Number of cars by make”)
plt.ylabel(‘Number of cars’)
plt.xlabel(‘Make’);

# COMMAND ----------

# Finding the relations between the variables using heat maps
plt.figure(figsize=(20,10))
c= df.corr()
sns.heatmap(c,cmap=”BrBG”,annot=True)
c

# COMMAND ----------

# Plotting a scatter plot btwn Horsepower & Price
fig, ax = plt.subplots(figsize=(10,6))
ax.scatter(df[‘HP’], df[‘Price’])
ax.set_xlabel(‘HP’)
ax.set_ylabel(‘Price’)
plt.show()
