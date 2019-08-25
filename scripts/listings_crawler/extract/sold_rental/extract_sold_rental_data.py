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

def extract_sold_rental_detail(driver, d):
	"""Extract rental detail such as number bedrooms and bathrooms, Sqft, Type of Housing, Year Built, etc.
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	try:
		detail = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/ul").text.split("\n")
	except:
		try:
			detail = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/ul").text.split("\n")
		except:
			try:
				detail = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/ul').text.split("\n")
									#'//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div/ul'
			except:
				try:
					detail = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split("\n")
				except:
					pass
		
	bedroom = ""
	bathroom = ""
	sqft = ""
	for p in detail:
		if "bed" in p.lower():
			bedroom = p
		elif "bath" in p.lower():
			bathroom = p
		elif "sqft" in p.lower():
			sqft = p.split(" ")[0]

	if " - " in bedroom:
		d["bedroom_min"] = bedroom.split(" - ")[0]
		d["bedroom_max"] = bedroom.split(" - ")[1]
	elif "-" in bedroom:
		d["bedroom_min"] = bedroom.split("-")[0]
		d["bedroom_max"] = bedroom.split("-")[1]
	elif bedroom != "":
		d["bedroom_min"] = bedroom.split(" ")[0]
		d["bedroom_max"] = bedroom.split(" ")[0]
	else:
		d["bedroom_min"] = "NA"
		d["bedroom_max"] = "NA"

	if " - " in bathroom:
		d["bathroom_min"] = bathroom.split(" - ")[0]
		d["bathroom_max"] = bathroom.split(" - ")[1]
	elif "-" in bathroom:
		d["bathroom_min"] = bathroom.split("-")[0]
		d["bathroom_max"] = bathroom.split("-")[1]
	elif bathroom != "":
		d["bathroom_min"] = bathroom.split(" ")[0]
		d["bathroom_max"] = bathroom.split(" ")[0]
	else:
		d["bathroom_min"] = "NA"
		d["bathroom_max"] = "NA"

	d["sqft"] = sqft

def extract_sold_rental_school(driver, d):
	"""Extract Assigned Schools score and get the average
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	try:
		info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button/div[2]").text
		button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button")
	except:
		try:
			info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button")
		except:
			try:
				info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]").text
				button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[2]")
			except:
				try:
					info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div/div[2]").text
					button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]")
				except:	
					info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]").text
					button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]")

	possible_xpath = ["//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button/div[2]", 
	"//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]"]

	buttons = ["//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button",
	"//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]"
	]

	for xpath, btn in zip(possible_xpath, buttons):
		try:
			info_text = driver.find_element_by_xpath(xpath).text
			if "school" in info_text.lower():
				button = driver.find_element_by_xpath(btn)
				break
		except:
			pass

	if "school" in info_text.lower():
		button.click()
	else:
		try:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button").click()
		except:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button").click()
	
	sleep(5)
	try:
		school = driver.find_element_by_xpath("//button[@data-id='ELEMENTARY']").click()
		try:
			scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			scores = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		school_count = len(scores) - 1
		score = 0
		for s in scores[:-1]:
			try:
				score += int(s.text.split("\n")[0])
			except:
				school_count -= 1
		d["elementary_school_count"] = school_count
		d["elementary_school_average_score"] = float(score) / school_count
	except:
		d["elementary_school_count"] = 0
		d["elementary_school_average_score"] = 0

	print("elem count: " + str(d["elementary_school_count"]), 
		"elem score: " + str(d["elementary_school_average_score"]))

	sleep(5)
	try:
		school = driver.find_element_by_xpath("//button[@data-id='MIDDLE']").click()
		try:
			scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			scores = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		school_count = len(scores) - 1
		score = 0
		for s in scores[:-1]:
			try:
				score += int(s.text.split("\n")[0])
			except:
				school_count -= 1
		d["middle_school_count"] = school_count
		d["middle_school_average_score"] = float(score) / school_count
	except:
		d["middle_school_count"] = 0
		d["middle_school_average_score"] = 0

	print("middle_school_count: " + str(d["middle_school_count"]), 
		"middle_school_average_score: " + str(d["middle_school_average_score"]))

	sleep(5)
	try:
		school = driver.find_element_by_xpath("//button[@data-id='HIGH']").click()
		try:
			scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			scores = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		school_count = len(scores) - 1
		score = 0
		for s in scores[:-1]:
			try:
				score += int(s.text.split("\n")[0])
			except:
				school_count -= 1
		d["high_school_count"] = school_count
		d["high_school_average_score"] = float(score) / school_count
	except:
		d["high_school_count"] = 0
		d["high_school_average_score"] = 0

	print("high_school_count: " + str(d["high_school_count"]), 
		"high_school_average_score: " + str(d["high_school_average_score"]))

