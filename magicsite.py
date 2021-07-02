import driver
import password

# REQUIRES: None
# MODIFIES: None
# RETURNS: 2D array: row = [Ticker, mkt cap(millions)]
def grab_tickers():
    # Log in to Screener
    browser = driver.init_browser()
    __access_magic_site(browser)
    __log_in_magic_site(browser)

    # Set up screener
    stock_num = __get_num_stocks()
    mkt_cap_min = __get_min_mkt_cap()
    __enter_num_stocks(browser, stock_num)
    __enter_min_mkt_cap(browser, mkt_cap_min)

    # Run Screener
    tickers = __screen_data(browser)
    browser.close()
    return tickers

###                   ###
### Private Functions ###
###                   ###


#REQUIRES: Selenium Webdriver object
#MODIFIES: Sends driver to website below, 
#          which is the login page for the magic formula screener
#RETURNS: None
def __access_magic_site(browser):
    browser.get('https://www.magicformulainvesting.com/Account/LogOn')


#REQUIRES: Selenium Webdriver object at login page of mfi.com
#MODIFIES: Logs webdriver object in to the website, setting it in front of the screener
#RETURNS: Nothing
def __log_in_magic_site(browser):
    # Get credentials
    user,passw = password.get_cred()
    #interact with website to login
    browser.find_element_by_name("Email").send_keys(user)
    browser.find_element_by_name("Password").send_keys(passw)
    browser.find_element_by_id('login').click()
    return

#REQUIRES: None
#MODIFIES: None
#RETURNS: # of stocks user wants to use for mfi screening
def __get_num_stocks():
    while True:
        try:
            num_stocks = int(input('Would you like to see 30 or 50 stocks? '))
            if(num_stocks != 30 and num_stocks != 50):
                print('Please enter 30 or 50')
                continue
            break
        except ValueError:
            print('Please enter a whole number')
    return num_stocks

#REQUIRES: None
#MODIFIES: None
#RETURNS: minimum mkt cap(in millions) user wants to use for mfi screening
def __get_min_mkt_cap():
    while True:
        try:
            min = int(input('In millions, Select the minimum market cap: '))
            if(min < 50 or min > 1000000):
                print('Please enter a value between 50 and 100,000')
                continue
            break
        except ValueError:
            print('Please enter a whole number')
    return min

#REQUIRES: Selenium Webdriver obj at mfi.com screening page
#MODIFIES: Selects either 30 or 50 as # stocks to screen
#RETURNS: None
def __enter_num_stocks(browser, stock_num):
    if(stock_num == 50):
        browser.find_elements_by_id("Select30")[1].click()
    else:
        browser.find_element_by_id("Select30").click()
    return

#REQUIRES: Selenium Webdriver obj at mfi.com screening page
#MODIFIES: Enters the min mkt cap(in millions) the user wants to the website
#RETURNS: None
def __enter_min_mkt_cap(browser,mkt_min):
    mkt_cap_box = browser.find_element_by_name("MinimumMarketCap")
    browser.execute_script('arguments[0].value = "";', mkt_cap_box)
    mkt_cap_box.send_keys(mkt_min)
    return


#REQUIRES: Selenium Webdriver obj at mfi.com screening page with appropriate
#          user preferences entered
#MODIFIES: Clicks the button to run the screener
#RETURNS: 2D array: row = [Ticker, mkt cap(millions)]
def __screen_data(browser):
    browser.find_element_by_id('stocks').click()
    before_XPath = "//*[@id='tableform']/table/tbody/tr["
    aftertd_XPath = "]/td["
    aftertr_XPath = "]"
    rows = len(browser.find_elements_by_xpath("//*[@id='tableform']/table/tbody/tr"))
    data = []
    for t_row in range(1, (rows + 1)):
        #name_path = before_XPath + str(t_row) + aftertd_XPath + "1" + aftertr_XPath
        ticker_path = before_XPath + str(t_row) + aftertd_XPath + "2" + aftertr_XPath
        mkt_path = before_XPath + str(t_row) + aftertd_XPath + "3" + aftertr_XPath
        #company_name = browser.find_element_by_xpath(name_path).text
        ticker = browser.find_element_by_xpath(ticker_path).text
        mkt_cap = float(browser.find_element_by_xpath(mkt_path).text.replace(',',''))
        data.append( [ticker,mkt_cap] )
    return data
