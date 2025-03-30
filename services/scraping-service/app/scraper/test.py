from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.get( "https://groceries.morrisons.com/categories")

print(driver.page_source)
driver.quit()

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service

# service = Service("C:\\chromedriver\\chromedriver.exe")
# driver = webdriver.Chrome(service=service)
# driver.get("https://www.google.com")
# print(driver.title)  # Should print "Google"
# driver.quit()
