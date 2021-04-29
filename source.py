#import libraries
#import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Initiate the browser
def init_browser():
    op = webdriver.ChromeOptions()
    #op.add_argument('headless') # prevents browser from actually popping up
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=op)
    return browser

##### Gather 30 stocks at X mkt cap ##########

def gather_info(browser):

    browser.find_element_by_id('stocks').click()
    before_XPath = "//*[@id='tableform']/table/tbody/tr["
    aftertd_XPath = "]/td["
    aftertr_XPath = "]"
    browser.implicitly_wait(500)
    rows = len(browser.find_elements_by_xpath("//*[@id='tableform']/table/tbody/tr"))
    data = []
    for t_row in range(1, (rows + 1)):
        name_path = before_XPath + str(t_row) + aftertd_XPath + "1" + aftertr_XPath
        ticker_path = before_XPath + str(t_row) + aftertd_XPath + "2" + aftertr_XPath
        company_name = browser.find_element_by_xpath(name_path).text
        ticker = browser.find_element_by_xpath(ticker_path).text
        data.append( (ticker,company_name) )
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
    return data

def login_magic(browser):
    user = "insert your email here"
    password = "insert yours here"
    browser.find_element_by_name("Email").send_keys(user)
    browser.find_element_by_name("Password").send_keys(password)
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
