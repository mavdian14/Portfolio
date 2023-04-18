# Databricks notebook source
!pip install yfinance

# COMMAND ----------
''' cvxpy package is for convex optimization problems'''
!pip install cvxpy

# COMMAND ----------

# Importing Library necessary for the project
import numpy as np
import pandas as pd
from pylab import plt, mpl
plt.style.use('seaborn')
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['figure.figsize'] = [14, 6]
np.set_printoptions(formatter={'float': lambda x: f'{x:5.2f}'})
import yfinance as yf
import seaborn as sns

#Import scipy for linear regressions
from scipy import stats
#from pypfopt import EfficientFrontier
import cvxpy as cp

import warnings
warnings.filterwarnings("ignore")

# COMMAND ----------

start="2014-09-17"
spy_df = yf.download('^GSPC',start)
btc_df = yf.download('BTC-USD',start)
gld_df = yf.download('GC=F',start)
#cpi_df = pd.read_excel('CPIAUCSL.xls') (need to download this file)
#extracted from the Fred website

# COMMAND ----------

btc_df.head()

# COMMAND ----------

gld_df.head()

# COMMAND ----------

#cpi_df.head()

# COMMAND ----------

# we can see that the we have one extra day of data compared to BTC data so let's drop that extra day
spy_df = spy_df[1:]
gld_df = gld_df[1:]

# COMMAND ----------

#lets set the index to date for CPI data and rename the date column
cpi_df.rename(columns={'observation_date':'Date'},inplace=True)
cpi_df.set_index('Date',inplace=True)
cpi_df

# COMMAND ----------

# Lets merge equity data and gold data together
merged_df1 = spy_df.merge(btc_df,on='Date',how='left').merge(gld_df,on='Date',how='left')
merged_df1

# COMMAND ----------

#lets resample the daily frequency to monthly frequency data
#.resample() summarizes the data by date/time
mnth_df = merged_df1.resample('MS').last()
mnth_df=mnth_df[:98]    #drop the last row 
mnth_df

# COMMAND ----------

#lets merge the cpi data with the above merged dataframe
final_df = mnth_df.merge(cpi_df,on='Date')
final_df

# COMMAND ----------

#Lets drop all the columns that are not adjusted closing price
final_df.drop(['Open_x','High_x','Close_x','Volume_x','Open_y','High_y','Close_y','Volume_y','Open','High','Close','Volume'],axis=1,inplace=True)
final_df.drop(['Low_x','Low_y','Low'],axis=1,inplace=True)
final_df

# COMMAND ----------

final_df.rename(columns={'Adj Close_x':'Adj Close_spy','Adj Close_y':'Adj Close_btc','Adj Close':'Adj Close_gld','CPIAUCSL':'CPI'},inplace=True)
final_df

# COMMAND ----------

#Calculate Standardised Returns 
final_df['spy_std_ret'] = final_df['Adj Close_spy']/final_df['Adj Close_spy'][0] *100
final_df['btc_std_ret'] = final_df['Adj Close_btc']/final_df['Adj Close_btc'][0] *100
final_df['gld_std_ret'] = final_df['Adj Close_gld']/final_df['Adj Close_gld'][0] *100
final_df['CPI_pct_change'] = final_df['CPI']/final_df['CPI'][0] *100
final_df

# COMMAND ----------

fig, ax = plt.subplots(1,2,figsize=(15,5))
plt.suptitle('Fig. 1: Return indices (Sep 2014 = 100)',fontweight='bold',y=1.0)
ax[0].plot(final_df['spy_std_ret'])
ax[0].plot(final_df['btc_std_ret'])
ax[0].plot(final_df['gld_std_ret'])
ax[0].set_title('Linear Scale')
ax[0].legend(['S&P 500','Bitcoin','Gold'])

ax[1].plot(final_df['spy_std_ret'])
ax[1].plot(final_df['btc_std_ret'])
ax[1].plot(final_df['gld_std_ret'])
plt.yscale('log')
ax[1].set_title('Lograthimic Scale')
ax[1].legend(['S&P 500','Bitcoin','Gold'])

# COMMAND ----------

##Calculate period performance & annualized performance
spy_return = (final_df['Adj Close_spy'][-1]/final_df['Adj Close_spy'][0])-1
spy_return_ann = (spy_return + 1) ** (1 / (len(final_df) / 12)) - 1

