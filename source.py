#import libraries
#import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from password import get_cred


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

    #user = "elijahgrubbs@hotmail.com"
    #password = "quigongin1"
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
    ranked_list = []
    browser = init_browser()

    for i in range(0,num_stocks,1):
        link = "https://www.morningstar.com/stocks/xnas/"+t_list[i][0]+"/financials"
        browser.get(link)
        browser.find_element_by_xpath('//*[@id="__layout"]/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/section/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/a').click()
        elem = browser.find_element_by_xpath('//*[@id="tabs"]')
        browser.execute_script(elem.setAttribute('selected-tab','Quarterly'))
        # Need to Change Annual Data to Quarterly
        curr_stock = t_list[i]
        earn = calc_earnings_yield(browser,curr_stock[2])
        
    return t_list

def calc_earnings_yield(browser,mkt_cap):
    frac = calc_ebit(browser)/calc_ent_val(browser,mkt_cap) * 100
    return frac

def calc_ebit(browser):
    total_rev = '5'
    return float(total_rev)

def calc_ent_val(browser,mkt_cap):
    total_debt = '5'
    cash = '5'
    ent_val = mkt_cap/1000 + float(total_debt.replace(',','')) - float(cash.replace(',',''))
    return ent_val

