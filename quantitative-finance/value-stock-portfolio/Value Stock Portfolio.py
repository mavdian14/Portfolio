# Databricks notebook source
import datetime as dt 
import pandas as pd
import concurrent.futures as cf
from yahoofinancials import YahooFinancials
import yfinance as yf
import re
import ast
import time
import requests

# COMMAND ----------

pip install lxml

# COMMAND ----------

!pip install yahoofinancials
!pip install yfinance

# COMMAND ----------

df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
df

# COMMAND ----------

tickers = df.Symbol.to_list()
tickers

# COMMAND ----------

balanceSheet = {}
incomeStatement = {}
cashStatement = {}

def retrieve_stock_data(stock):
    try:
        print(stock)
        yahoo_financials = YahooFinancials(stock)
         #get_financial_stmts() used to retrieve financial statements of a company
        balance_sheet_data = yahoo_financials.get_financial_stmts('annual', 'balance')
        income_statement_data = yahoo_financials.get_financial_stmts('annual', 'income')
        cash_statement_data = yahoo_financials.get_financial_stmts('annual', 'cash')

        balanceSheet[stock] = balance_sheet_data['balanceSheetHistory'][stock]
        incomeStatement[stock] = income_statement_data['incomeStatementHistory'][stock]
        cashStatement[stock] = cash_statement_data['cashflowStatementHistory'][stock]
    except:
        print('error with retrieving stock data')

# COMMAND ----------

start = time.time()
#ThreadPoolExecutor() allows you to create & manage thread pools
executor = cf.ThreadPoolExecutor(16)
futures = [executor.submit(retrieve_stock_data, stock) for stock in tickers]
cf.wait(futures)
end = time.time()
print('  time taken {:.2f} s'.format(end-start))

# COMMAND ----------

roe_dict, epsg_dict = {}, {}
count_missing, count_cond, count_eps_0 = 0, 0, 0
for (keyB, valB), (keyI, valI) in zip(balanceSheet.items(), incomeStatement.items()):
    try:
        if keyB == keyI:
            yearsI = [k for year in valI for k, v in year.items()]
            yearsB = [k for year in valB for k, v in year.items()]
            if yearsI == yearsB:
                count_cond += 1
                equity = [v['totalStockholderEquity'] for year in valB for k, v in year.items()]
                commonStock = [v['commonStock'] for year in valB for k, v in year.items()]

                profit = [v['grossProfit'] for year in valI for k, v in year.items()]
                revenue = [v['totalRevenue'] for year in valI for k, v in year.items()]
                netIncome = [v['netIncome'] for year in valI for k, v in year.items()]

                roe = [round(netin/equity*100,2) for netin, equity in zip(netIncome, equity)]
                roe_dict[keyB] = (round(sum(roe)/len(roe),2), roe)

                eps = [round(earn/stono,2) for earn, stono in zip(profit, commonStock)]
                
                try:
                    epsg = []
                    for ep in range(len(eps)):
                        if ep == 0:
                            continue
                        elif ep == 1:
                            epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                        elif ep == 2:
                            epsg.append(round(100*((eps[ep-2]/eps[ep])**(1/2)-1),2))
                            epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                        elif ep == 3:
                            epsg.append(round(100*((eps[ep-3]/eps[ep])**(1/3)-1),2))
                            epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                        else:
                            print('More than 4 years of FY data')
                        
                    epsg_dict[keyB] = (round(sum(epsg)/len(epsg),2), epsg)
                except:
#                     print(keyB, 'eps contains 0')
                    count_eps_0 += 1
                    epsg_dict[keyB] = (0, eps)

    except:
#         print(keyB, 'data missing')
        count_missing += 1

print('Yearly data avail',count_cond, 'out of', len(balanceSheet))
print('Some key data missing', count_missing, 'out of', len(balanceSheet))
print('EPS Growth NaN', count_eps_0, 'out of', len(balanceSheet))

# COMMAND ----------

#Intrinsic Value & Value Investing
ROE_req = 10
EPSG_req = 10
print('-'*50, 'RETURN ON EQUITY','-'*50)
roe_crit = {k:v for (k,v) in roe_dict.items() if v[0] >= ROE_req and sum(n < 0 for n in v[1])==0}
# print(roe_crit)
print('-'*50, 'EARNINGS PER SHARE GROWTH','-'*50)
eps_crit = {k:v for (k,v) in epsg_dict.items() if v[0] >= EPSG_req and sum(n < 0 for n in v[1])==0}
# print(eps_crit)
print('-'*50, 'ROE & EPS Growth Critera','-'*50)
both = [key1 for key1 in roe_crit.keys() for key2 in eps_crit.keys() if key2==key1]
print(both)

# COMMAND ----------

# Importing Library necessary for the project
import numpy as np
from pylab import plt, mpl
plt.style.use('seaborn')
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['figure.figsize'] = [16, 10]
np.set_printoptions(precision=5, suppress=True,formatter={'float': lambda x: f'{x:6.3f}'})
import yfinance as yf
import scipy.optimize as sco

# COMMAND ----------

start = "2015-01-01"
end = "2022-07-08"
val_tickers = both
stocks_df = pd.DataFrame()
for stock_name in val_tickers:
    # daily data
    stocks_df[stock_name] = yf.download(stock_name,start,end)['Adj Close']  
    
stocks_df = round(stocks_df,2)

# COMMAND ----------

