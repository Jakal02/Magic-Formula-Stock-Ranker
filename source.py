#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from password import get_cred
import os
import csv
# import yfinance as yf

# Initiate the browser
def init_browser():
    op = webdriver.ChromeOptions()
    op.add_argument('log-level=3')
    op.add_argument('headless') # prevents browser from actually popping up
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=op)
    browser.implicitly_wait(2)
    return browser

##### Gather 30/50 stocks at X mkt cap ##########

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
    #print(data)
    browser.close()
    return data

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
            val = int(input('\nWould you like to see 30 or 50 stocks? '))
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

def will_refresh_data():
    val = ""
    while True:
        val = input("Would you like to update the stock data on file? (y/n)").lower()
        if(val != 'n' and val != 'y'):
            print("Please Enter either 'y' or 'n'")
            continue
        break
    
    return val
##### Write 30/50 stocks ROC and Enterprise Value to csv file ##########

def tickers_to_csv(mkt_min, num_stocks):
    t_list = grab_tickers(mkt_min, num_stocks)
    data = [["Ticker","ROC","Earnings Yield"]]

    #for i in range(0,2,1):
    for i in range(0,num_stocks,1):
        print('Working on stock',i+1,'of',num_stocks)
        curr_stock = t_list[i]
        ticker = curr_stock[0]
        roc, earnings_yield = scrape_variables(ticker, curr_stock[2])
        print(ticker+':', roc, earnings_yield,'\n')
        
        row = [ticker,roc,earnings_yield]
        #data_to_csv([row])
        data.append(row)

    data_to_csv(data)

    return

# REQUIRES: Browser on a Yahoo finance stock website
def nav_to_income(browser):
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[1]/div/a[1]/div').click()
    time.sleep(2)
    expand_sheet(browser)
    return

# REQUIRES: Browser on a Yahoo finance stock website
def nav_to_quarterly(browser):
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
    time.sleep(2)
    return


def scrape_variables(ticker_name, mkt):
    browser = init_browser()
    link = 'https://finance.yahoo.com/quote/'+ticker_name+'/balance-sheet?p='+ticker_name
    browser.get(link)

    nav_to_quarterly(browser)
    expand_sheet(browser)

    mkt_cap = mkt * 1000 # TO ADD: 2nd Parameter of mkt_cap
    
    fixed_assets = get_fixed_assets(browser) # Done
    work_cap = get_working_cap(browser) # Done
    current_liab = get_current_liabilities(browser) # Done
    long_debt = get_long_debt(browser) # Done
    cash = get_cash(browser) # Done

    nav_to_income(browser)
    nav_to_quarterly(browser)
    ebit = get_ebit(browser) # Done

    total_debt = long_debt + current_liab
    ent_val = mkt_cap + total_debt - cash

    earn_yield = ebit / ent_val
    roc = ebit / (work_cap + fixed_assets)

    browser.close()
    return [roc, earn_yield]



def get_ebit(browser):
    try:
        return get_income_sheet_var(browser,"EBIT")
    except:
        total_rev = get_total_rev(browser)
        cost_of_rev = get_cost_of_rev(browser)
        op_expenses = get_op_expenses(browser)
        return total_rev - cost_of_rev - op_expenses

def get_total_rev(browser):
    return get_income_sheet_var(browser,"Total Revenue")
def get_cost_of_rev(browser):
    return get_income_sheet_var(browser,"Cost of Revenue")
def get_op_expenses(browser):
    return get_income_sheet_var(browser,"Operating Expense")


def get_long_debt(browser):
    long_debt = '0'
    try:
        long_debt = browser.find_element_by_xpath("//*[@title='Long Term Debt And Capital Lease Obligation']//parent::div//following-sibling::div[@data-test='fin-col']").text
    except:
        try:
            long_debt = browser.find_element_by_xpath("//*[@title='Total Non Current Liabilities Net Minority Interest']//parent::div//following-sibling::div[@data-test='fin-col']").text
        except:
            long_debt = '0'
    return text_to_float(long_debt)

def get_cash(browser):
    return get_balance_sheet_var(browser, "Cash And Cash Equivalents")

def get_working_cap(browser):
    try:
        return get_balance_sheet_var(browser,"Working Capital")
    except:
        current_assets = get_current_assets(browser)
        current_liabilities = get_current_liabilities(browser)
        return current_assets - current_liabilities
    
def get_current_assets(browser):
    return get_balance_sheet_var(browser, "Current Assets")

def get_current_liabilities(browser):
    return get_balance_sheet_var(browser,"Current Liabilities")

def get_fixed_assets(browser):
    accum = get_accumulated_depreciation(browser)
    fixed_assets = get_net_ppe(browser)

    return fixed_assets - accum

def get_accumulated_depreciation(browser):
    return get_balance_sheet_var(browser,'Accumulated Depreciation')
def get_net_ppe(browser):
    return get_balance_sheet_var(browser, 'Net PPE')


def get_balance_sheet_var(browser, word):
    xpath = "//*[@title='"+word+"']//parent::div//following-sibling::div[@data-test='fin-col']"
    return get_table_var(browser,xpath,word)

def get_income_sheet_var(browser, word):
    xpath = "//*[@title='"+word+"']//parent::div[1]//following-sibling::div[@data-test='fin-col'][1]"
    return get_table_var(browser,xpath,word)

def get_table_var(browser,xpath,word):
    try:
        var = browser.find_elements_by_xpath(xpath)
        var= var[0].text
    except:
        print(word,"could not be found on the balance sheet")
    return text_to_float(var)


def expand_sheet(browser):
    expand = browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span')
    if(expand.text == 'Expand All'):
        button = browser.find_element_by_class_name('expandPf')
        browser.execute_script("arguments[0].click();", button)
    return

def text_to_float(number):
    if number != "-":
        return float(number.replace(',',''))
    return 0

def data_to_csv(data, style='w'):
    loc = os.path.dirname(os.path.abspath(__file__))
    with open('data.csv', style) as csvfile:
        # delimiter=',', quoting=csv.QUOTE_ALL
        filewriter = csv.writer(csvfile,delimiter=',',lineterminator='\n')
        for row in data:
            filewriter.writerow(row)
    return



#######################################################################
#######################################################################
#######################################################################

print(scrape_variables('ASO', 3793.97))

'''
Variables I need:

Earning Yield = EBIT/EV
    Ent Val = Mkt_cap + Total Debt - Cash
    EBIT = Total_Rev - Cost of Goods Sold - Operating Expenses

Return on Capital = EBIT / ( Net Fixed Assests + Working Capital)

'''

