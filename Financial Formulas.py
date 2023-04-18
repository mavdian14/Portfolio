# Databricks notebook source
#make necessary imports
import numpy as np
import pandas as pd


%load_ext autoreload
%autoreload 2

# COMMAND ----------

#formula to calcualte the price of a discount bond paying $1 at time t & r is interest rate
def discount(t, r):
    """
    Compute the price of a pure discount bond that pays $1 at time t where t is in years and r is the annual interest rate
    """
    return (1+r)**(-t)

# COMMAND ----------

b = discount(10, .03)
b

# COMMAND ----------

b*(1.03**10)

# COMMAND ----------

#formula for present value of list of liabilities w/ time (index) & amounts
def pv(l, r):
    """
    Compute the present value of a list of liabilities given by the time (as an index) and amounts
    """
    dates = l.index
    discounts = discount(dates, r)
    return (discounts*l).sum()

# COMMAND ----------

liabilities = pd.Series(data=[1, 1.5, 2, 2.5], index=[3, 3.5, 4, 4.5])

# COMMAND ----------

pv(liabilities, 0.03)

# COMMAND ----------

def funding_ratio(assets, liabilities, r):
    """
    Computes the funding ratio of a series of liabilities, based on an interest rate and current value of assets
    """
    return assets/pv(liabilities, r)

# COMMAND ----------

funding_ratio(5, liabilities, 0.03)

# COMMAND ----------

funding_ratio(5, liabilities, 0.02)

# COMMAND ----------

liabilities

# COMMAND ----------

import ipywidgets as widgets
from IPython.display import display
%matplotlib inline

def show_funding_ratio(assets, r):
    fr = funding_ratio(assets, liabilities, r)
    print(f'{fr*100:.2f}%')
    
controls = widgets.interactive(show_funding_ratio,
                                   assets=widgets.IntSlider(min=1, max=10, step=1, value=5),
                                   r=(0, .20, .01)
)
display(controls)

# COMMAND ----------

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import HBox, VBox

# COMMAND ----------

#formula to calculate cumulative future value of an asset's current value 
def fv_cum(value, r, t):
    future_value = value*(1+r)**t
       
    return round(future_value, 2)

# COMMAND ----------

fv_cum(100, .06, 30)

# COMMAND ----------

import numpy_financial as npf
# Calculate investment
investment = npf.fv(rate=.05, nper=2, pmt=0, pv=-100)
print("$" + str(round(investment, 2)))

# COMMAND ----------

plt.figure(figsize=(10,8))

y = [npf.fv(rate=np.linspace(0.0,0.15,num=4), nper=i, pmt=0.0, pv=-100) for i in range(21)]

plt.plot(y)

plt.legend(["r = 0%", "r = 5%","r = 10%" , "r = 15%"])

plt.ylabel('Future value of $100, dollars')
plt.xlabel('years')

# COMMAND ----------

import ipywidgets as widgets
from IPython.display import display

%matplotlib inline


def show_fv(rate):
    plt.figure(figsize=(10,8))
    y = [npf.fv(rate, nper=i, pmt=0, pv=-100) for i in range(21)]

    plt.plot(y)

    plt.ylabel('Future value of $100, dollars')
    plt.xlabel('years')
    
controls = widgets.interactive(show_fv,rate=(0, .20, .01))

display(controls)

# COMMAND ----------

#Adjusting Future Values for Inflation

# Calculate investment_1
investment_1 = npf.fv(rate=0.08, nper=10, pmt=0, pv=-10000)
print("Investment 1 will yield a total of $" + str(round(investment_1, 2)) + " in 10 years")

# Calculate investment_2
investment_1_discounted = npf.pv(rate=0.03, nper=10, pmt=0, fv=investment_1)
print("After adjusting for inflation, investment 1 is worth $" + str(round(-investment_1_discounted, 2)) + " in today's dollars")

# COMMAND ----------

#Discounting Cash Flows

# Predefined array of cash flows
cash_flows = np.array([100, 100, 100, 100, 100])

# Calculate investment_1
investment_1 = npf.npv(rate=.03, values=cash_flows)
print("Investment 1's net present value is $" + str(round(investment_1, 2)) + " in today's dollars")

# Calculate investment_2
investment_2 = npf.npv(rate=.05, values=cash_flows)
print("Investment 2's net present value is $" + str(round(investment_2, 2)) + " in today's dollars")

# COMMAND ----------

# Create an array of cash flows for project 1
cash_flows_1 = np.array([-250, 100, 200, 300, 400])

# Create an array of cash flows for project 2
cash_flows_2 = np.array([-250, 300, -250, 300, 300])


# Calculate the net present value of project 1
investment_1 = npf.npv(rate=0.03, values=cash_flows_1)

print("The net present value of Investment 1 is worth $" + str(round(investment_1, 2)) + " in today's dollars")

# Calculate the net present value of project 2
investment_2 = npf.npv(rate=0.03, values=cash_flows_2)
print("The net present value of Investment 2 is worth $" + str(round(investment_2, 2)) + " in today's dollars")

# COMMAND ----------

#Diminishing Cash Flows

# Calculate investment_1
investment_1 = npf.pv(rate=.03, nper=30, pmt=0, fv=100)
print("Investment 1 is worth $" + str(round(-investment_1, 2)) + " in today's dollars")

# Calculate investment_2
investment_2 = npf.pv(rate=.03, nper=50, pmt=0, fv=100)
print("Investment 2 is worth $" + str(round(-investment_2, 2)) + " in today's dollars")
