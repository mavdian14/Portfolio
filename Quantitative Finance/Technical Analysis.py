# Databricks notebook source
!pip install yfinance

# COMMAND ----------

#Loading essential library for this project
import numpy as np
import pandas as pd
import datetime as dt
from pylab import mpl, plt
import yfinance as yf
plt.style.use('seaborn')
mpl.rcParams['font.family'] = 'serif'
%matplotlib inline

# COMMAND ----------

# I want to analyse Tesla as it has a cult following thus testing technical features to trade
data = yf.download('TSLA')
data

# COMMAND ----------

#Lets define the short and long period for coming simple moving average
SMA1 = 42
SMA2 = 252
data['SMA1'] = data['Adj Close'].rolling(SMA1).mean()
data['SMA2'] = data['Adj Close'].rolling(SMA2).mean()

# COMMAND ----------

#Lets visualise the price and SMA
plt.figure(figsize=(16, 10))
plt.plot(data['Adj Close'],label = 'Adj. Close')
plt.plot(data['SMA1'],label = 'Simple Moving Average 42 days')
plt.plot(data['SMA2'],label = 'Simple Moving Average 252 days')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.title('Tesla Price Movements');

# COMMAND ----------

data.dropna(inplace=True)
data['Position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1) #condition to go long or short
mask = data[['Adj Close','SMA1','SMA2','Position']]
mask

# COMMAND ----------

ax = mask.plot(secondary_y='Position', figsize=(16, 10))
#set_bbox_to_anchor() will create a bounding box on the axes, inside which the actual legend will be placed
ax.get_legend().set_bbox_to_anchor((0.25, 0.85));

# COMMAND ----------

#Vectorized Backtesting
#np.log() computes the natural log of input array's elements
mask['Returns'] = np.log(mask['Adj Close'] / mask['Adj Close'].shift(1))
mask['Strategy'] = mask['Position'].shift(1) * mask['Returns']
mask

# COMMAND ----------

mask.dropna(inplace=True)
np.exp(mask[['Returns', 'Strategy']].sum())
mask[['Returns', 'Strategy']].std() * 252 ** 0.5

# COMMAND ----------

ax = mask[['Returns', 'Strategy']].cumsum().apply(np.exp).plot(figsize=(16, 10))
mask['Position'].plot(ax=ax, secondary_y='Position', style='--')
ax.get_legend().set_bbox_to_anchor((0.25, 0.85));

# COMMAND ----------

from itertools import product
data = yf.download('TSLA')
sma1 = range(20, 61, 4)
sma2 = range(180, 281, 10)

# COMMAND ----------

results = pd.DataFrame()
for SMA1, SMA2 in product(sma1, sma2):
    data = pd.DataFrame(raw['Adj Close'])
    data.dropna(inplace=True)
    data['Returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
    data['SMA1'] = data['Adj Close'].rolling(SMA1).mean()
    data['SMA2'] = data['Adj Close'].rolling(SMA2).mean()
    data.dropna(inplace=True)
    data['Position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1)
    data['Strategy'] = data['Position'].shift(1) * data['Returns']
    data.dropna(inplace=True)
    perf = np.exp(data[['Returns', 'Strategy']].sum())
    results = results.append(pd.DataFrame(
                            {'SMA1': SMA1, 'SMA2': SMA2,
                            'MARKET': perf['Returns'],
                            'STRATEGY': perf['Strategy'],
                            'OUT': perf['Strategy'] - perf['Returns']},
                            index=[0]), ignore_index=True)

# COMMAND ----------

results.sort_values('OUT', ascending=False).head(7)

# COMMAND ----------

#Exponential Moving Average
data = yf.download('TSLA')
ema1 = range(20, 61, 4)
ema2 = range(180, 281, 10)

# COMMAND ----------

results = pd.DataFrame()
for EMA1, EMA2 in product(ema1, ema2):
    data = pd.DataFrame(raw['Adj Close'])
    data.dropna(inplace=True)
    data['Returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
    #.ewm() provides exponential weighted functions
    data['EMA1'] = data['Adj Close'].ewm(span=EMA1, adjust=False).mean()
    data['EMA2'] = data['Adj Close'].ewm(span=EMA2, adjust=False).mean()
    data.dropna(inplace=True)
    data['Position'] = np.where(data['EMA1'] > data['EMA2'], 1, -1)
    data['Strategy'] = data['Position'].shift(1) * data['Returns']
    data.dropna(inplace=True)
    perf = np.exp(data[['Returns', 'Strategy']].sum())
    results = results.append(pd.DataFrame(
                            {'EMA1': EMA1, 'EMA2': EMA2,
                            'MARKET': perf['Returns'],
                            'STRATEGY': perf['Strategy'],
                            'OUT': perf['Strategy'] - perf['Returns']},
                            index=[0]), ignore_index=True)

# COMMAND ----------

data

# COMMAND ----------

ax = data[['Returns', 'Strategy']].cumsum().apply(np.exp).plot(figsize=(16, 10))
data['Position'].plot(ax=ax, secondary_y='Position', style='--')
ax.get_legend().set_bbox_to_anchor((0.25, 0.85));

# COMMAND ----------

data = yf.download('TSLA')
data

# COMMAND ----------

#RSI Strategy
def RSI(series, period):
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
    d = d.drop(d.index[:(period-1)])
    rs = pd.DataFrame.ewm(u, com=period-1, adjust=False).mean() / \
         pd.DataFrame.ewm(d, com=period-1, adjust=False).mean()
    return 100 - 100 / (1 + rs)

# COMMAND ----------

def get_rsi(price):
    """
    Args:
        price (pd.DataFrame)  : pd.DataFrame include stock_price
        code (int)  : A local code for a listed company
    Returns:
        feature DataFrame (pd.DataFrame)
    """
    df = price.copy()
    df['Returns'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
    period = 14
    df[f"RSI_{period}days"] = RSI(df['Adj Close'], period)
    
    return df

data = get_rsi(data)
data = data.dropna()
data

# COMMAND ----------

plt.figure(figsize=(16, 10))
plt.plot(data['RSI_14days'],label = '14 days Relative Strenth Index')
plt.plot((data['Volume']/data['Volume'].mean())*10,label = 'Normalized Volume Scaled by 10')
plt.xlabel('Date')
plt.ylabel('RSI !4 days')
plt.legend()
plt.title('RSI 14 day movement vs Volume');

# COMMAND ----------

plt.figure(figsize=(16, 10))
ax1 = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
ax2 = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
ax1.plot(data['Adj Close'], linewidth = 2.5)
ax1.set_title('TESLA CLOSE PRICE')
ax2.plot(data['RSI_14days'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.set_title('TESLA RELATIVE STRENGTH INDEX')
plt.show()

# COMMAND ----------

def implement_rsi_strategy(prices, rsi):    
    buy_price = []
    sell_price = []
    rsi_signal = []
    signal = 0

    for i in range(len(rsi)):
        if rsi[i-1] > 30 and rsi[i] < 30:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                rsi_signal.append(0)
        elif rsi[i-1] < 70 and rsi[i] > 70:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            rsi_signal.append(0)
            
    return buy_price, sell_price, rsi_signal

# COMMAND ----------

buy_price, sell_price, rsi_signal = implement_rsi_strategy(data['Adj Close'], data['RSI_14days'])

# COMMAND ----------

plt.figure(figsize=(16, 10))
ax1 = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
ax2 = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
ax1.plot(data['Adj Close'], linewidth = 2.5, color = 'skyblue', label = 'IBM')
ax1.plot(data.index, buy_price, marker = '^', markersize = 10, color = 'green', label = 'BUY SIGNAL')
ax1.plot(data.index, sell_price, marker = 'v', markersize = 10, color = 'r', label = 'SELL SIGNAL')
ax1.set_title('TESLA RSI TRADE SIGNALS')
ax2.plot(data['RSI_14days'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
plt.show()

# COMMAND ----------

position = []
for i in range(len(rsi_signal)):
    if rsi_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)
        
for i in range(len(data['Adj Close'])):
    if rsi_signal[i] == 1:
        position[i] = 1
    elif rsi_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]

# COMMAND ----------

data['Position'] = position
data

# COMMAND ----------

data['Strategy'] = data['Position'].shift(1) * data['Returns']
data

# COMMAND ----------

data.dropna(inplace=True)
np.exp(data[['Returns', 'Strategy']].sum())
data[['Returns', 'Strategy']].std() * 252 ** 0.5

# COMMAND ----------

ax = data[['Returns', 'Strategy']].cumsum().apply(np.exp).plot(figsize=(16, 10))
data['Position'].plot(ax=ax, secondary_y='Position', style='--')
ax.get_legend().set_bbox_to_anchor((0.25, 0.85));

# COMMAND ----------

#Momentum Strategy
data = yf.download('TSLA')
data

# COMMAND ----------

data['returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
#np.sign() returns an element-wise indication of the sign of a number
data['position'] = np.sign(data['returns'])
data['strategy'] = data['position'].shift(1) * data['returns']
to_plot = ['returns']

# COMMAND ----------

data[to_plot].dropna().cumsum().apply(np.exp).plot(title='TESLA Momentum Strategy returns', figsize=(16, 10), style=['-', '--', '--', '--', '--', '--']);
