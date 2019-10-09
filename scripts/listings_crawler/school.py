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

def extract_school(driver, d, off_market):
	xpath_list = []
	if not off_market:
		xpath_list = [('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div'), ('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[2]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[2]/div')]
	else:
		xpath_list = [('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div'),('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div/div/div[2]/div')] 
	result = find_button(driver, xpath_list)
	if result == 0:
		print("\tSchool page found")
	else:
		print("\tCould NOT find school page")
		set_NA(d)
		sleep(1)
		driver.save_screenshot("missing/mising-school.png")
		return -1
	sleep(3)
	d["Elementary_School_Count"], d["Elementary_School_Avg_Score"] = count_schools(driver, '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[1]/div/button')
	d["Middle_School_Count"], d["Middle_School_Avg_Score"] = count_schools(driver, '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/div/button')
	d["High_School_Count"], d["High_School_Avg_Score"] = count_schools(driver, '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[3]/div/button') 
	print("\t{} Elementary Schools | Score = {}".format(d["Elementary_School_Count"], d["Elementary_School_Avg_Score"]))
	print("\t{} Middle Schools     | Score = {}".format(d["Middle_School_Count"], d["Middle_School_Avg_Score"]))
	print("\t{} High Schools       | Score = {}".format(d["High_School_Count"], d["High_School_Avg_Score"]))
	close_page(driver)
	return 0

def close_page(driver):
	driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[2]/div[2]').click()
	sleep(1)
	
def count_schools(driver, xpath):
	try:
		driver.find_element_by_xpath(xpath).click()
		schools = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")
		max_count = len(schools) - 1
		count = 0
		total = 0
		for i in range(1, 1 + max_count):
			try:
				total += int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
				count += 1
			except:
				break
		if count == 0:
			return 0, 0
		avg = float(total) / count
        	return count, round(avg, 3)
	except:
		return -1, -1

def find_button(driver, xpath_list):
	for pair in xpath_list:
		text, button = pair
		try:
			text = driver.find_element_by_xpath(text).text
			if text == "Schools":
				driver.find_element_by_xpath(button).click()
				return 0
		except:
			break
	return -1

def set_NA(d):
	d["Elementary_School_Count"] = -1
	d["Elementary_School_Avg_Score"] = -1
	d["Middle_School_Count"] = -1
	d["Middle_School_Avg_Score"] = -1
	d["High_School_Count"] = -1
	d["High_School_Avg_Score"] = -1
	print("\tUnable to find any school info - setting to NA")