btc_return = (final_df['Adj Close_btc'][-1]/final_df['Adj Close_btc'][0])-1
btc_return_ann = (btc_return + 1) ** (1 / (len(final_df) / 12)) - 1

gld_return = (final_df['Adj Close_gld'][-1]/final_df['Adj Close_gld'][0])-1
gld_return_ann = (gld_return + 1) ** (1 / (len(final_df) / 12)) - 1

print("SP500 ROI : ", spy_return, "SP500 annualized returns : ", spy_return_ann)
print("Bitcoin ROI : ", btc_return, "Bitcoin annualized returns : ", btc_return_ann)
print("Gold ROI : ", gld_return, "Gold annualized returns : ", gld_return_ann)

# COMMAND ----------

fig, ax = plt.subplots(1,2,figsize=(15,5))
plt.suptitle('Fig. 2: S&P 500 and Bitcoin Daily Trading Volume',fontweight='bold',y=1.0)
ax[0].plot(merged_df1['Volume_x'])
ax[0].plot(merged_df1['Volume_y'])
ax[0].set_title('Linear Scale')
ax[0].legend(['S&P 500','Bitcoin'])

ax[1].plot(merged_df1['Volume_x'])
ax[1].plot(merged_df1['Volume_y'])
plt.yscale('log')
ax[1].set_title('Lograthimic Scale')
ax[1].legend(['S&P 500','Bitcoin'])

# COMMAND ----------

#Comparing risk & returns of all the asset class in our universe
#resample data to annual frequency

ann_df = final_df.resample('Y').last()
ann_df['spy_pct'] = ann_df['Adj Close_spy'].pct_change()
ann_df['btc_pct'] = ann_df['Adj Close_btc'].pct_change()
ann_df['gld_pct'] = ann_df['Adj Close_gld'].pct_change()
ann_df = ann_df[1:]

fig, ax = plt.subplots(figsize=(12,5))
plt.title('Fig. 3: Returns by year', pad=23, fontweight='bold')

years = ann_df.index.year
#np.arrange() is an array creation routine based on numerical ranges
x_axis = np.arange(len(years))

ax.bar(x_axis, ann_df['spy_pct'], width=0.25, label = 'S&P 500', color='teal')
ax.bar(x_axis + 0.25, ann_df['gld_pct'], width=0.25, label = 'Gold', color='gold')
ax.bar(x_axis + 0.5, ann_df['btc_pct'], width=0.25, label = 'Bitcoin', color='lightcoral')

plt.xticks(x_axis + 0.25, years)
plt.ylim([-1,2])
#ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
#ax.grid(axis='y')
ax.legend(loc='upper left')
ax.set_ylabel('Total return')
ax.set_xlabel('Year (2022 until 31 Oct)')
ax.annotate('1425%', (2.32, 2), color='maroon')
ax.annotate('303%', (5.35, 2), color='maroon')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(left=False)

plt.show()

# COMMAND ----------

#Visualizing Monthly Returns of different asset class
final_df['spy_pct']= final_df['Adj Close_spy'].pct_change()
final_df['btc_pct']=final_df['Adj Close_btc'].pct_change()
final_df['gld_pct']=final_df['Adj Close_gld'].pct_change()
final_df=final_df[1:]

final_df

# COMMAND ----------

sns.histplot(final_df['spy_pct'],kde=True, bins=15)

# COMMAND ----------

sns.histplot(final_df['btc_pct'],kde=True, bins=15)

# COMMAND ----------

sns.histplot(final_df['gld_pct'],kde=True, bins=15)

# COMMAND ----------

#Calculating Standard Deviation and Sharpe Ratio

spy_ann_sdv = final_df['spy_pct'].std()*(12**0.5)
btc_ann_sdv = final_df['btc_pct'].std()*(12**0.5)
gld_ann_sdv = final_df['gld_pct'].std()*(12**0.5)

spy_sharpe = spy_return_ann/spy_ann_sdv
btc_sharpe = btc_return_ann/btc_ann_sdv
gld_sharpe = gld_return_ann/gld_ann_sdv

#Max Drawdown
#.expanding() returns the calculated cumulative sum of a selected col in a df
spy_maxDD = min(final_df['Adj Close_spy']/final_df['Adj Close_spy'].expanding().max()-1)
btc_maxDD = min(final_df['Adj Close_btc']/final_df['Adj Close_btc'].expanding().max()-1)
gld_maxDD = min(final_df['Adj Close_gld']/final_df['Adj Close_gld'].expanding().max()-1)

