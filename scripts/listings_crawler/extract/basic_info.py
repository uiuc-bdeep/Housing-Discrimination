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
sys.path.insert(1, '/home/ubuntu/Housing-Discrimination/scripts/listings_crawler/extract/')
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


def extract_basic_info(driver, d, off_market):
	"""Extract rental detail such as number bedrooms and bathrooms, Sqft, Type of Housing, Year Built, etc.
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	    off_market (int): 0 if the listing is on the market, otherwise it is off the market
	"""

	d["Phone_Number"] = get_phone_number(driver, off_market)
	
	if off_market:
		bed_bath_count = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split('\n')
	else:
		try:
			bed_bath_count = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split("\n")
		except:
			try:
				bed_bath_count = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split("\n")
			except:
				bed_bath_count = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div/ul').text.split("\n")

	bedroom = ""
	bathroom = ""

	for detail in bed_bath_count:
		if "bed" in detail.lower():
			bedroom = detail.rsplit(" ", 1)[0]
		elif "bath" in detail.lower():
			bathroom = detail.rsplit(" ", 2)[0]
		elif "day" in detail.lower():
			d["Days_On_Trulia"] = detail.split(" ")[0]
		elif "sqft" in detail.lower():
			d["Sqft"] = detail.split(" ")[0]
	
	split_min_max(bedroom, "Bedroom", d)
	split_min_max(bathroom, "Bathroom", d)

	property_detail = get_property_detail(driver, off_market)


	for s in property_detail:
		if "sqft" in s and "/sqft" not in s:
			d["Sqft"] = s.split(" ")[0]
			print("\t" + s)
		elif "Built" in s:
			d["Year"] = s.split(" ")[2]
			print("\t" + s)
		elif "Home" in s or "Apartment" in s or "Family" in s or "Townhouse" in s or "loft" in s.lower():
			d["Type"] = s
			print("\t" + s)
		elif "Days" in s:
			d["Days_On_Trulia"] = s.split(" ")[0]
			print("\t" + s)

def get_property_detail(driver, off_market):
	if not off_market:
		try:
			li_options = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[5]/ul').find_elements_by_tag_name("li")
		except:
			li_options = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/ul').find_elements_by_tag_name("li")
	else:
			li_options = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[8]/ul').find_elements_by_tag_name("li")
	property_detail = []
	for option in li_options:
		if str(option.text) != '':
			property_detail.append(str(option.text))
	return property_detail

def get_phone_number(driver, off_market):
	if off_market:
		print("\tNo Phone Number Available")
		return "NA"
	try:
		phone_number = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[4]/div[2]/div/div/div[1]/a/div/div[2]').text
		print("\tPhone Number: {}".format(phone_number))
		return phone_number
	except:
		print("\tNo Phone Number Available")
		return "NA"

def phone_to_int(number):
	return int(number[1:4] + number[6:9] + number[10:])
	
def split_min_max(room, room_type, d):
	room_max = room_type + "_max"
	room_min = room_type + "_min"
	if " - " in room:
                d[room_min] = room.split(" - ")[0]
                d[room_max] = room.split(" - ")[1]
		print("\t{}s: {} (min) - {} (max)".format(room_type, d[room_min], d[room_max]))
        elif "-" in room:
                d[room_min] = room.split("-")[0]
                d[room_max] = room.split("-")[1]
		print("\t{}s: {} (min) - {} (max)".format(room_type, d[room_min], d[room_max]))
        elif room != "":
                d[room_min] = room[0]
                d[room_max] = room[0]
		print("\t{}s: {}".format(room_type, d[room_min]))
        else:
                d[room_min] = "NA"
                d[room_max] = "NA"
		print("\t{}s Not Available".format(room_type))

