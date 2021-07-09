
import magicsite
#import dataroma
#import finviz
#import vic
import pandas as pd

### Grab Tickers from magicformulainvesting.com ###

tickers_data = magicsite.grab_tickers()
tickers_only = pd.DataFrame(tickers_data["Ticker"],columns=["Ticker"])

### Get # of Superinvestors ###
guru_data = magicsite.get_num_gurus(tickers_only)

### Get Most Recent VIC writeup ###
vic_data = magicsite.get_vic_writeup(tickers_only)

### Get InsiderInformation ###
insider_data = magicsite.get_insider_ownership(tickers_only)

### Append data to original set ###
l = [guru_data,vic_data,insider_data]
for i in l:
    tickers_data = tickers_data.merge(i)

### Write to csv file to paste into google sheets ###
with open('magic.csv','w') as csv_file:
    tickers_data.to_csv(path_or_buf = csv_file,line_terminator='\n',index=False)

### Done ###
