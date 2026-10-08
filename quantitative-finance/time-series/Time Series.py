# Databricks notebook source
#visualize & analyze the top 5 highest valued tech stocks as of the end of 1st half of 2019 (Jan-June): MSFT,AMZN,AAPL,GOOG,FB
import pandas as pd
import numpy as np

# COMMAND ----------

pip install pandas-datareader

# COMMAND ----------

import pandas_datareader as web
import matplotlib as plt

# COMMAND ----------

#Define the stocks
symbols = ['MSFT', 'AMZN', 'AAPL', 'GOOG', 'FB']

#Creating Dates
start_date = '2019-01-01'
end_date = '2019-07-1'

#Retreiving data
#get_data_yahoo() retrieves stock data from yahoo
stock_data = web.get_data_yahoo(symbols, start_date, end_date)

#viewing the data
stock_data

# COMMAND ----------

#View Adj Close df
stock_data['Adj Close']

# COMMAND ----------

#Plot the adjusted closing prices over time
adj_date = stock_data["Adj Close"]
adj_date.plot()
plt.title("Tech Stocks Adjusted Price")
plt.xlabel("Date")
plt.ylabel("Adjusted Closing Price Over Time")
plt.show()

# COMMAND ----------

#Calculate & plot the daily simple rate of return over time
daily_return = adj_date.pct_change()

daily_return.plot()
plt.title("Daily Simple Rate of Return")
plt.xlabel("Date")
plt.ylabel("Rate of Return")
plt.show()

# COMMAND ----------

#Create subplots of daily simple rate of return
fig = plt.figure(figsize=(20,10))

#Microsoft
ax1 = plt.subplot(2,3,1)
plt.plot(daily_return['MSFT'], color='green')
plt.title('Microsoft')
plt.xlabel('Date')
plt.ylabel('Daily Return')

#Amazon
ax2 = plt.subplot(2, 3, 2)
plt.plot(daily_return['AMZN'], color='green')
plt.title('Amazon')
plt.xlabel('Date')


#Apple
ax3 = plt.subplot(2, 3, 3)
plt.plot(daily_return['AAPL'], color='green')
plt.title('Apple')
plt.xlabel('Date')


#Google
ax4 = plt.subplot(2, 3, 4)
plt.plot(daily_return['GOOG'], color='green')
plt.title('Google')
plt.xlabel('Date')
plt.ylabel('Daily Return')

#Facebook
ax5 = plt.subplot(2, 3, 5)
plt.plot(daily_return['FB'], color='green')
plt.title('Facebook')
plt.xlabel('Date')

#subplots_adjust specifies the spacing along the height & width of the figure in units of the subplot size
plt.subplots_adjust(wspace=0.3, bottom=0.1)

plt.show()

# COMMAND ----------

#Calculate & plot the mean of each tech stock's daily simple rate of return. 1. calculating the mean rate of return

mean_daily_return = daily_return.mean()
print(mean_daily_return)

# COMMAND ----------

#Plotting bar chart
ax7 = plt.subplot()
ax7.set_xticks(range(len(symbol)))
ax7.set_xticklabels(symbols)

plt.bar(range(len(symbols)), mean_daily_return, color = 'green')

plt.xlabel('Stocks')
plt.ylabel('Mean Daily')
plt.title('Mean Rate of Return x Stocks')

plt.show()

# COMMAND ----------

# Based only on the rate of the mean daily rate of return of stocks, the Facebook stock has the highest mean return rate. 
#Therefore, it is the best option to invest.
#Calculating the variance
variance_daily_return = daily_return.var()
print(variance_daily_return)

# COMMAND ----------

#Plotting bar chart
ax8 = plt.subplot()
ax8.set_xticks(range(len(symbols)))
ax8.set_xticklabels(symbols)

plt.bar(range(len(symbols)), variance_daily_return, color = 'green')

plt.xlabel('Stocks')
plt.ylabel('Variance')
plt.title('Variance x Stocks')

plt.show()
#Analyzing the variance

#Considering the stocks are being analyzed individually, Facebook is the riskiest one  due to its highest variance.

# COMMAND ----------

#Calculate & plot the standard deviation
sd_daily_return = daily_return.std()
print(sd_daily_return)

# COMMAND ----------

#Plotting bar chart
ax9 = plt.subplot()
ax9.set_xticks(range(len(symbols)))
ax9.set_xticklabels(symbols)

plt.bar(range(len(symbols)), sd_daily_return, color = 'green')

plt.xlabel('Stocks')
plt.ylabel('Standard Deviation')
plt.title('Standard Deviation x Stocks')

plt.show()
#Analyzing the Standard Deviation

#I would choose a stock to invest according to my investor profile. If I'd rather take more risk, I would invest in Facebook stocks.
# because it brings more return.
#On the other hand, if I was risk-averse, I would invest in Microsoft stocks because brings a good return with less risk.
