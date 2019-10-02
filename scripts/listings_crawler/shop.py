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


def extract_rental_shop_eat(driver, d):
	"""Extract Shop and Eat scores from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""
	#try:
		#try:
	driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div').click()
	print("Clicked shop") 
		#except:
			#driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[2]/button').click() #scroll it into view
				#ERROR: This button ^ is not clickable because something obscures it
			#driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div/div').click()

		#driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div/button').click() #restaurant button
		#print("Clicked restaraunt")
		#restaurant_counter = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul')
		#restaurants = len(restarurant_counter.find_elements_by_tag_name("li"))
		#d["restaurant"] = restaurant
		#print(d)
		#return
	#except:
		#print("new shop method unsuccessful")
	try:
		try:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[7]").click()
			print("change to shop and eat")
			restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
			#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]
		except:
			try:
				driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[6]").click()
				print("shop and eat button")
				restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
				#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]
			except:
				driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div').click()
				print("shop & eat")
				restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]

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
