# Use Later to make final nice file
from source import *


if will_refresh_data() == 'y':
    print("\n\tThis will take around 3 minutes\n")
# Ask user for
#   1. # of stocks
    stock_num = select_num_stocks()
#   2. mkt cap minimum
    mkt_min = select_mkt_cap()

#### Grab Tickers and Company names from magicformulainvesting.com ####
#ticker_data = grab_tickers(mkt_min, stock_num)
    tickers_to_csv(mkt_min,stock_num)
    print("Successly written all",stock_num,"with multiples into data.csv")

print("Done")