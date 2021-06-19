# Use Later to make final nice file
from source import *

# Ask user for
#   1. # of stocks
stock_num = select_num_stocks()
#   2. mkt cap minimum
mkt_min = select_mkt_cap()

#### Grab Tickers and Company names from magicformulainvesting.com ####

#ticker_data = grab_tickers(mkt_min, stock_num)

t = rank_tickers(mkt_min,stock_num)

#print(grab_tickers(mkt_min,stock_num))


print("Done")