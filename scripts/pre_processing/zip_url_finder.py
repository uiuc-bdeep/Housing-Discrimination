import re
import os
import csv 
import sys
import math
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

root = '/home/ubuntu/Housing-Discrimination/'


ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip/'#3_beds/2_baths/'
ZIP_URL_PAGE = '_p'

# read in zip code csv file 
if len(sys.argv) != 3 and len(sys.argv) != 4: 
	print('-------------------------------------------------')
	print('REQUIRED ARGUMENTS:')
	print('python zip_url_finder.py <csv file> <round_num> <zip_page_start (Default = 0)>')
	print('-------------------------------------------------')
	exit()

zip_csv     = sys.argv[1]
round_num   = sys.argv[2]
zip_start = 0
if len(sys.argv) == 4:
	zip_start   = int(sys.argv[3])
print("Starting from index {}".format(zip_start)) 
dest = '/home/ubuntu/Housing-Discrimination/rounds/round_' + round_num + '/round_' + round_num + '_urls.csv'
df_zip    = pd.read_csv(zip_csv) 
zip_list =  list(df_zip['zip_codes'].values.flatten())

options = Options()
options.add_argument("--headless")
fp = webdriver.FirefoxProfile()
#fp.set_preference("general.useragent.override", UserAgent().random)
fp.update_preferences()
driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options,
                                                        capabilities = webdriver.DesiredCapabilities.FIREFOX,
                                                        executable_path = '/usr/bin/geckodriver')
#driver   = webdriver.Firefox(executable_path='/usr/bin/geckodriver')
#driver.set_page_load_timeout(30) # set a time out for 30 secons
driver.maximize_window()
display  = Display(visible=0, size=(1024, 768)) # start display
display.start() # start the display

listings_all = []
with open(dest, "w") as f:
	writer = csv.writer(f)
	writer.writerow(["URL"])
	for i in range(0,len(zip_list)):
		if zip_start != 0: 
			zip_url = ZIP_URL_PRE + str(zip_list[i]) + ZIP_URL_SUF + '/' + str(zip_start) + ZIP_URL_PAGE 
			counter = zip_start
		else: 
			zip_url = ZIP_URL_PRE + str(zip_list[i]) + ZIP_URL_SUF 
			counter      = 0
		driver.get(zip_url)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		num_listings = list(set(re.findall(r'\w*[0-9]* rentals? available on Trulia',driver.page_source)))
		print('Page Number: ' + str(counter))
		num_pages    = 0
		if num_listings:
			num_pages    = math.ceil(float((num_listings[0].split(' ')[0]))/30)

		print('=======================================================================================')
		print(str(i) + '. Scraping ' + str(zip_list[i]) + ' with ' + str(num_pages) + ' pages')
		while counter < num_pages: 
			print('Page Number: ' + str(counter))
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			listings_on_page = []

			next_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,'#resultsColumn > div > div.resultsColumn > div.backgroundControls > div.backgroundBasic > div.paginationContainer.pls.mtl.ptl.mbm > div:nth-child(1) > a > i'))
			next_handle = wait_and_get(driver, next_cond, 15)

			listings_on_page = list(set(re.findall(r'\w*href="\W[a-z]\W[a-z][a-z][\w|\W]*?"',driver.page_source)))

			listings_on_page = [listing.replace('href="','https://www.trulia.com').replace('"','') for listing in listings_on_page]

			listings_on_page = [page for page in listings_on_page if page not in listings_all]
			listings_all = (listings_all) + listings_on_page
			listings_on_page = [[page] for page in listings_on_page]
			writer.writerows(listings_on_page)
			#print(listings_on_page)
			print('------------------------------------------------------------')
			print('Length of listings on page: ' + str(len(listings_on_page)))
			print('Length of listings        : ' + str(len(listings_all)))
			counter += 1
			if counter < num_pages:
				driver.get(zip_url+str(counter) + '_p')
				sleep(5)

			


driver.quit()
display.stop()

listings_all = list(set(listings_all))
listings_all  = pd.Series(listings_all)
df_listings   = pd.DataFrame()
df_listings['urls'] = listings_all
print(df_listings)