spy_maxDD_daily = min(merged_df1['Adj Close_x']/merged_df1['Adj Close_x'].expanding().max()-1)
btc_maxDD_daily = min(merged_df1['Adj Close_y']/merged_df1['Adj Close_y'].expanding().max()-1)
gld_maxDD_daily = min(merged_df1['Adj Close']/merged_df1['Adj Close'].expanding().max()-1)

#Historical VAR(95%) and CVAR(5%)
spy_Var = final_df['spy_pct'].nsmallest(5)[4]
btc_Var = final_df['btc_pct'].nsmallest(5)[4]
gld_Var = final_df['gld_pct'].nsmallest(5)[4]

spy_CVar = final_df['spy_pct'].nsmallest(5).mean()
btc_CVar = final_df['btc_pct'].nsmallest(5).mean()
gld_CVar = final_df['gld_pct'].nsmallest(5).mean()

#Summary Table
table = {'Annual Return (in %)': [round(spy_return_ann*100,2),round(btc_return_ann*100,2),round(gld_return_ann*100,2)],
        'Annual Volitility (in %)':[round(spy_ann_sdv*100,2),round(btc_ann_sdv*100,2),round(gld_ann_sdv*100,2)],
        'Sharpe Ratio':[round(spy_sharpe,2),round(btc_sharpe,2),round(gld_sharpe,2)],
        'Maximum Drawdown(monthly, in %)':[round(spy_maxDD*100,2),round(btc_maxDD*100,2),round(gld_maxDD*100,2)],
        'Maximum Drawdown(daily, in %)':[round(spy_maxDD_daily*100,2),round(btc_maxDD_daily*100,2),round(gld_maxDD_daily*100,2)],
        'Var(95)(in %)':[round(spy_Var*100,2),round(btc_Var*100,2),round(gld_Var*100,2)],
        'CVar(5)(in %)':[round(spy_CVar*100,2),round(btc_CVar*100,2),round(gld_CVar*100,2)]}
summary_df = pd.DataFrame(table).transpose()
summary_df.columns = ['S&P 500', 'Bitcoin','Gold']

print('\033[1m' +  'Asset class summary statistics (2014-2022)')
display(summary_df)

# COMMAND ----------

#Add daily intraday trading ranges and plot (SP 500 & BTC only)

merged_df1['spy_range'] = (merged_df1['High_x'] - merged_df1['Low_x'])/merged_df1['Open_x']
merged_df1['btc_range'] = (merged_df1['High_y'] - merged_df1['Low_y'])/merged_df1['Open_y']

merged_df1['spy_range_mean'] = merged_df1['spy_range'].mean()
merged_df1['btc_range_mean'] = merged_df1['btc_range'].mean()

fig, ax = plt.subplots(1,2,figsize=(15,5),sharey=True)
plt.suptitle('Intraday trading ranges',fontweight='bold',y=1.0)

ax[0].plot(merged_df1.index, merged_df1['spy_range'], color='lightseagreen', label='Daily intraday range')
#.rolling() is used to provide rolling window calculations
ax[0].plot(merged_df1.index, merged_df1['spy_range'].rolling(50).mean(), color='teal', label='50-day average')
ax[0].plot(merged_df1.index, merged_df1['spy_range_mean'] , color='lightcoral', label='Long-term average')
ax[0].set_title('S&P 500')
ax[0].set_ylabel('Intraday range')
ax[0].legend(loc='upper left')

ax[1].plot(merged_df1.index, merged_df1['btc_range'] , color='lightseagreen')
ax[1].plot(merged_df1.index, merged_df1['btc_range'] .rolling(50).mean(), color='teal')
ax[1].plot(merged_df1.index, merged_df1['btc_range_mean'], color='lightcoral')
ax[1].set_title('Bitcoin')

plt.show()

# COMMAND ----------

#Inflation Analysis
#Calculate correlation matrix on monthly changes
final_df['cpi_pct'] = cpi_df.CPIAUCSL.pct_change()
corr_df = final_df[['spy_pct','btc_pct','gld_pct','cpi_pct']]
corr_df.rename(columns={'spy_pct':'S&P 500','btc_pct':'Bitcoin','gld_pct':'Gold','cpi_pct':'CPI US'},inplace=True)
corr_mat = corr_df.corr().round(2)

