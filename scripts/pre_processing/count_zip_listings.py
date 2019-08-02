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

root = '/home/ubuntu/Housing-Discrimination/rounds/'


ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip'

# read in zip code csv file 
if len(sys.argv) != 3: 
	print('-------------------------------------------------')
	print('REQUIRED ARGUMENTS:')
	print('python zip_url_finder.py <csv file> <row index>')
	print('-------------------------------------------------')
	exit()

zip_csv     = sys.argv[1]
row_index   = int(sys.argv[2])

df_zip    = pd.read_csv(zip_csv) 
zip_list =  df_zip['zip_codes'].values

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
stop = 0

dest = '/home/ubuntu/Housing-Discrimination/rounds/round_16/num_listings_per_zip.csv'
with open(dest, "a") as f:
	writer = csv.writer(f)

	if row_index == 0:
		writer.writerow(['zip_codes', 'num_listings'])
	for i in range(row_index,len(zip_list)):
		print('===========================================================================')
		zip_url = ZIP_URL_PRE + str(zip_list[i]) + ZIP_URL_SUF 
		driver.get(zip_url)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		if driver.title == 'Access to this page has been denied.': 
			try_conter = 0 
			print(driver.title)
			while driver.title == 'Access to this page has been denied.': 
				sleep(30)
				driver.get(zip_url)
				if try_conter > 5: 
					stop = 1
					break
				try_conter += 1
		if stop == 1: 
			break
		num_listings  = list(set(re.findall(r'\w*[0-9]* rentals? available on Trulia',driver.page_source)))
		if num_listings: 
			num_listings = int(num_listings[0].split(' ')[0])
		else: 
			num_listings = 0
		print(str(i) + '. ' + 'zip: ' + str(zip_list[i]) + ' ' + 'num_listings: ' + str(num_listings))
		writer.writerow([zip_list[i], num_listings])

	driver.quit()
	display.stop()
    
