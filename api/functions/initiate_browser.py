## Initiate ChromeDriver (WebDriver) for the 1st time
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(chrome_options=chrome_options)
hyperlinks_dynamic = False
dynamic_links = []
dynamic_texts = []

## Reset ChromeDriver function    
def reset_browser():
    ''' Browser will be reset if an exception occurs when running di WebDriver 
        and will be reset after one crawling job finished '''

    global driver
    global hyperlinks_dynamic
    global dynamic_links
    global dynamic_texts

    ## Quit driver
    driver.close()
    driver.quit()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(chrome_options=chrome_options)    
    hyperlinks_dynamic = False
    dynamic_links = []
    dynamic_texts = []