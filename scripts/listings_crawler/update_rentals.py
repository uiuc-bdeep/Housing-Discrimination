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
from extract.extract_data import extract_rental, check_off_market, extract_commute
import extract.rental.extract_rental_data as rental
import extract.sold_rental.extract_sold_rental_data as sold
from util.util import start_firefox, restart

trulia = "https://www.trulia.com"
geckodriver_path = '/usr/bin/geckodriver'
adblock_path = "/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi"
uBlock_path = "/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi"

if len(sys.argv) != 5:
    print("Include rentals file, start point, end point, and debug (0 or 1) as arguments")
    exit()

def update_row(idx):
    url = rentals["URL"][idx]
    print(idx, url)
    result = open_page(url)
    if result == 0:
        is_off_market = check_off_market(driver)
        if is_off_market:
            print("Off market")
        else:
            print("On the market")
        num_failed = 0
        num_failed += update_basic_info(idx, is_off_market)
        num_failed += update_crime(idx, is_off_market)
        num_failed += update_school(idx, is_off_market)
        num_failed += update_commute(idx, is_off_market)
        #shop & eat
        #rentals.to_csv('../../rounds/round_2/round_2_rentals_1_updated.csv', index=False)
        print("Finished")

def update_basic_info(idx, off_market):
    print("Updating basic info")
    d = {}
    try:
        if not off_market:
            rental.extract_rental_detail(driver, d)
        else:
            sold.extract_sold_rental_detail(driver, d)
        print("Successfully updated basic info:")
        print(d)
        for key in d.keys():
            if key == "days":
                rentals.at[idx, 'Days_on_Trulia'] = d['days']
            elif key == 'type':
                rentals.at[idx, key.capitalize()] = str(d[key])
            else:
                rentals.at[idx, key.capitalize()] = int(d[key])
        return 0
    except:
        print("Unable to extract basic info")
        return 1

def update_crime(idx, off_market):
    if rentals['Assault'][idx] != 'NA' and not pd.isnull(rentals['Assault'][idx]):
        print("No need to update crime")
        return 0
    print("Updating crime data")
    d = {}
    try:
        if not off_market:
            rental.extract_rental_crime(driver, d)
        else:
            sold.extract_sold_rental_crime(driver, d)
        print("Successfully extracted crime data:")
        print(d)
        #write to rentals
        return 0
    except:
        print("Unable to extract crime data")
        return 1
            
def update_school(idx, off_market):
    if not pd.isnull(rentals['Elementary_School_Avg_Score'][idx]) and int(rentals['Elementary_School_Avg_Score'][idx]) != 0:
        print("No need to update school")
        return 0
    print("Updating school data")
    d = {}
    try:
        if not off_market:
            rental.extract_rental_school(driver, d)
        else:
            sold.extract_sold_rental_school(driver, d)
        print("Successfully extracted school data:")
        print(d)
        rentals.at[idx, 'Elementary_School_Count'] = d['elementary_school_count']
        rentals.at[idx, 'Elementary_School_Avg_Score'] = d['elementary_school_average_score']
        rentals.at[idx, 'Middle_School_Count'] = d['middle_school_count']
        rentals.at[idx, 'Middle_School_Avg_Score'] = d['middle_school_average_score']
        rentals.at[idx, 'High_School_Count'] = d['high_school_count']
        rentals.at[idx, 'High_School_Avg_Score'] = d['high_school_average_score']
        return 0
    except:
        print("Unable to extract school data")
        return 1

def update_commute(idx, off_market):
    if not pd.isnull(rentals['Driving'][idx]) and rentals['Driving'][idx] != 'NA':
        print("No need to update commute")
        return 0
    print("Updating commute data")
    d = {}
    extract_commute(driver, d)
    print("Successfully extraced commute data:")
    print(d)
    #update rentals df
    return 0
    #except:
        #print("Unable to update commute data")
        #return 1


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

def finish_listing(d, idx):
    #save_rental(d, urls[i], output_file) FIX THIS

    with open("logfile", "ab") as log:
        filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
        filewriter.writerow([i])

    driver.close()
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

rentals_path = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])
debug = int(sys.argv[4])
rentals = pd.read_csv(rentals_path)
if end > rentals.shape[0]:
    end = rentals.shape[0]
print("Updating rentals file from {} to {}".format(start, end))
if(debug == 1):
    print("DEBUG = true")
driver = start_driver()
if driver != None:
    print("Driver Successfully Started")
for i in range(0, 1):
    update_row(i)