def extract_sold_rental_crime(driver, d):
	"""Extract number of Crimes from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	# try:
	# 	info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button/div[2]").text
	# 	button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button")
	# except:
	# 	try:
	# 		info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button/div[2]").text
	# 		button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button")
	# 	except:
	# 		try:
	# 			info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]").text
	# 			button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]")
	# 		except:
	# 			try:
	# 				info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]/div/div[2]").text
	# 				button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]")
	# 			except:
	# 				info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]").text
	# 				button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]")

	possible_xpath = ["//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button/div[2]", 
	"//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]/div/div[2]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]/div/div[2]"]

	buttons = ["//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button",
	"//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]",
	"//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]"]

	for xpath, btn in zip(possible_xpath, buttons):
		try:
			info_text = driver.find_element_by_xpath(xpath).text
			if "crime" in info_text.lower():
				button = driver.find_element_by_xpath(btn)
				break
		except:
			pass

	if "crime" in info_text.lower():
		button.click()
	else:
		try:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[4]/button").click()
		except:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[4]/button").click()

	print("crime button clicked")
	sleep(10)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Theft']").click()

		try:
			theft = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			theft = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["theft"] = len(theft) - 1
	except:
		d["theft"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Assault']").click()
		try:
			assault = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			assault = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["assault"] = len(assault) - 1
	except:
		d["assault"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Arrest']").click()
		try:
			arrest = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			arrest = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["arrest"] = len(arrest) - 1
	except:
		d["arrest"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Vandalism']").click()
		try:
			vandalism = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			vandalism = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["vandalism"] = len(vandalism) - 1
	except:
		d["vandalism"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Burglary']").click()
		try:
			burglary = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			burglary = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["burglary"] = len(burglary) - 1
	except:
		d["burglary"] = "NA"

	d["crime_other"] = "NA"

	print("assult: " + str(d.get("assault", "NA")), 
		"arrest: " + str(d.get("arrest", "NA")), 
		"theft: " + str(d.get("theft", "NA")), 
		"burglary: " + str(d.get("burglary", "NA")), 
		"vandalism: " + str(d.get("vandalism", "NA")))

def extract_sold_rental_shop_eat(driver, d):
	"""Extract Shop and Eat scores from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""
	
	webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

	print("Change to shop and eat")
	sleep(5)

	try:
		info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[5]/button/div[2]").text
		button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[5]/button")
	except:
		try:
			info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[5]/button/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[5]/button")
		except:
			try:
				info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]/div/div[2]").text
				button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]")
			except:
				try:
					info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]/div/div/div[2]").text
					button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]")
				except:
					try:
						info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[5]/div/div/div[2]").text
						button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[5]")
					except:
						print("shop & eat not available")
						return

	if "shop" in info_text.lower():
		button.click()
	else:
		try:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[6]/button").click()
		except:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[6]/button").click()

	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Restaurants']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["restaurant"] = len(item)
	except:
		d["restaurant"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Groceries']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["groceries"] = len(item)
	except:
		d["groceries"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Nightlife']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["nightlife"] = len(item)
	except:
		d["nightlife"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Cafes']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["cafe"] = len(item)
	except:
		d["cafe"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Shopping']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["shopping"] = len(item)
	except:
		d["shopping"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='ArtsAndEntertainment']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["entertainment"] = len(item)
	except:
		d["entertainment"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Fitness']").click()
		try:
			item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		except:
			item = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
		d["active_life"] = len(item)
	except:
		d["active_life"] = "NA"

	sleep(5)
	d["beauty"] = "NA"

	print(d["restaurant"], d["groceries"], d["nightlife"], d["cafe"], d["shopping"], d["entertainment"], d["beauty"], d["active_life"])
	sleep(3)
