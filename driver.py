from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#REQUIRES: None
#MODIFIES: NONE
#RETURNS:  Selenium chrome webdriver object with modified settings for optimal use
def init_browser(no_window=True):
    op = webdriver.ChromeOptions()
    op.add_argument('log-level=3') # prevents lots of useless text
    #op.add_experimental_option("excludeSwitches", ["enable-automation"])
    #op.add_experimental_option('useAutomationExtension', False)
    #op.add_argument("--disable-blink-features=AutomationControlled")
    op.add_argument("user-agent=whatever you want")
    if(no_window):
        op.add_argument('headless') # prevents browser from actually popping up
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=op)
    browser.implicitly_wait(2)
    return browser

#REQUIRES: Selenium Webdriver obj on a webpage
#          Xpath of object wanted to be grabbed
#MODIFIES: Nothing
#RETURNS: the element wanted to be grabbed
def web_wait_grab(browser, xpath):
    elem = WebDriverWait(browser,10)
    data = elem.until(lambda browser: browser.find_element_by_xpath(xpath) )
    #data = elem.until(EC.presence_of_element_located((By.XPATH,xpath)) )
    return data