# COMMAND ----------

#Scatterplots with linear regression lines
sp = corr_df['S&P 500']
btc = corr_df['Bitcoin']
cpi = corr_df['CPI US']
gld = corr_df['Gold']

res1 = stats.linregress(sp, btc)
res2 = stats.linregress(cpi, sp)
res3 = stats.linregress(cpi, btc)
res4 = stats.linregress(cpi,gld)

fig, ax = plt.subplots(1,4, figsize=(20,5))
fig.suptitle('S&P 500, Bitcoin and inflation (scatterplots of monthly changes)',fontweight='bold')

ax[0].scatter(corr_df['S&P 500'], corr_df['Bitcoin'], color='teal')
ax[0].set_xlabel('S&P 500 (m/m)')
ax[0].set_ylabel('Bitcoin (m/m)',labelpad=-10)
ax[0].tick_params(bottom=False)

fx = np.array([sp.min(), sp.max()])
fy = res1.intercept + res1.slope * fx
ax[0].plot(fx,fy,color='lightcoral',lw=2)

#.scatter() function to draw a scatter plot
ax[1].scatter(corr_df['CPI US'], corr_df['S&P 500'], color='teal')
ax[1].set_xlabel('US CPI (m/m)')
ax[1].set_ylabel('S&P 500 (m/m)',labelpad=-10)
ax[1].tick_params(bottom=False)

fx = np.array([cpi.min(), cpi.max()])
fy = res2.intercept + res1.slope * fx
ax[1].plot(fx,fy,color='lightcoral',lw=2)

ax[2].scatter(corr_df['CPI US'], corr_df['Bitcoin'], color='teal')
ax[2].set_xlabel('US CPI (m/m)')
ax[2].set_ylabel('Bitcoin (m/m)',labelpad=-10)
ax[2].tick_params(bottom=False)

fx = np.array([cpi.min(), cpi.max()])
fy = res3.intercept + res1.slope * fx
ax[2].plot(fx,fy,color='lightcoral',lw=2)

ax[3].scatter(corr_df['CPI US'], corr_df['Gold'], color='teal')
ax[3].set_xlabel('US CPI (m/m)')
ax[3].set_ylabel('Gold (m/m)',labelpad=-10)
#.tick_params() changes the appearance of ticks, tick_labels, & gridlines
ax[3].tick_params(bottom=False)

fx = np.array([cpi.min(), cpi.max()])
fy = res4.intercept + res1.slope * fx
ax[3].plot(fx,fy,color='lightcoral',lw=2)

plt.show()

print()
print('\033[1m' + ' Correlation coefficients')
display(corr_mat)

# COMMAND ----------

#Find BTC returns in different inflation percentiles and show in boxplot
#np.percentile() is used to compute the nth percentile of the array elements over a specified axis
btc_90perc = corr_df['Bitcoin'][corr_df['CPI US'] >= np.percentile(corr_df['CPI US'],90)]
btc_between = corr_df['Bitcoin'][corr_df['CPI US'] < np.percentile(corr_df['CPI US'],90)][corr_df['CPI US'] > np.percentile(corr_df['CPI US'],10)]
btc_10perc = corr_df['Bitcoin'][corr_df['CPI US'] <= np.percentile(corr_df['CPI US'],10)]

perc_data =  [btc_90perc, btc_between, btc_10perc]

fig, ax = plt.subplots(figsize=(8,6))
plt.title('Fig. 9: Monthly Bitcoin returns by inflation percentiles',fontweight='bold')

ax.boxplot(perc_data,labels=['High CPI (top 10%)','Medium CPI','Low CPI (bottom 10%)'],showfliers=False,showmeans=True,patch_artist=True,
           boxprops=dict(facecolor='whitesmoke'),medianprops=dict(color='lightcoral',linewidth=2.5),meanprops=dict(markerfacecolor='teal',markeredgecolor='teal',markersize=8))

