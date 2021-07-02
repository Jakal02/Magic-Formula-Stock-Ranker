
import magicsite
import yahoosite


### Grab Tickers from magicformulainvesting.com ###
# 2D array: row = [Ticker, mkt cap(millions)]
tickers_data = magicsite.grab_tickers()
### Calculate ROC and Earnings Yield for each ticker ###
### Uses Yahoo Finance ###

# 2D array: row = [Ticker, ROC, Earnings Yield]
magic_formula_data = yahoosite.find_roc_and_eyield(tickers_data)
print(magic_formula_data)
### Find inside ownership and chng in it for past 6 months ###
### Uses Finviz ###
insider_data = ""


### Find # of Superinvestors in it, and weighting of highest conviction investor ###
super_data = ""



### Take this data and put it into a csv file ### 