returns = stocks_df.pct_change().dropna()
N_DAYS = 252    # number of trading dates in a years
tot_return  = returns.mean() * N_DAYS
cov_mat = returns.cov() * N_DAYS
n_assets = len(val_tickers)

# COMMAND ----------

# Create effecient frontier using monte carlo simulation
N_PORTFOLIOS = 10 ** 5
n_assets = len(val_tickers)
#Simulate random portfolio weights:
np.random.seed(42)
weights = np.random.random(size=(N_PORTFOLIOS, n_assets))
weights /=  np.sum(weights, axis=1)[:, np.newaxis]

# COMMAND ----------

#Calculate the portfolio metrics:
portf_rtns = np.dot(weights, tot_return)

portf_vol = []
for i in range(0, len(weights)):
    portf_vol.append(np.sqrt(np.dot(weights[i].T, np.dot(cov_mat, weights[i]))))
portf_vol = np.array(portf_vol)  
portf_sharpe_ratio = portf_rtns / portf_vol

# COMMAND ----------

portf_results_df = pd.DataFrame({'returns': portf_rtns, 'volatility': portf_vol,'sharpe_ratio': portf_sharpe_ratio})
portf_results_df

# COMMAND ----------

# find the portfolio with lowest volatility 
low_vol_portfolio = portf_results_df.iloc[ portf_results_df['volatility'].idxmin() ]
print("Global Minimum Volatility portfolio:")
print("- return      : {:.2f}%".format(low_vol_portfolio[0]*100) )
print("- volatility  : {:.2f}%".format(low_vol_portfolio[1]*100) )
print("- sharpe ratio: {:.2f}".format(low_vol_portfolio[2]) )

# find the portfolio with highest sharpe ratio
high_sharpe_portfolio = portf_results_df.iloc[ portf_results_df['sharpe_ratio'].idxmax() ]
print("Maximum Sharpe Ratio portfolio:")
print("- return      : {:.2f}%".format(high_sharpe_portfolio[0]*100) )
print("- volatility  : {:.2f}%".format(high_sharpe_portfolio[1]*100) )
print("- sharpe ratio: {:.2f}".format(high_sharpe_portfolio[2]) )

# COMMAND ----------

#Plotting the results of monte carlo simulation
fig, ax = plt.subplots(1,1, figsize=(20,12)) 
fig = plt.scatter(portf_results_df['volatility'], portf_results_df['returns'],
c=portf_results_df['sharpe_ratio'], cmap='coolwarm')
cb = plt.colorbar(fig)
cb.set_label('Sharpe ratio')
ax.scatter(low_vol_portfolio[1],     low_vol_portfolio[0],     marker="X", color='g', s=120, label="GMV portfolio")
ax.scatter(high_sharpe_portfolio[1], high_sharpe_portfolio[0], marker="X", color='b', s=120, label="MSR portfolio")
ax.set_title("Portfolios and efficient frontier")
ax.set_xlabel("volatility")
ax.set_ylabel("returns")
ax.legend()
#plt.xlabel('expected volatility')
#plt.ylabel('expected return')
#plt.title('Effiecient Frontier using Monte Carlo Simulation');

# COMMAND ----------

#Define functions calculating portfolio returns and volatility:
def neg_sharpe_ratio(w, avg_rtns, cov_mat, rf_rate):
    portf_returns = np.sum(avg_rtns * w)
    portf_volatility = np.sqrt(np.dot(w.T, np.dot(cov_mat, w)))
    portf_sharpe_ratio = (portf_returns - rf_rate) / portf_volatility
    return -portf_sharpe_ratio

def port_vol(w, avg_rtns, cov_mat):
    portf_returns = np.sum(avg_rtns * w)
    portf_volatility = np.sqrt(np.dot(w.T, np.dot(cov_mat, w)))
    return portf_volatility 

def get_portf_rtn(w, avg_rtns):
    return np.sum(avg_rtns * w)

# COMMAND ----------

RF_RATE = 0

args = (tot_return, cov_mat, RF_RATE)
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
bounds = tuple((0,1) for asset in range(n_assets))
initial_guess = n_assets * [1. / n_assets]

max_sharpe_portf_opt = sco.minimize(neg_sharpe_ratio, x0=initial_guess, args=args, method='SLSQP', bounds=bounds, constraints=constraints)

# COMMAND ----------

max_sharpe_portf_w = max_sharpe_portf_opt['x']
print("Global Maximum Sharpe Ratio portfolio:")
max_sharpe_portf = {'Return': get_portf_rtn(max_sharpe_portf_w, tot_return), 'Volatility': port_vol(max_sharpe_portf_w, tot_return, cov_mat), 'Sharpe Ratio': -max_sharpe_portf_opt['fun']}
max_sharpe_portf

# COMMAND ----------

spy = yf.download('^GSPC','2019-03-14',end)['Adj Close']  
spy_ret =  spy.pct_change().dropna()
tot_spy = (spy_ret+1).cumprod()

# COMMAND ----------

ret_msr = (returns*max_sharpe_portf_w).sum(axis='columns')
total_ret_msr = (ret_msr+1).cumprod()

# COMMAND ----------

plt.plot(total_ret_msr, label='Max Sharpe Ratio Weighted Value Portfolio')
plt.plot(tot_spy, label='S&P500 net return')
plt.xlabel('Date')
plt.ylabel('Total Return')
plt.legend(loc="upper left")