ax.set_ylabel('Bitcoin returns (m/m)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(left=False)

plt.show()


# COMMAND ----------

#Portfolio Allocation & Analysis
corr_sp500_btc = corr_mat.iloc[0,2]
corr_sp500_gold = corr_mat.iloc[0,1]
corr_btc_gold = corr_mat.iloc[1,2]

vol_list = []
ret_list = []
vol_table = pd.DataFrame()

for i in range(0,120,20):
    for j in range(0,120,20):
        if i+j<=100:
            w_spy = i/100
            w_btc = j/100
            w_gld = 1-w_spy-w_btc
            
            port_vol = ((w_spy**2)*(spy_ann_sdv**2)+(w_btc**2)*(btc_ann_sdv**2)+(w_gld**2)*(gld_ann_sdv**2)
                       +(2*corr_sp500_btc*w_spy*w_btc*spy_ann_sdv*btc_ann_sdv)
                        +(2*corr_sp500_gold*w_spy*w_gld*spy_ann_sdv*gld_ann_sdv)
                       +(2*corr_btc_gold*w_btc*w_gld*btc_ann_sdv*gld_ann_sdv)) ** (1/2)
            
            port_ret = w_spy*spy_return_ann + w_btc*btc_return_ann + w_gld*gld_return_ann
            
            vol_list.append(port_vol*100)
            ret_list.append(port_ret*100)
            
        else:
            vol_list.append(np.nan)
            ret_list.append(np.nan)
            
            
vol_table['0% Equities'] = vol_list[0:6]
vol_table['20% Equities'] = vol_list[6:12]
vol_table['40% Equities'] = vol_list[12:18]
vol_table['60% Equities'] = vol_list[18:24]
vol_table['80% Equities'] = vol_list[24:30]
vol_table['100% Equities'] = vol_list[30:36]

vol_table.set_index(pd.Index(['0% Bitcoin','20% Bitcoin','40% Bitcoin','60% Bitcoin','80% Bitcoin','100% Bitcoin']), inplace=True)

print('\033[1m' + 'Portfolio volatility for different allocations (in % p.a.)')
display(vol_table.style.highlight_min(axis=None, color='cyan'))

# COMMAND ----------

# Run 1000 random portfolio samples to build risk-return scatter (estimated efficient frontier)
risk_ret = {}
risk_w = {}
#initializes a random number generator starting at 1
np.random.seed(1)
#draws samples from a uniform distribution
for i in np.random.uniform(0,.99,1000):
    w_spy = round(i,4)
    #random.randint() returns random ints from the defined interval
    w_btc = np.random.randint(100-w_spy*100)/100
    w_gld = 1-w_spy*w_btc
        
    port_vol = ((w_spy**2)*(spy_ann_sdv**2)+(w_btc**2)*(btc_ann_sdv**2)+(w_gld**2)*(gld_ann_sdv**2)
                       +(2*corr_sp500_btc*w_spy*w_btc*spy_ann_sdv*btc_ann_sdv)
                        +(2*corr_sp500_gold*w_spy*w_gld*spy_ann_sdv*gld_ann_sdv)
                       +(2*corr_btc_gold*w_btc*w_gld*btc_ann_sdv*gld_ann_sdv)) ** (1/2)
    
    port_ret = w_spy*spy_return_ann + w_btc*btc_return_ann + w_gld*gld_return_ann
    
    risk_ret[port_vol]=port_ret
    risk_w[port_vol]=w_spy,w_btc,w_spy
    
risk_return_df = pd.DataFrame(list(risk_ret.items()),columns = ['Ptf volatility','Ptf return']) 
risk_weights_df = pd.DataFrame(list(risk_w.items()),columns = ['Ptf volatility','Asset class weights']) 
risk_return_df['Ptf Sharpe'] = risk_return_df['Ptf return'] / risk_return_df['Ptf volatility']
portfolio_df = risk_return_df.merge(risk_weights_df) 

fig, ax = plt.subplots(figsize=(8,6))
plt.title('Efficient frontier (2014-2021)',fontweight='bold')

sns.scatterplot(portfolio_df['Ptf volatility'],portfolio_df['Ptf return'],hue=portfolio_df['Ptf Sharpe'], palette='RdBu', alpha = 0.5)
ax.scatter(spy_ann_sdv, spy_return_ann, color='teal')
ax.scatter(btc_ann_sdv, btc_return_ann, color='orange')
ax.scatter(gld_ann_sdv, gld_return_ann, color='gold')
ax.set_xlabel('Annualized volatility')
ax.set_ylabel('Annualized total return')
ax.set_ylim([0,0.8])
ax.set_xlim([0,0.9])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(loc='upper left',title='Portfolio Sharpe')
ax.annotate('S&P 500', (0.16, 0.10), color='teal')
ax.annotate('Bitcoin', (0.80, 0.65), color='lightcoral')
ax.annotate('Gold', (0.14, 0.05), color='black')

plt.show()

# COMMAND ----------

#Approximate the min vola and max Sharpe ratio portfolios (from the 1000 random samples above)
min_vol = portfolio_df['Ptf volatility'].min()
min_vol_ret = portfolio_df['Ptf return'][portfolio_df['Ptf volatility'] == min_vol]
min_vol_SR = portfolio_df['Ptf Sharpe'][portfolio_df['Ptf volatility'] == min_vol]
min_vol_w = portfolio_df['Asset class weights'][portfolio_df['Ptf volatility'] == min_vol]

max_SR = portfolio_df['Ptf Sharpe'].max()
max_SR_vol = portfolio_df['Ptf volatility'][portfolio_df['Ptf Sharpe'] == max_SR]
max_SR_ret = portfolio_df['Ptf return'][portfolio_df['Ptf Sharpe'] == max_SR]
max_SR_w = portfolio_df['Asset class weights'][portfolio_df['Ptf Sharpe'] == max_SR]

#Summary table
#.reset_index() allows you to reset the indices back to 0,1,2,...
Opt_ptfs1 = {'Equity weight (in %)': [round(min_vol_w.reset_index()['Asset class weights'][0][0]*100,0), round(max_SR_w.reset_index()['Asset class weights'][0][0]*100,0)], 
            'Gold weight (in %)': [round(min_vol_w.reset_index()['Asset class weights'][0][1]*100,0), round(max_SR_w.reset_index()['Asset class weights'][0][1]*100,0)],
            'Bitcoin weight (in %)': [round(min_vol_w.reset_index()['Asset class weights'][0][2]*100,0), round(max_SR_w.reset_index()['Asset class weights'][0][2]*100,0)],
            'Annual ptf return (in %)': [round(min_vol_ret.iloc[0]*100,2), round(max_SR_ret.iloc[0]*100,2)],
            'Annual ptf volatility (in %)': [round(min_vol*100,2), round(max_SR_vol.iloc[0]*100,2)], 
            'Ptf Sharpe ratio': [round(min_vol_SR.iloc[0],2), round(max_SR,2)] }

#.iloc() is used for integer indexing
Opt_ptfs1_df = pd.DataFrame(Opt_ptfs1).transpose()
Opt_ptfs1_df.columns = ['Min volatility ptf (random sampling)', 'Max Sharpe ptf (random sampling)']

print('\033[1m' + 'Minimum volatility and maximum Sharpe ratio portfolios (approximated by random sampling)')
display(Opt_ptfs1_df)

# COMMAND ----------

#Add min vola and max Sharpe portfolios to efficient frontier chart (and "zoom in")
fig, ax = plt.subplots(1,2,figsize=(20,6))
plt.suptitle('Efficient frontier (2014-2022)',fontweight='bold')

sns.scatterplot(portfolio_df['Ptf volatility'],portfolio_df['Ptf return'],ax=ax[0],hue=portfolio_df['Ptf Sharpe'], palette='RdBu', alpha = 0.5)
ax[0].scatter(spy_ann_sdv, spy_return_ann, color='teal')
ax[0].scatter(btc_ann_sdv, btc_return_ann, color='lightcoral')
ax[0].scatter(gld_ann_sdv, gld_return_ann, color='gold')
ax[0].set_xlabel('Annualized volatility')
ax[0].set_ylabel('Annualized total return')
ax[0].set_ylim([0,0.9])
ax[0].set_xlim([0,0.9])
ax[0].spines['top'].set_visible(False)
ax[0].spines['right'].set_visible(False)
ax[0].legend(loc='upper left',title='Portfolio Sharpe')
ax[0].annotate('S&P 500', (0.16, 0.12), color='teal')
ax[0].annotate('Bitcoin', (0.84, .61), color='lightcoral')
ax[0].annotate('Gold', (0.14, 0.04), color='black')

ax[0].scatter(min_vol, min_vol_ret, color='red')
ax[0].scatter(max_SR_vol, max_SR_ret, color='red')
ax[0].annotate('Min volatility', (0.001, 0.0111), color='red')
ax[0].annotate('Max SR', (0.3, 0.33), color='red')


sns.scatterplot(portfolio_df['Ptf volatility'],portfolio_df['Ptf return'],ax=ax[1],hue=portfolio_df['Ptf Sharpe'], palette='RdBu', alpha = 0.5)
ax[1].scatter(spy_ann_sdv, spy_return_ann, color='teal')
ax[1].scatter(btc_ann_sdv, btc_return_ann, color='lightcoral')
ax[1].scatter(gld_ann_sdv, gld_return_ann, color='black')
ax[1].set_xlabel('Annualized volatility')
ax[1].set_ylabel('Annualized total return')
ax[1].set_ylim([0,0.4])
ax[1].set_xlim([0,0.4])
ax[1].spines['top'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[1].legend(loc='upper left',title='Portfolio Sharpe')
ax[1].annotate('S&P 500', (0.15, 0.12), color='teal')
ax[1].annotate('Gold', (0.13, 0.05), color='gold')

ax[1].scatter(min_vol, min_vol_ret, color='red')
ax[1].scatter(max_SR_vol, max_SR_ret, color='red')
ax[1].annotate('Min vola', (0.13, 0.03), color='red')
ax[1].annotate('Max SR', (0.3, 0.33), color='red')

plt.show()

# COMMAND ----------

#Min vola optimization
cov = corr_df.drop('CPI US',axis=1).cov()*12
exp_returns = [spy_return_ann, btc_return_ann, gld_return_ann]

# ef is the set of optimal portfolios maximizing the exp_returns for defined cov levels or the lowest cov for a given exp_return
ef = EfficientFrontier(exp_returns, cov, solver=cp.CVXOPT)

ef.min_volatility()
min_vol_w = ef.clean_weights()
min_vol_ptf = ef.portfolio_performance(risk_free_rate=0)

# COMMAND ----------

#Max Sharpe optimization
ef = EfficientFrontier(exp_returns, cov)

ef.max_sharpe(risk_free_rate=0)
max_SR_w = ef.clean_weights()
max_SR_ptf = ef.portfolio_performance(risk_free_rate=0)

# COMMAND ----------

#Min vola optimization with a min. BTC weight of 5%
ef = EfficientFrontier(exp_returns, cov, weight_bounds=(0.05,1))

ef.min_volatility()
#clean_weights rounds the weights & clips near-zeros
min_vol_w = ef.clean_weights()
#portfolio.performance() calculates the expected return, volatility, & sharpe ratio for the optimized portfolio
min_vol_ptf = ef.portfolio_performance(risk_free_rate=0)

# COMMAND ----------

#Summary table
Opt_ptfs2 = {'Equity weight (in %)': [round(min_vol_w['S&P 500']*100,0), round(max_SR_w['S&P 500']*100,0), round(min_volBTC_w['S&P 500']*100,0)], 
            'Gold weight (in %)': [round(min_vol_w['Gold']*100,0), round(max_SR_w['Gold']*100,0), round(min_volBTC_w['Gold']*100,0)],
            'Bitcoin weight (in %)': [round(min_vol_w['Bitcoin']*100,0), round(max_SR_w['Bitcoin']*100,0), round(min_volBTC_w['Bitcoin']*100,0)],
            'Annual ptf return (in %)': [round(min_vol_ptf[0]*100,2), round(max_SR_ptf[0]*100,2), round(min_volBTC_ptf[0]*100,2)],
            'Annual ptf volatility (in %)': [round(min_vol_ptf[1]*100,2), round(max_SR_ptf[1]*100,2), round(min_volBTC_ptf[1]*100,2)], 
            'Ptf Sharpe ratio': [round(min_vol_ptf[2],2), round(max_SR_ptf[2],2), round(min_volBTC_ptf[2],2)] }

Opt_ptfs2_df = pd.DataFrame(Opt_ptfs2).transpose()
Opt_ptfs2_df.columns = ['Min volatility ptf (opt.)', 'Max Sharpe ptf (opt.)', 'Min Volatility with 2% BTC allocation (opt.)']

print('\033[1m' + ' Minimum volatility and maximum Sharpe ratio portfolios (optimized)')
display(Opt_ptfs2_df)

# COMMAND ----------

#Illustrate the historic development for three "optimal" portfolios in a line chart
corr_df['Min volatility ptf'] = min_vol_w['S&P 500']*corr_df['S&P 500'] + min_vol_w['Gold']*corr_df['Gold'] + min_vol_w['Bitcoin']*corr_df['Bitcoin']
corr_df['Max Sharpe ptf'] = max_SR_w['S&P 500']*corr_df['S&P 500'] + max_SR_w['Gold']*corr_df['Gold'] + max_SR_w['Bitcoin']*corr_df['Bitcoin']
corr_df['Min vola w. BTC ptf'] = min_volBTC_w['S&P 500']*corr_df['S&P 500'] + min_volBTC_w['Gold']*corr_df['Gold'] + min_volBTC_w['Bitcoin']*corr_df['Bitcoin']

corr_df['Min vola ptf index'] = 100.0
corr_df['Max Sharpe ptf index'] = 100.0
corr_df['Min vola w. BTC ptf index'] = 100.0

for i in range(len(corr_df)-1):
    corr_df['Min vola ptf index'][i+1] = corr_df['Min vola ptf index'][i] * (1 + corr_df['Min volatility ptf'][i+1])
    corr_df['Max Sharpe ptf index'][i+1] = corr_df['Max Sharpe ptf index'][i] * (1 + corr_df['Max Sharpe ptf'][i+1])
    corr_df['Min vola w. BTC ptf index'][i+1] = corr_df['Min vola w. BTC ptf index'][i] * (1 + corr_df['Min vola w. BTC ptf'][i+1])

    
fig, ax = plt.subplots(1,3, figsize=(20,5))
plt.suptitle('Total returns of optimized portfolios (Sep 2014 = 100)',fontweight='bold',y=1.0)

ax[0].plot(corr_df.index, corr_df['Min vola ptf index'],color='teal')
ax[0].set_title('Minimum volatility portfolio')

ax[1].plot(corr_df.index, corr_df['Min vola w. BTC ptf index'],color='teal')
ax[1].set_title('Minimum volatility portfolio (with 2% BTC)')

ax[2].plot(corr_df.index, corr_df['Max Sharpe ptf index'],color='teal')
ax[2].set_title('Maximum Sharpe ratio portfolio')

plt.show()

# COMMAND ----------

#Add MC simulation based on normal distribution for both portfolios (just 50 runs each for illustration)
fig, ax = plt.subplots(1,3, figsize=(20,5), sharey=True)
plt.suptitle('Monto Carlo simulations (shared y-axis)',fontweight='bold',y=1.0)

ax[0].set_title('Minimum volatility portfolio')

ax[1].set_title('Minimum volatility portfolio (with 2% BTC)')

ax[2].set_title('Maximum Sharpe portfolio')


np.random.seed(1)

for i in range(50):

    s = np.random.normal((1+min_vol_ptf[0])**(1/12)-1, min_vol_ptf[1] / (12**0.5),97)

    corr_df['random'] = s
    corr_df['random index'] = 100.0

    for j in range(len(corr_df)-1):
        corr_df['random index'][j+1] = corr_df['random index'][j] * (1 + corr_df['random'][j+1])

    ax[0].plot(corr_df.index, corr_df['random index'],color='lightcoral')

    
for i in range(50):

    s = np.random.normal((1+min_volBTC_ptf[0])**(1/12)-1, min_volBTC_ptf[1] / (12**0.5),97)

    corr_df['random'] = s
    corr_df['random index'] = 100.0

    for j in range(len(corr_df)-1):
        corr_df['random index'][j+1] = corr_df['random index'][j] * (1 + corr_df['random'][j+1])

    ax[1].plot(corr_df.index, corr_df['random index'],color='lightcoral')  

for i in range(50):
    #draw random samples from a normal dist
    s = np.random.normal((1+max_SR_ptf[0])**(1/12)-1, max_SR_ptf[1] / (12**0.5),97)

    corr_df['random'] = s
    corr_df['random index'] = 100.0

    for j in range(len(corr_df)-1):
        corr_df['random index'][j+1] = corr_df['random index'][j] * (1 + corr_df['random'][j+1])

    ax[2].plot(corr_df.index, corr_df['random index'],color='lightcoral') 

    
ax[0].plot(corr_df.index, corr_df['Min vola ptf index'],color='teal',linewidth=3)
ax[1].plot(corr_df.index, corr_df['Min vola w. BTC ptf index'],color='teal',linewidth=3)
ax[2].plot(corr_df.index, corr_df['Max Sharpe ptf index'],color='teal',linewidth=3)

plt.show()
