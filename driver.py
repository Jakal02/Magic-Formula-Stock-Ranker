from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

#REQUIRES: None
#MODIFIES: NONE
#RETURNS:  Selenium chrome webdriver object with modified settings for optimal use
def init_browser(no_window=True):
    op = webdriver.ChromeOptions()
    op.add_argument('log-level=3') # prevents lots of useless text
    if(no_window):
        op.add_argument('headless') # prevents browser from actually popping up
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=op)
    browser.implicitly_wait(2)
    return browser