import driver
import password
import pandas as pd

# REQUIRES: None
# MODIFIES: None
# RETURNS: pd dataframe: Columns = [ticker, mkt cap (mil)]
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
    return pd.DataFrame(tickers[1:],columns=tickers[0])

def print_tickers(tickers):
    i = 0
    for tick in tickers:
        if(i==0):
            i = 1
            continue
        print(tick[0],end="")
        
        if(i < len(tickers)-1):
            print(",",end="")
        i = i +1
    print("")
    return

#REQUIRES: tickers is a pd dataframe with a column of tickers
#MODIFIES: None
#RETURNS: a modified pd dataframe with column of num_gurus added

def get_num_gurus(tickers):
    tickers_list = tickers["Ticker"]
    url_base = "https://www.dataroma.com/m/stock.php?sym="
    list_ownership= pd.DataFrame(columns=["Ticker","Gurus"])
    num_tick = len(tickers_list)
    i=1
    for ticker in tickers_list:
        print("Getting Guru info on stock",i,"of",num_tick)
        try:
            data_table = pd.read_html(url_base+ticker)[0]
            ownership_count = int(data_table[1][2])
        except:
            print("Webpage Error for",ticker)
            ownershp_count=0
        list_ownership = list_ownership.append({"Ticker":ticker,"Gurus":ownership_count},ignore_index=True)
        i=i+1
    return tickers.merge(list_ownership)

#REQUIRES: tickers is a pd dataframe with a column of tickers
#MODIFIES: None
#RETURNS: a modified pd dataframe with column of when the most revent VIC writeup was
def get_vic_writeup(tickers):
    # MUST log in to VIC so results show up
    browser = driver.init_browser(no_window=False)
    __log_in_vic(browser)

    tickers_list = tickers["Ticker"]
    list_writeup = pd.DataFrame(columns=["Ticker","VIC"])

    num_tick = len(tickers_list)
    i=1
    for ticker in tickers_list:
        print("Getting Writeup info on stock",i,"of",num_tick)
        try:
            data_table = __get_writeups(ticker,browser)
            writeup = __find_recent_writeup(data_table,ticker)
            if data_table.empty:
                print("No writeup for",ticker)
                writeup = 'None'
        except:
                print("Webpage Error for",ticker)
                writeup = 'None'
        list_writeup= list_writeup.append({"Ticker":ticker,"VIC":writeup},ignore_index=True)
        i=i+1
    browser.close()
    return tickers.merge(list_writeup)

#REQUIRES: tickers is a pd dataframe with a column of tickers
#MODIFIES: None
#RETURNS:  a modified pd dataframe with column of
def get_insider_ownership(tickers):
    browser = driver.init_browser()

    tickers_list = tickers["Ticker"]
    list_ins = pd.DataFrame(columns=["Ticker","Insider Ownership","6 Month Change"])
    num_tick = len(tickers_list)
    i=1
    for ticker in tickers_list:
        print("Getting insider info on stock",i,"of",num_tick)
        try:
            ownership,change = __get_insider_info(ticker,browser)
        except:
            print("Webpage Error for",ticker)
            ownership,change = 0,0
        list_ins = list_ins.append({"Ticker":ticker,"Insider Ownership":ownership,"6 Month Change":change},ignore_index=True)
        i=i+1
    browser.close()
    return tickers.merge(list_ins)

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
#RETURNS: Pandas Dataframe Columns = [ticker, mkt cap (mil)]
def __screen_data(browser):
    browser.find_element_by_id('stocks').click()
    before_XPath = "//*[@id='tableform']/table/tbody/tr["
    aftertd_XPath = "]/td["
    aftertr_XPath = "]"
    rows = len(browser.find_elements_by_xpath("//*[@id='tableform']/table/tbody/tr"))
    data = [["Ticker","Mkt Cap"]]
    for t_row in range(1, (rows + 1)):
        #name_path = before_XPath + str(t_row) + aftertd_XPath + "1" + aftertr_XPath
        ticker_path = before_XPath + str(t_row) + aftertd_XPath + "2" + aftertr_XPath
        mkt_path = before_XPath + str(t_row) + aftertd_XPath + "3" + aftertr_XPath
        #company_name = browser.find_element_by_xpath(name_path).text
        ticker = browser.find_element_by_xpath(ticker_path).text
        mkt_cap = float(browser.find_element_by_xpath(mkt_path).text.replace(',',''))
        data.append( [ticker,mkt_cap] )
    
    return data

#########################################################################
#########################################################################

#REQUIRES: Selenium browser object
#MODIFIES: The webpage
#RETURNS: Nothing
def __log_in_vic(browser):
    url = "https://www.valueinvestorsclub.com/login"
    browser.get(url)
    user,passw = password.get_cred(type="vic")
    browser.find_element_by_name("login[login_name]").send_keys(user)
    browser.find_element_by_name("login[password]").send_keys(passw)
    browser.find_element_by_id("login_btn").click()
    return

#REQUIRES: The ticker of a company, as a string
#MODFIES: None
#RETURNS: pd dataframe of all writeups that have the ticker as a substring in the name
#         empty pd dataframe if none found
def __get_writeups(ticker,browser):
    browser.get("https://www.valueinvestorsclub.com/search/"+ticker)
    source = str(browser.page_source)
    data_table = pd.read_html(source)[0]
    if 'MEMBER' in data_table.columns:
        data_table = pd.read_html(source)[1]
        
    if data_table.columns[0].find("KEYWORDS IN DESCRIPTION") != -1:
        data_table = pd.DataFrame()
    return data_table

#REQUIRES: pd Dataframe of shape: x rows 1 column pulled from valueinvestorsclub.com
#MODIFIES: None
#RETURNS: String containing date of most recent relevant writeup
def __find_recent_writeup(data,ticker):
    col = "COMPANY  AUTHOR  PUBLISHED DATE"
    for item in data[col]:
            lst = item.split("  ")
            key = lst[0]
            if __is_right_key(key,ticker):
                return lst[-1]
    return "None"

#REQUIRES: ticker string, and string of company title as attached to a vic writeup
#MODIFIES: None
#RETURNS: True or False based on if the key string refers to the ticker
def __is_right_key(key,ticker):
    last = key.split(" ")[-1]
    if last.upper() == ticker:
        return True
    ticker = "("+ticker+")"
    if last == ticker:
        return True
    if ticker.find(last) == 0:
        return True
    return False

#########################################################################
#########################################################################

def __get_insider_info(ticker,browser):
    browser.get("https://finviz.com/quote.ashx?t="+ticker)
    source = browser.find_element_by_xpath("//*[@class='snapshot-table2']//parent::div").get_attribute('innerHTML')
    data_table = pd.read_html(str(source))[3][7][0:2]
    return_pkg = []
    for data in data_table:
        data = float(data.replace("%",""))
        return_pkg.append(data)
    return return_pkg

########## Test Area ###########


