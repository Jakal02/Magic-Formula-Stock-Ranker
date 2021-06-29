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


##### Rank 30/50 stocks based on ROC and Enterprise Value ##########

def rank_tickers(mkt_min, num_stocks):
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

    return data

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

    
    return [roc, earn_yield]



def get_ebit(browser):
    try:
        ebit = browser.find_element_by_xpath("//*[@title='EBIT']//parent::div[1]//following-sibling::div[@data-test='fin-col'][1]").text
        return text_to_float(ebit)
    except:
        total_rev = get_total_rev(browser)
        cost_of_rev = get_cost_of_rev(browser)
        op_expenses = get_op_expenses(browser)
        return total_rev - cost_of_rev - op_expenses

def get_total_rev(browser):
    
    total_rev = browser.find_element_by_xpath("//*[@title='Total Revenue']//parent::div//following-sibling::div[2]").text
    return text_to_float(total_rev)

def get_cost_of_rev(browser):

    cost_rev = browser.find_element_by_xpath("//*[@title='Cost of Revenue']//parent::div//following-sibling::div[2]").text
    return text_to_float(cost_rev)

def get_op_expenses(browser):
    
    op_exp = browser.find_element_by_xpath("//*[@title='Operating Expense']//parent::div//following-sibling::div[2]").text

    return text_to_float(op_exp)



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
    cash = browser.find_element_by_xpath("//*[@title='Cash And Cash Equivalents']//parent::div//following-sibling::div[@data-test='fin-col']").text
    return text_to_float(cash)

def get_working_cap(browser):
    try:
        work_cap = browser.find_element_by_xpath("//*[@title='Working Capital']//parent::div//following-sibling::div[@data-test='fin-col']").text
        return text_to_float(work_cap)
    except:
        current_assets = get_current_assets(browser)
        current_liabilities = get_current_liabilities(browser)
        return current_assets - current_liabilities
    
def get_current_assets(browser):
    
    curr_assets = browser.find_element_by_xpath("//*[@title='Current Assets']//parent::div//following-sibling::div[@data-test='fin-col']").text
    return text_to_float(curr_assets)

def get_current_liabilities(browser):
    
    curr_liab = browser.find_element_by_xpath("//*[@title='Current Liabilities']//parent::div//following-sibling::div[@data-test='fin-col']").text
    return text_to_float(curr_liab)

def get_fixed_assets(browser):

    accum = get_accumulated_depreciation(browser)

    fixed_assets = get_net_ppe(browser)

    return fixed_assets - accum

def get_accumulated_depreciation(browser):
    accum = '0'
    try:
        accum = browser.find_element_by_xpath("//*[@title='Accumulated Depreciation']//parent::div//following-sibling::div[@data-test='fin-col']").text
    except:
        accum = '0'
    accum = text_to_float(accum)
    return accum

def get_net_ppe(browser):
    fixed_assets = browser.find_element_by_xpath("//*[@title='Net PPE']//parent::div//following-sibling::div[@data-test='fin-col']").text
    return text_to_float(fixed_assets)



def expand_sheet(browser):
    
    expand = browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span')
    if(expand.text == 'Expand All'):
        button = browser.find_element_by_class_name('expandPf')
        browser.execute_script("arguments[0].click();", button)
    '''
    used=[]
    all_clicked = False
    while not all_clicked:
        new_buttons = browser.find_elements_by_class_name('tgglBtn')
        for button in used:
            if button in new_buttons:
                new_buttons.remove(button)
        if len(new_buttons) == 0:
            all_clicked = True
        for button in new_buttons:
                used.append(button)
                browser.execute_script("arguments[0].click();", button)
        #time.sleep(0.5)
    '''
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
#print(rank_tickers(50,30))
#print(yf.Ticker('ASO').balance_sheet)
#print(yf.Ticker('BKE').balance_sheet)
# Need to fix data that is missing

#print(scrape_variables('VYGR', 164.12))

'''
Variables I need:

Earning Yield = EBIT/EV
    Ent Val = Mkt_cap + Total Debt - Cash
    EBIT = Total_Rev - Cost of Goods Sold - Operating Expenses

Return on Capital = EBIT / ( Net Fixed Assests + Working Capital)

'''

