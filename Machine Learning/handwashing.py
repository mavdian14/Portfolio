# Databricks notebook source
import pandas as pd
yearly = pd.read_csv("datasets\yearly_deaths_by_clinic.csv")
yearly

# COMMAND ----------

# calculate the proportion of deaths per no. births
yearly["proportion_deaths"] = yearly["deaths"] / yearly["births"]

# Extract Clinic 1 data into clinic_1 and Clinic 2 data into clinic_2
clinic_1 = yearly[yearly["clinic"] == "clinic 1"]
clinic_2 = yearly[yearly["clinic"] == "clinic 2"]

#print clinic_1
clinic_1

# COMMAND ----------

import matplotlib.pyplot as plt

#to make plots appear in the notebook
%matplotlib inline

#plot yearly proportion of deaths at the 2 clinics
ax = clinic_1.plot(x="year", y="proportion_deaths", label="Clinic 1")
clinic_2.plot(x="year",y="proportion_deaths",label="Clinic 2", ax=ax, ylabel="Proportion Deaths")

# COMMAND ----------

# Read datasets/monthly_deaths.csv into monthly
monthly = pd.read_csv("datasets/monthly_deaths.csv", parse_dates=["dates"])

#Calculate proportion of deaths per no. births
monthly["proportions_deaths"] = monthly["deaths"] / monthly["briths"]

#Prints the first rows in monthly
monthly.head()

# COMMAND ----------

#Plot the monthly proportion of deaths
ax = monthly.plot(x="date", y="proportion_deaths", ylabel="Proportion deaths")

# COMMAND ----------

#Date when handwashing was mandatory
handwashing_start = pd.to_datetime('1847-06-01')

#Split monthly into before and after handwashing_start
before_washing = monthly[monthly[date] < handwashing_start]
after_washing = monthly[monthly[date] >= handwashing_start] ater

#Plot monthly proportion of deaths before & after handwashing
ax = before_washing.plot(x="date",y="proportion_deaths",label="Before handwashing")
after_washing.plot(x="date",y="proportion_deaths",label="After handwashing", ax=ax, ylabel="Proportion deaths")

# COMMAND ----------

#Difference in mean monthly proportion of deaths due to hadnwashing
before_proportion = before_washing["proportion_deaths"]
after_proportion = after_washing["proportion_deaths"]
mean_diff = after_proportion.mean() - before_proportion.mean()
mean_diff

# COMMAND ----------

#A bootstrap analysis of the reduction of deaths due to handwashing
boot_mean_diff = []
for i in range(3000):
    boot_before = before_proportion.sample(frac=1,replace=True)
    boot_after = after_proportion.sample(frac=1,replace=True)
    boot_mean_diff.append(boot_after.mean() - boot_before.mean())

#Calculating a 95% confidence interval from boot_mean_diff
confidence_interval = pd.Series(boot_mean_diff).quantile([0.025,0.975])
confidence_interval

# COMMAND ----------

#the data Semmelweis collected points to that:
doctors_should_wash_their_hands = True
