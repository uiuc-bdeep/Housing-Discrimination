"""Summary
"""
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
sys.path.insert(1, '/home/ubuntu/Housing-Discrimination/scripts/listings_crawler/extract/sold_rental')
import extract_sold_rental_data as extract
from sys import exit
from time import sleep
from re import sub
from fake_useragent import UserAgent

#from pyvirtualdisplay import Display
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


def extract_shop(driver, d, off_market):
	# Must click on another link and then click on Shop & Eat
	xpath_list = []
	if not off_market:	# Listing is on the market
		xpath_list = ['//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[1]/div']
	else:			# Listing is off the market
		xpath_list = ['//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[1]/div']
	result = find_button(driver, xpath_list)
	if result == 0:
		print("\tShop Page Found")
	else:
		print("\tCould NOT find Shop page")
		set_NA(d)
		sleep(2)
		driver.save_screenshot("missing/missing-shop.png")
		return -1
	sleep(3)
	buttons = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div').find_elements_by_tag_name("div")
	for i in range(2, len(buttons) + 1):
                try:
		        button = '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div/div[{}]/div/button'.format(i)
		        count_shop(driver, button, d, i)
                except:
                        continue
	set_empty_fields(d)		
	# Currently on the shop page, extract all the info
	return 0
		
def count_shop(driver, button, d, i):
	sleep(3)
	driver.find_element_by_xpath(button).click()
	#text = driver.find_element)by_xpath(button).text
	text = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div/div[{}]/div/button/div'.format(i)).text.split(" ")[-1]
	count = len(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li"))
	print("\t{}: {}".format(text, count))
        d[text] = count

def find_button(driver, xpath_list):
	clicked = False
	for xpath in xpath_list:
		try:
			driver.find_element_by_xpath(xpath).click()
			clicked = True
			continue	
		except:
			break
	if not clicked:
		print("\tCan't click ANY buttons")
		return -1
	sleep(2)
	buttons = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[1]/div/div[1]/div').find_elements_by_tag_name("div")
	print("\tNumber of buttons = {}".format(len(buttons)))
	for i in range(1, len(buttons) + 1):
                try:
		        text = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[1]/div/div[1]/div/div[{}]/div/button'.format(i)).text
		        if text == "Shop & Eat":
			        driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[1]/div/div[1]/div/div[{}]/div/button'.format(i)).click()
			        return 0
                except:
                        continue
	print("\tCould not find Shop & Eat Button inside Data page")	
	return -1

def set_empty_fields(d):
	fields = ["Restaurants", "Groceries", "Nightlife", "Cafes", "Shopping", "Entertainment", "Fitness"]
	for key in fields:
		if key not in d.keys():
			print("\t{}: {}".format(key, 0))
			d[key] = 0
		

def restaurant_count(driver):
	try:
		driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div/button').click() #restaurant button
		print("\tClicked Restaraunt")
		restaurant_counter = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul')
		restaurants = len(restarurant_counter.find_elements_by_tag_name("li"))
		return restaurants
	except:
		print("\tCould not count restaurants")
		return "NA"

def count_shop_and_eat(driver, d):
	try:
		num_buttons = len(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div').find_elements_by_tag_name('div'))
		print("\tNum buttons found = ", num_buttons)
	except:
		print("\tCould not count buttons")

def extra():
	try:
		sleep(5)

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[2]").click()
		groceries = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[3]").click()
		nightlife = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[4]").click()
		cafe = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[5]").click()
		shopping = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[6]").click()
		entertainment = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[7]").click()
		beauty = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		driver.find_element_by_xpath("//*[@id='amenitiesTab']/div[2]/div/div[1]/div[1]/ul/li[8]").click()
		active_life = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

		d["restaurant"] = restaurant
		d["groceries"] = groceries
		d["nightlife"] = nightlife
		d["cafe"] = cafe
		d["shopping"] = shopping
		d["entertainment"] = entertainment
		d["beauty"] = beauty
		d["active_life"] = active_life

		print (restaurant, groceries, nightlife, cafe, shopping, entertainment, beauty, active_life)
	except:
		d["restaurant"] = "NA"
		d["groceries"] = "NA"
		d["nightlife"] = "NA"
		d["cafe"] = "NA"
		d["shopping"] = "NA"
		d["entertainment"] = "NA"
		d["beauty"] = "NA"
		d["active_life"] = "NA"
		print("shop and eat not available")
