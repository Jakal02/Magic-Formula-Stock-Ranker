#import libraries
#import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from password import get_cred
import yfinance as yf

# Initiate the browser
def init_browser():
    op = webdriver.ChromeOptions()
    op.add_argument('headless') # prevents browser from actually popping up
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=op)
    browser.implicitly_wait(10)
    return browser

##### Gather 30 stocks at X mkt cap ##########

def gather_info(browser):

    browser.find_element_by_id('stocks').click()
    before_XPath = "//*[@id='tableform']/table/tbody/tr["
    aftertd_XPath = "]/td["
    aftertr_XPath = "]"
    rows = len(browser.find_elements_by_xpath("//*[@id='tableform']/table/tbody/tr"))
    data = []
    for t_row in range(1, (rows + 1)):
        name_path = before_XPath + str(t_row) + aftertd_XPath + "1" + aftertr_XPath
        ticker_path = before_XPath + str(t_row) + aftertd_XPath + "2" + aftertr_XPath
        mkt_path = before_XPath + str(t_row) + aftertd_XPath + "3" + aftertr_XPath
        company_name = browser.find_element_by_xpath(name_path).text
        ticker = browser.find_element_by_xpath(ticker_path).text
        mkt_cap = float(browser.find_element_by_xpath(mkt_path).text.replace(',',''))
        data.append( (ticker,company_name,mkt_cap) )
    return data


def grab_tickers(mkt_min, stock_num):
    browser = init_browser()
    # Open Log On Page
    browser.get('https://www.magicformulainvesting.com/Account/LogOn')

    # Fill credentials
    login_magic(browser)
    #Edit Market Cap search criteria
    change_mkt_cap(browser, mkt_min)
    #Edit num stocks search criteria
    change_num_stocks(browser, stock_num)

    data = gather_info(browser)
    data.sort()
    print(data)
    browser.close()
    return data

def login_magic(browser):
    user1,passw1 = get_cred()

    
    browser.find_element_by_name("Email").send_keys(user1)
    browser.find_element_by_name("Password").send_keys(passw1)
    browser.find_element_by_id('login').click()

def change_mkt_cap(browser, mkt_min):
    target_cap = mkt_min
    mkt_cap_box = browser.find_element_by_name("MinimumMarketCap")
    browser.execute_script('arguments[0].value = "";', mkt_cap_box)
    mkt_cap_box.send_keys(target_cap)

def change_num_stocks(browser, stock_num):
    if(stock_num == 50):
        #print('hello')
        browser.find_elements_by_id("Select30")[1].click()
    else:
        #print('goodbye')
        browser.find_element_by_id("Select30").click()

def select_num_stocks():
    while True:
        try:
            val = int(input('Would you like to see 30 or 50 stocks? '))
            if(val != 30 and val != 50):
                print('Please enter 30 or 50')
                continue
            break
        except ValueError:
            print('Please enter a whole number')
    return val

def select_mkt_cap():
    while True:
        try:
            val = int(input('In millions, Select the minimum market cap: '))
            if(val < 50 or val > 1000000):
                print('Please enter a value between 50 and 1,000,000')
                continue
            break
        except ValueError:
            print('Please enter a whole number')
    return val


def rank_tickers(mkt_min, num_stocks):
    t_list = grab_tickers(mkt_min, num_stocks)
    data = ["Ticker","ROC","Earnings Yield"]

    for i in range(0,num_stocks,1):

        curr_stock = t_list[i]
        roc, earnings_yield = get_variables(curr_stock)
        print(curr_stock[0], roc, earnings_yield)
        data.append([curr_stock[0],roc,earnings_yield])
    return data


def get_variables(curr_stock):
    
    ticker = yf.Ticker(curr_stock[0])
    q_income = ticker.quarterly_financials
    q_balance = ticker.quarterly_balance_sheet
    
    ebit = q_income.loc['Ebit'][0] 
    mkt_cap = curr_stock[2] * pow(10,6)
    cash = q_balance.loc['Cash'][0]
    current_liab = q_balance.loc['Total Current Liabilities'][0]
    long_debt = q_balance.loc['Long Term Debt'][0]
    total_debt = (long_debt + current_liab )

    ent_val = mkt_cap + total_debt - cash
    
    
    work_cap = q_balance.loc['Total Current Assets'][0] - q_balance.loc['Total Current Liabilities'][0]
    fixed_assets = get_fixed_assets(curr_stock[0])
    
    roc = ebit / (work_cap + fixed_assets)
    earnings_yield = ebit/ent_val

    return [roc, earnings_yield]

def get_fixed_assets(ticker_name):
    browser = init_browser()
    link = 'https://finance.yahoo.com/quote/'+ticker_name+'/balance-sheet?p='+ticker_name
    browser.get(link)
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/button').click()
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()
    accum = browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]').text
    accum = float(accum.replace(',',''))
    fixed_assets = browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/span').text
    fixed_assets = float(fixed_assets.replace(',',''))
    
    return fixed_assets - accum


#print(rank_tickers(50,30))
print(yf.Ticker('ASO').balance_sheet)
print(yf.Ticker('BKE').balance_sheet)
# Need to fix data that is missing
'''
Variables I need:

Earning Yield = EBIT/EV
    Ent Val = Mkt_cap + Total Debt - Cash
    EBIT = Total_Rev - Cost of Goods Sold - Operating Expenses

Return on Capital = EBIT / ( Net Fixed Assests + Working Capital)

'''

