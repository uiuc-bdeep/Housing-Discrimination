import os
import sys
import os.path
import csv
import datetime
import psutil
import random
import json
import pandas as pd
import numpy as np
from sys import exit
from time import sleep
from re import sub
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.proxy import Proxy

from save_to_file import save_rental
from ejscreen.ejscreen import handle_ejscreen_input, extract_pollution
from extract.extract_data import check_off_market
from util.util import start_firefox, restart
from extract import shop, school, crime, basic_info as info

trulia = "https://www.trulia.com"
geckodriver_path = '/usr/bin/geckodriver'
adblock_path = "/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi"
uBlock_path = "/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi"

if len(sys.argv) != 5:
    print("Include start point, end point, destination, and debug (0 or 1) as arguments")
    exit()

def update_row(idx, destination):
    url = rentals["URL"][idx]
    print(idx, url)
    result = open_page(url)
    if result == 0:
        is_off_market = check_off_market(driver)
        if not is_off_market:
            print("On the market")
        update_basic_info(idx, is_off_market)
        update_crime(idx, is_off_market)
        update_school(idx, is_off_market)
        update_shop_eat(idx, is_off_market)
        rentals.to_csv(destination, index=False)
    finish_listing(driver, idx)

def update_basic_info(idx, off_market):
	print("Updating basic info")
	d = {}
	info.extract_basic_info(driver, d, off_market)
	update_rental_file(idx, d)
        return 1

def update_crime(idx, off_market):
	print("Updating Crime Data")
	d = {}
	crime.extract_crime(driver, d, off_market)
	update_rental_file(idx, d)
	return 0
            
def update_school(idx, off_market):
	print("Updating School Data")
	d = {}
	school.extract_school(driver, d, off_market)
	update_rental_file(idx, d)
	return 0

def school_check(idx):
	fields = ["Elementary_School_Count", "Middle_School_Count", "High_School_Count"]
	for f in fields:
		if rentals[f][idx] == -1:
			return False
	return True

def update_shop_eat(idx, off_market):
	print("Updating Shop & Eat")
	d = {}	
	shop.extract_shop(driver, d, off_market)
	update_rental_file(idx, d)  
	return 0

def update_rental_file(idx, d):
	for key in d.keys():
		#if isinstance(d[key], basestring):
		rentals.at[idx, key] = d[key]
		#else:
		#	rentals.at[idx, key] = d[key]

def open_page(url):
    driver.delete_all_cookies()
    d = {}
    driver.get(url)
    print(driver.title)
    sleep(3)
    if "Real Estate, " in driver.title or "Not Found" in driver.title:
        print ("404 in trulia")
        return 1
    elif "Trulia" in driver.title:
        print ("Successfully loaded URL")
        return 0
    else:
        print ("Being blocked from accessing Trulia. Restarting...")
        driver.quit()
        restart("logfile", debug, start)
        return 1

def finish_listing(driver, idx):
    with open("logfile", "ab") as log:
        filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
        filewriter.writerow([idx])

    #driver.close()
    driver.switch_to_window(driver.window_handles[0])
    sleep(random.randint(10,40))

def start_driver():
    print("Starting Driver")
    driver = start_firefox(trulia, geckodriver_path, adblock_path, uBlock_path)
    sleep(5)

    try:
        driver.switch_to_window(driver.window_handles[1])
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        return driver
    except:
        print ("Switching window failed??")
        driver.quit()
        restart("logfile", debug, start)

rentals_path = "/home/ubuntu/Housing-Discrimination/rounds/round_1/round_1_rentals.csv"
start = int(sys.argv[1])
end = int(sys.argv[2])
destination = sys.argv[3]
debug = int(sys.argv[4])
rentals = pd.read_csv(rentals_path)
if end > rentals.shape[0]:
    end = rentals.shape[0]

rentals['Sqft'] = rentals['Sqft'].astype(str)
rentals['Type'] = rentals['Type'].astype(str)
rentals['Phone_Number'] = rentals['Phone_Number'].astype(str)
rentals['Crime_Relative'] = rentals['Crime_Relative'].astype(str)
rentals['Year'] = rentals['Year'].astype(str)
rentals['Bedroom_min'] = rentals['Bedroom_min'].astype(str)
rentals['Bedroom_max'] = rentals['Bedroom_max'].astype(str)
rentals['Bathroom_min'] = rentals['Bathroom_min'].astype(str)
rentals['Bathroom_max'] = rentals['Bathroom_max'].astype(str)

print("Updating rentals file from {} to {}".format(start, end))
if debug == 1:
    print("DEBUG = TRUE")
driver = start_driver()
if driver != None:
    print("Driver Successfully Started")
for i in range(start, end):
    update_row(i, destination)


