import re
import os
import csv 
import sys
import pandas as pd 
from time import sleep 
from selenium import webdriver
from pyvirtualdisplay import Display 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def wait_and_get(browser, cond, maxtime): 
	flag = True

	while flag:
		try: 
			ret = WebDriverWait(browser, maxtime).until(cond)
			sleep(2)
			ret = WebDriverWait(browser, maxtime).until(cond)
			flag = False
			return ret
		except TimeoutException:
			#print("Time out")
			flag = False
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True
			if not flag:
				try:
					browser.find_elements_by_id("searchID").click()
					flag = True
				except:
					#print("Time out without pop-ups. Exit.")
					return 0

		except ElementNotVisibleException:
			print("Element Not Visible, presumptuously experienced pop-ups")
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True

root = '~/Racial Discrimination Project/stores'


ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip/3_beds/2_baths/'

# read in zip code csv file 
if len(sys.argv) !=5: 
	print('-------------------------------------------------')
	print('REQUIRED ARGUMENTS:')
	print('python zip_url_finder.py <csv file> <round_num> <city path> <state>')
	print('example: python zip_url_finder.py ~/project_files/houston/houston_zips 10 houston tx')
	print('-------------------------------------------------')
	exit()

zip_csv     = sys.argv[1]
round_num   = sys.argv[2]
round_city  = sys.argv[3]
round_state = sys.argv[4]

df_zip    = pd.read_csv(zip_csv) 
zip_list =  df_zip['zip_codes'].values

driver   = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
driver.set_page_load_timeout(30) # set a time out for 30 secons
driver.maximize_window()
display  = Display(visible=0, size=(1024, 768)) # start display
display.start() # start the display
listings_all = []
for zip_ in zip_list:
	zip_url = ZIP_URL_PRE + str(zip_) + ZIP_URL_SUF 
	driver.get(zip_url)
	while True: 
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		listings_on_page = []

		next_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,'#resultsColumn > div > div.resultsColumn > div.backgroundControls > div.backgroundBasic > div.paginationContainer.pls.mtl.ptl.mbm > div:nth-child(1) > a:nth-child(8) > i'))

		listings_on_page = list(set(re.findall(r'\w*href="\Wp\Wtx[\w|\W]*?"',driver.page_source)))
		listings_on_page = [listing for listing in listings_on_page if 'atlanta' not in listing]
		listings_on_page = [listing.replace('href="','') for listing in listings_on_page]

		listings_all = (listings_all) + listings_on_page

		print('=======================================================================================')
		print(listings_on_page)
		print('Length of listings on page: ' + str(len(listings_on_page)))
		print('Length of listings        : ' + str(len(listings_all)))

		next_handle = wait_and_get(driver, next_cond, 15)
		if next_handle == 0: 
			break
		else:
			next_handle.click()

driver.quit()
display.stop()

listings_all = list(set(listings_all))
listings_all  = pd.Series(listings_all)
df_listings   = pd.DataFrame()
df_listings['urls'] = listings_all
print(df_listings)
dest = root + round_city + '_data/' + 'round_' + round_num + '/' + round_city + '_' + round_state + '_' +'round_' + round_num + '_' + 'rental_urls.csv'
if os.path.isfile(dest) == False:
	open(dest, 'a').close()  
df_listings.to_csv(dest,'w' ,index = False)
