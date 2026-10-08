# Databricks notebook source
!pip install yfinance

# COMMAND ----------

# Importing Library necessary for the project
import numpy as np
import pandas as pd
from pylab import plt, mpl
plt.style.use('seaborn')
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'serif'
np.set_printoptions(precision=5, suppress=True,formatter={'float': lambda x: f'{x:6.3f}'})
import yfinance as yf

# COMMAND ----------

df = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')[1]
df

# COMMAND ----------

tickers = df.Symbol.to_list()
tickers

# COMMAND ----------

infos = []
for tick in tickers:
    infos.append(yf.Ticker(tick).info)

infos = pd.DataFrame(infos)

# COMMAND ----------

infos = infos.set_index('symbol')
infos

# COMMAND ----------

for col in infos.columns:
    print(col)

# COMMAND ----------

fundamental = ['industry','operatingCashflow','ebitda','freeCashflow','pegRatio','earningsGrowth','currentRatio','debtToEquity','returnOnEquity','totalCash','totalDebt','quickRatio','beta3Year','beta','forwardEps','priceToBook','priceToSalesTrailing12Months','forwardPE','dividendRate','trailingPE','marketCap','dividendYield']
#lets filter out the fundamental data 
fund_info = infos[infos.columns[infos.columns.isin(fundamental)]]
fund_info

# COMMAND ----------

#First let plot out the companies with the biggest market cap
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['marketCap'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

fund_info['marketCap'].nlargest(10)

# COMMAND ----------

##First let plot out the companies with the biggest ebita
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['ebitda'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

##First let plot out the companies with the biggest pegratio
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['pegRatio'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

##First let plot out the companies with the biggest debt to equity ratio
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['debtToEquity'])
plt.xticks(rotation = 90)
plt.show()


# COMMAND ----------

##First let plot out the companies with the biggest price to book ratio
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['priceToBook'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

##First let plot out the companies with the biggest price to book ratio
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['freeCashflow'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

##First let plot out the companies with the biggest price to book ratio
plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['beta'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

plt.figure(figsize=(16,10))
plt.bar(fund_info.index,fund_info['forwardPE'])
plt.xticks(rotation = 90)
plt.show()

# COMMAND ----------

!pip install yahoo_fin

# COMMAND ----------

import yahoo_fin.stock_info as yfi
import time

# COMMAND ----------

balance_sheet = []
income_statement = []
cfs = []
years = []
profitability_score = 0
leverage_score = 0
operating_efficiency_score = 0
pe_ratio = 0

# COMMAND ----------

summary = pd.DataFrame(columns = ['Ticker', 'PE ratio',
                                  'Profitability', 'Leverage',
                                  'Operating eficiency'])

# COMMAND ----------

def get_data(ticker):
    global balance_sheet
    global income_statement
    global cfs
    global years
    balance_sheet = yfi.get_balance_sheet(ticker)
    income_statement = yfi.get_income_statement(ticker)
    cfs = yfi.get_cash_flow(ticker)
    years = balance_sheet.columns

def pe(ticker):
    global pe_ratio
     #get_quote_table() returns a collection of useful data on a stock ticker, a dictionary of 70 useful related metrics (company, close price,P/E,etc.)
    pe_ratio = yfi.get_quote_table(ticker)['PE Ratio (TTM)']
    if pe_ratio != pe_ratio: #Check if NaN
        pe_ratio = 0   

def profitability():
    global profitability_score
    #Scores #1 and 2 - net income
    net_income = income_statement[years[0]]['netIncome']
    net_income_py = income_statement[years[1]]['netIncome']
    ni_score = 1 if net_income > 0 else 0
    ni_score_2 = 1 if net_income > net_income_py else 0

    #Score #3 - operating cash flow
    op_cf = cfs[years[0]]['totalCashFromOperatingActivities']
    op_cf_score = 1 if op_cf > 0 else 0

    #Score #4 - change in RoA
    avg_assets = (balance_sheet[years[0]]['totalAssets']
                    + balance_sheet[years[1]]['totalAssets']) / 2
    avg_assets_py = (balance_sheet[years[1]]['totalAssets']
                    + balance_sheet[years[2]]['totalAssets']) / 2
    RoA = net_income / avg_assets
    RoA_py = net_income_py / avg_assets_py
    RoA_score = 1 if RoA > RoA_py else 0

    #Score #5 - Accruals
    total_assets = balance_sheet[years[0]]['totalAssets']
    accruals = op_cf / total_assets - RoA
    ac_score = 1 if accruals > 0 else 0

    profitability_score = ni_score + ni_score_2 + op_cf_score + RoA_score + ac_score

def leverage():
    global leverage_score
    #Score #6 - long-term debt ratio
    try:
        lt_debt = balance_sheet[years[0]]['longTermDebt']
        total_assets = balance_sheet[years[0]]['totalAssets']
        debt_ratio = lt_debt / total_assets
        debt_ratio_score = 1 if debt_ratio < 0.4 else 0
    except:
        debt_ratio_score = 1

    #Score #7 - Current ratio
    current_assets = balance_sheet[years[0]]['totalCurrentAssets']
    current_liab = balance_sheet[years[0]]['totalCurrentLiabilities']
    current_ratio = current_assets / current_liab
    current_ratio_score = 1 if current_ratio > 1 else 0

    leverage_score = debt_ratio_score + current_ratio_score

def operating_efficiency():
    global operating_efficiency_score
    #Score #8 - Gross margin
    gp = income_statement[years[0]]['grossProfit']
    gp_py = income_statement[years[1]]['grossProfit']
    revenue = income_statement[years[0]]['totalRevenue']
    revenue_py = income_statement[years[1]]['totalRevenue']
    gm = gp / revenue
    gm_py = gp_py / revenue_py
    gm_score = 1 if gm > gm_py else 0
    
    #Score #9 - Asset turnover
    avg_assets = (balance_sheet[years[0]]['totalAssets']
                    + balance_sheet[years[1]]['totalAssets']) / 2
    avg_assets_py = (balance_sheet[years[1]]['totalAssets']
                    + balance_sheet[years[2]]['totalAssets']) / 2

    at = revenue / avg_assets #at = asset turnover
    at_py = revenue_py / avg_assets_py
    at_score = 1 if at > at_py else 0

    operating_efficiency_score = gm_score + at_score
    

# COMMAND ----------

#firms with a Piotroski score of 8-9 is considered to be strong, whereas, ones with a score 0-2 is considered to be weak
for ticker in tickers:
    try:
        get_data(ticker)
        pe(ticker)
        profitability()
        leverage()
        operating_efficiency()
        new_row = {'Ticker': ticker,
                   'PE ratio': pe_ratio,
                   'Profitability': profitability_score,
                   'Leverage': leverage_score,
                   'Operating eficiency': operating_efficiency_score}

        summary = summary.append(new_row, ignore_index = True)
        print(ticker + ' added.')
        time.sleep(3)
    except:
        print(ticker + ': Something went wrong.')
summary['Total score'] = summary['Profitability'] + summary['Leverage'] + summary['Operating eficiency']
summary
