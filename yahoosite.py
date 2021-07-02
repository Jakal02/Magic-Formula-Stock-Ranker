import driver
import time

#REQUIRES: 2D list of stocks: row = [Ticker, mkt_cap(in millions)]
#MODIFIES: None
#RETURNS: Additional list: row = [Ticker, ROC, Earnings Yield]
def find_roc_and_eyield(tickers):
    data = []
    for i in range(0,2):
    #for i in range(0,len(tickers)):
        print('\nWorking on stock',i+1,'of',len(tickers))
        ticker = tickers[i][0]
        mkt_cap = tickers[i][1]
        roc,eyield = __scrape_roc_and_eyield(ticker,mkt_cap)
        data.append([ticker,roc,eyield])

    return data



###                   ###
### Private Functions ###
###                   ###

# REQUIRES: Browser on a Yahoo finance stock website
def __nav_to_income(browser):
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[1]/div/a[1]/div').click()
    time.sleep(2)
    __expand_sheet(browser)
    return

# REQUIRES: Browser on a Yahoo finance stock website
def __nav_to_quarterly(browser):
    browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
    time.sleep(2)
    return


def __scrape_roc_and_eyield(ticker_name, mkt):
    browser = driver.init_browser()
    link = 'https://finance.yahoo.com/quote/'+ticker_name+'/balance-sheet?p='+ticker_name
    browser.get(link)

    __nav_to_quarterly(browser)
    __expand_sheet(browser)

    mkt_cap = mkt * 1000 # TO ADD: 2nd Parameter of mkt_cap
    
    fixed_assets = __get_fixed_assets(browser) # Done
    work_cap = __get_working_cap(browser) # Done
    current_liab = __get_current_liabilities(browser) # Done
    long_debt = __get_long_debt(browser) # Done
    cash = __get_cash(browser) # Done

    __nav_to_income(browser)
    __nav_to_quarterly(browser)
    ebit = __get_ebit(browser) # Done

    total_debt = long_debt + current_liab
    ent_val = mkt_cap + total_debt - cash

    earn_yield = ebit / ent_val
    roc = ebit / (work_cap + fixed_assets)

    earn_yield = round(earn_yield*100,3)
    roc = round(roc * 100, 3)

    browser.close()
    return roc, earn_yield



def __get_ebit(browser):
    try:
        return __get_income_sheet_var(browser,"EBIT")
    except:
        total_rev = __get_total_rev(browser)
        cost_of_rev = __get_cost_of_rev(browser)
        op_expenses = __get_op_expenses(browser)
        return total_rev - cost_of_rev - op_expenses

def __get_total_rev(browser):
    return __get_income_sheet_var(browser,"Total Revenue")
def __get_cost_of_rev(browser):
    return __get_income_sheet_var(browser,"Cost of Revenue")
def __get_op_expenses(browser):
    return __get_income_sheet_var(browser,"Operating Expense")


def __get_long_debt(browser):
    long_debt = '0'
    try:
        long_debt = browser.find_element_by_xpath("//*[@title='Long Term Debt And Capital Lease Obligation']//parent::div//following-sibling::div[@data-test='fin-col']").text
    except:
        try:
            long_debt = browser.find_element_by_xpath("//*[@title='Total Non Current Liabilities Net Minority Interest']//parent::div//following-sibling::div[@data-test='fin-col']").text
        except:
            long_debt = '0'
    return __text_to_float(long_debt)

def __get_cash(browser):
    return __get_balance_sheet_var(browser, "Cash And Cash Equivalents")

def __get_working_cap(browser):
    try:
        return __get_balance_sheet_var(browser,"Working Capital")
    except:
        current_assets = __get_current_assets(browser)
        current_liabilities = __get_current_liabilities(browser)
        return current_assets - current_liabilities
    
def __get_current_assets(browser):
    return __get_balance_sheet_var(browser, "Current Assets")

def __get_current_liabilities(browser):
    return __get_balance_sheet_var(browser,"Current Liabilities")

def __get_fixed_assets(browser):
    accum = __get_accumulated_depreciation(browser)
    fixed_assets = __get_net_ppe(browser)

    return fixed_assets - accum

def __get_accumulated_depreciation(browser):
    return __get_balance_sheet_var(browser,'Accumulated Depreciation')
def __get_net_ppe(browser):
    return __get_balance_sheet_var(browser, 'Net PPE')


def __get_balance_sheet_var(browser, word):
    xpath = "//*[@title='"+word+"']//parent::div//following-sibling::div[@data-test='fin-col']"
    return __get_table_var(browser,xpath,word)

def __get_income_sheet_var(browser, word):
    xpath = "//*[@title='"+word+"']//parent::div[1]//following-sibling::div[@data-test='fin-col'][1]"
    return __get_table_var(browser,xpath,word)

def __get_table_var(browser,xpath,word):
    try:
        var = browser.find_elements_by_xpath(xpath)
        var= var[0].text
    except:
        print(word,"could not be found on the balance sheet")
    return __text_to_float(var)


def __expand_sheet(browser):
    expand = browser.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span')
    if(expand.text == 'Expand All'):
        button = browser.find_element_by_class_name('expandPf')
        browser.execute_script("arguments[0].click();", button)
    return

def __text_to_float(number):
    if number != "-":
        return float(number.replace(',',''))
    return 0




