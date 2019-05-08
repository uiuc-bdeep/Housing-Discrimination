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

def extract_data(driver, d, crawl_type):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	sleep(3)

	try:
		#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@data-role='address']"))).text
		address = driver.find_element_by_xpath("//*[@data-role='address']").text
		d["address"] = address
	except:
		print("Address Not Disclosed")
		d["address"] = "Address Not Disclosed"
		return False

	if crawl_type != "sold":
		try:
			agent_name = driver.find_element_by_xpath("//*[@id='topPanelLeadFormContainer']/div/div/form/div[1]/div[1]/div[1]/img").get_attribute("alt").split(",")[0]
			print(agent_name)
			d["agent_name"] = agent_name
		except:
			print("agent unavailable")
			d["agent_name"] = "NA"

	city_state = driver.find_element_by_xpath("//*[@data-role='cityState']").text
	city, state = city_state.split(", ")
	print(state)
	state, zip_code = state.split(" ")
	d["city"] = city
	d["state"] = state
	d["zip code"] = "\"" + zip_code + "\""

	price = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]").text.split("\n")[1]
	d["price"] = sub(r'[^\d.]', '', price)


	if crawl_type != "sold":
		details = driver.find_element_by_xpath("//div[7]/div[2]/div/div[2]/div[1]").text.split("\n")
	else:
		#d["sold_on"] = " ".join(driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]/div/div[1]/div/span[3]").text.split(" ")[1:])
		try:
			details = driver.find_element_by_xpath("//div[7]/div[3]/div/div[2]/div[1]").text.split("\n")
		except:
			print("It's not sold")
			return False

	for detail in details:
		if "Bed" in detail:
			d["bedroom"] = detail.split(" ")[0]
		if "Bath" in detail:
			d["bathroom"] = detail.split(" ")[0]
		if "Built in " in detail:
			d["year"] = detail.split(" ")[-1]
		if crawl_type != "sold":
			if "days" in detail:
				d["days"] = detail.split(" ")[0]
	home = details[0]
	d["type"] = home

	try:
		details = driver.find_element_by_xpath("//div[7]/div[2]/div/div[2]/div[2]").text.split("\n")
	except:
		print("house already sold")
		if crawl_type == "sold":
			details = driver.find_element_by_xpath("//div[7]/div[3]/div/div[2]/div[2]").text.split("\n")
		else:
			return False

	for detail in details:
		if "/sqft" in detail:
			d["dolloar_per_sqft"] = sub(r'[^\d.]', '', detail.split("/")[0])
		if " sqft" in detail:
			d["sqft"] = sub(r'[^\d.]', '', detail.split(" ")[0])
		if "lot size" in detail:
			d["lot_size"] = sub(r'[^\d.]', '', detail.split(" ")[0])
			d["lot_size_unit"] = detail.split(" ")[1]
		if "view" in detail:
			d["views"] = detail.split(" ")[0]

	sleep(3)

	if crawl_type == "sold":
		ele = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[7]/div[3]/div/div[6]"))).text.split("\n")[3:]
		i = 0
		f = False
		while i < 5:
			try:
				index = ele.index("Sold")
				d["sold_on"] = ele[index - 2]
				i = 5
			except:
				driver.refresh()
				print("refresh")
				sleep(5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				ele = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[7]/div[3]/div/div[6]"))).text.split("\n")[3:]
				i += 1
		try:
			index = ele.index("Listed for sale")
			d["last_listed_date"] = ele[index - 2]
			d["last_listed_price"] = sub(r'[^\d.]', '', ele[index - 1])
			d["days"] = str(datetime.datetime.strptime(d["sold_on"], "%m/%d/%Y").date() - datetime.datetime.strptime(d["last_listed_date"], "%m/%d/%Y").date()).split(" ")[0]
		except:
			print("last listed date unavailable")

		try:
			tmp = ele[index+1:]
			index = tmp.index("Sold")
			d["prior_sales_date"] = tmp[index - 2]
			d["prior_sales_price"] = sub(r'[^\d.]', '', tmp[index - 1])
		except:
			print("prior sales unavailable")
			d["prior_sales_date"] = "NA"
			d["prior_sales_price"] = "NA"

		try:
			mortgage = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='mortgage-calculators-home-price']/div/span/input")))
			driver.execute_script("arguments[0].scrollIntoView();", mortgage)
			mortgage.clear()
			mortgage.send_keys(d["price"])
		except:
			print("no affordability available")
			return True
		sleep(1)
        #driver.save_screenshot('screenie.png')
		tmp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='moduleAccordion']/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]"))).text
        #print(hello)
	#affordability = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "affordabilityModule")))
	#tmp = WebDriverWait(affordability, 30).until(EC.presence_of_element_located((By.XPATH, "//div/div/div[2]/div[1]/div/div/div[2]"))).text
	#tmp = affordability.find_element_by_xpath("//div/div/div[2]/div[1]/div/div/div[2]").text.split("\n")
	tmp = tmp.split("\n")
        #print(tmp)
	if len(tmp) == 1:
		print("no affordability")
		return True

	for i in range(0, 9, 2):
		d[tmp[i].strip()] = sub(r'[^\d.]', '', tmp[i+1].replace("(", "").replace(")",""))
		print(d[tmp[i].strip()], tmp[i].strip())

	return True

def extract_school_and_crime(driver, d):
	go = driver.find_element_by_id("crimeCard")
	go.click()

	#crime = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div")
	has_crime_report = False

	try:
		crime = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='crimeTab']/div[2]/div/div[2]/div/ul")))
		#crime = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div/div[2]/div/ul")
		has_crime_report = True
	except:
		print ("no crime report")

	if has_crime_report == False:
		d["Theft"] = 0
		d["Assault"] = 0
		d["Arrest"] = 0
	else:
		crimes = crime.text.split("\n")
		for i in range(0, len(crimes) - 1, 2):
			d[crimes[i+1]] = crimes[i]

	go = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Schools')]")))
	# go = driver.find_element_by_xpath("//button[contains(text(), 'Schools')]")
	go.click()
	sleep(5)

	button = Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/form/div/span/div/select"))))
	#button = Select(driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/form/div/span/div/select"))
	button.select_by_value("Assigned")

	try:
		#elementary = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span"))).text
		elementary = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(elementary)):
			if (i + 1) % 5 == 0:
				tmp.append(elementary[i])
		index = elementary.index(min(tmp))
		d["elementary_name"] = elementary[index - 3]
		d["elementary"] = elementary[index - 4]
		
		#elementary = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span").text
		#d["elementary"] = elementary
		if d["elementary"] == "-":
			d["elementary"] = "NA"
	except:
		print("No elementary scahool available")
		d["elementary"] = "NA"
		d["elementary_name"] = "NA"

	go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[2]/div")
	go.click()

	try:
		#middle = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span"))).text
		#middle = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span").text
		#d["middle"] = middle
		middle = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(middle)):
			if (i + 1) % 5 == 0:
				tmp.append(middle[i])
		index = middle.index(min(tmp))
		d["middle_name"] = middle[index - 3]
		d["middle"] = middle[index - 4]
		if d["middle"] == "-":
			d["middle"] = "NA"
	except:
		print("No middle school available")
		d["middle"] = "NA"
		d["middle_name"] = "NA"

	go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[3]/div")
	go.click()

	try:
		high_school = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(high_school)):
			if (i + 1) % 5 == 0:
				tmp.append(high_school[i])
		index = high_school.index(min(tmp))
		d["high_school_name"] = high_school[index - 3]
		d["high school"] = high_school[index - 4]
	except:
		print("No high school available")
		d["high school"] = "NA"
		d["high_school_name"] = "NA"

def extract_sold_rental_crime(driver, d):
	try:
		info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button/div[2]").text
		button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/button")
	except:
		try:
			info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/button")
		except:
			info_text = driver.find_element_by_xpath("//*[@id='__next']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]/div/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='__next']/div[2]/div[2]/div[4]/div[2]/div/div/div[4]")

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
		theft = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["theft"] = len(theft) - 1
	except:
		d["theft"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Assault']").click()
		assault = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["assault"] = len(assault) - 1
	except:
		d["assault"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Arrest']").click()
		arrest = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["arrest"] = len(arrest) - 1
	except:
		d["arrest"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Vandalism']").click()
		vandalism = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["vandalism"] = len(vandalism) - 1
	except:
		d["vandalism"] = "NA"

	sleep(3)

	try:
		crime = driver.find_element_by_xpath("//button[@data-id='Burglary']").click()
		burglary = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["burglary"] = len(burglary) - 1
	except:
		d["burglary"] = "NA"

	d["crime_other"] = "NA"

	print("assult: " + d.get("assault", "NA"), 
		"arrest: " + d.get("arrest", "NA"), 
		"theft: " + d.get("theft", "NA"), 
		"burglary: " + d.get("burglary", "NA"), 
		"vandalism: " + d.get("vandalism", "NA"))

def extract_sold_rental_school(driver, d):
	try:
		info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button/div[2]").text
		button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button")
	except:
		try:
			info_text = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/button")
		except:
			info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[3]")

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
		scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
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

	print("elem count: " + d["elementary_school_count"], 
		"elem score: " + d["elementary_school_average_score"])

	sleep(5)
	try:
		school = driver.find_element_by_xpath("//button[@data-id='MIDDLE']").click()
		scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
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

	print("middle_school_count: " + d["middle_school_count"], 
		"middle_school_average_score: " + d["middle_school_average_score"])

	sleep(5)
	try:
		school = driver.find_element_by_xpath("//button[@data-id='HIGH']").click()
		scores = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
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

	print("high_school_count: " + d["high_school_count"], 
		"high_school_average_score: " + d["high_school_average_score"])

def extract_rental_school(driver, d):
	try:
		driver.find_element_by_xpath("//*[@id='schoolsCard']").click()
	except:	
		try:
			driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
		except:
				driver.refresh()
				driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
	try:
		print ("try part for school")
		button = Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/form/div/span/div/select"))))
		button.select_by_value("Assigned")

		elementary_school_count = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[1]/div/div").text
		d["elementary_school_count"] = elementary_school_count

		if int(d["elementary_school_count"]) == 0:
			d["elementary_school_average_score"] = 0
		else:
			score = 0
			elementary_school = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]").text.split("\n")
			for s in range(0,len(elementary_school),5):
				if elementary_school[s] != u'-':
					score += int(elementary_school[s])
			d["elementary_school_average_score"] = score / int(d["elementary_school_count"])

		go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[2]/div")
		go.click()

		middle_school_count = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[2]/div/div").text
		d["middle_school_count"] = middle_school_count

		if int(d["middle_school_count"]) == 0:
			d["middle_school_average_score"] = 0
		else:
			score = 0
			middle_school = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]").text.split("\n")
			for s in range(0, len(middle_school), 5):
				if middle_school[s] != u'-':
					score += int(middle_school[s])
			d["middle_school_average_score"] = score / int(d["middle_school_count"])

		go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[3]/div")
		go.click()

		high_school_count = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[3]/div/div").text
		d["high_school_count"] = high_school_count

		if int(d["high_school_count"]) == 0:
			d["high_school_average_score"] = 0
		else:
			score = 0
			high_school = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]").text.split("\n")
			for s in range(0, len(high_school), 5):
				if high_school[s] != u'-': 
					score += int(high_school[s])
			d["high_school_average_score"] = score / int(d["high_school_count"])

		print(d["elementary_school_count"], d["middle_school_count"], d["high_school_count"])
		print(d["elementary_school_average_score"], d["middle_school_average_score"], d["high_school_average_score"])
	except:
		print("except part for school")
		high_school = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[1]/div/div[2]/table/tbody"))).text.split("\n")
		total = 0
		indices = [i for i, j in enumerate(high_school) if "Assigned" in j]
		for i in indices:
			total += int(high_school[i+1])
		d["high_school_count"] = len(indices)
		if len(indices) != 0:
			d["high_school_average_score"] = total / len(indices)
		else:
			d["high_school_average_score"] = "NA"

		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[1]/div/div[2]/table/thead/tr/th[1]/select/option[2]"))).click()
		sleep(3)

		middle_school = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[1]/div/div[2]/table/tbody"))).text.split("\n")
		total = 0
		indices = [i for i, j in enumerate(middle_school) if "Assigned" in j]
		for i in indices:
			total += int(middle_school[i+1])
		d["middle_school_count"] = len(indices)
		if len(indices) != 0:
			d["middle_school_average_score"] = total / len(indices)
		else:
			d["middle_school_average_score"] = "NA"

		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[1]/div/div[2]/table/thead/tr/th[1]/select/option[3]"))).click()
		sleep(3)

		elementary_school = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[1]/div/div[2]/table/tbody"))).text.split("\n")
		total = 0
		indices = [i for i, j in enumerate(elementary_school) if "Assigned" in j]
		for i in indices:
			total += int(elementary_school[i+1])
		d["elementary_school_count"] = len(indices)
		if len(indices) != 0:
			d["elementary_school_average_score"] = total / len(indices)
		else:
			d["elementary_school_average_score"] = "NA"

def extract_commute(driver, d, has_commute):
	try:
		try:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[6]").click()
			print("change to commute")
			driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
			#driving = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]
		except:
			try:
				driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[5]").click()
				print("commute button")
				driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
				#driving = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]
			except:
				try:
					driver.find_element_by_xpath("//*[@id='commuteCard']").click()
					print("commute card")
					driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
				except:
					driver.find_element_by_xpath("//*[@id='tabButtonContainer']/button[5]").click()
					driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]

		sleep(5)
		
		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[2]").click()

		transit = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[3]").click()

		walking = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[4]").click()

		cycling = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		d["driving"] = driving
		d["transit"] = transit
		d["walking"] = walking
		d["cycling"] = cycling
		has_commute = True
		print (driving, transit, walking, cycling)
	except:
		d["driving"] = "NA"
		d["transit"] = "NA"
		d["walking"] = "NA"
		d["cycling"] = "NA"
		print("commute not available")

def extract_sold_rental_shop_eat(driver, d):
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
			info_text = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]/div/div[2]").text
			button = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[4]/div[2]/div/div/div[6]")

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
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["restaurant"] = len(item)
	except:
		d["restaurant"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Groceries']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["groceries"] = len(item)
	except:
		d["groceries"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Nightlife']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["nightlife"] = len(item)
	except:
		d["nightlife"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Cafes']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["cafe"] = len(item)
	except:
		d["cafe"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Shopping']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["shopping"] = len(item)
	except:
		d["shopping"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='ArtsAndEntertainment']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["entertainment"] = len(item)
	except:
		d["entertainment"] = "NA"
	sleep(5)

	try:
		button = driver.find_element_by_xpath("//button[@data-id='Fitness']").click()
		item = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
		d["active_life"] = len(item)
	except:
		d["active_life"] = "NA"

	sleep(5)
	d["beauty"] = "NA"

	print(d["restaurant"], d["groceries"], d["nightlife"], d["cafe"], d["shopping"], d["entertainment"], d["beauty"], d["active_life"])
	sleep(3)

def extract_rental_shop_eat(driver, d):
	try:
		try:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[7]").click()
			print("change to shop and eat")
			restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
			#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]
		except:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[6]").click()
			print("shop and eat button")
			restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
			#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

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

def extract_rental(driver, d, mode, add = None, df = None, index = None):
	is_off_market = 0
	is_apartment = True
	recently_sold = False

	try:
		off_market = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]/div/div[1]/div/span[1]").text
		if "OFF" in off_market:
			print("off market = 1")
			is_off_market = 1
	except:
		try:
			off_market = driver.find_element_by_xpath("//*[@id='marketStatusLabel']").text
			if "off" in off_market.lower():
				print("off market = 1")
				is_off_market = 1
		except:
			try:
				off_market = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[1]/div/div/div[3]/div[1]/div/span/span").text
				if "off" in off_market.lower() or "sold" in off_market.lower():
					print("off market = 2")
					is_off_market = 2
			except:
				try:
					off_market = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[1]/div/div/div[3]/div[1]/span/span").text
					if "off" in off_market.lower() or "sold" in off_market.lower():
						print("off market = 2")
						is_off_market = 2
				except:
					try:
						off_market = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[2]/div[1]/div/div/div[3]/div[1]/span[1]/span").text
						if "off" in off_market.lower() or "sold" in off_market.lower():
							print("off_market = 2")
							is_off_market = 2
					except:
						print ("in market")

	if is_off_market > 0:
		try:
			rent = driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[6]/div/div/div[3]/div[1]/div[2]").text
		except:
			rent = "NA"
	else:
		try:
			rent = driver.find_element_by_xpath("//*[@id='rentalPdpContactLeadForm']/div[1]/div").text
		except:
			try:
				rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div[3]/div[1]/div/div[2]/span").text
			except:
				try:
					rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div[3]/div[1]/div/div[2]/span[1]").text
				except:
					try:
						rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]/div/div[2]/span").text
						is_apartment = False
					except:
						try:
							rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div[2]/div[2]/div[1]/div[1]/span").text
							recently_sold = True
						except:
							try:
								rent = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div/div[2]/h2/div").text
							except:
								try:
									rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div[2]/div[1]/div/div[2]/span").text
								except:
									try:
										rent = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div[1]/div[2]/h2/div").text
									except:
										rent = "NA"

	d["rent_per_month"] = rent.split("/")[0]

	if (mode == "R" and pd.isnull(df["Rent_Per_Month"][index])):
		df.at[index, "Rent_Per_Month"] = d["rent_per_month"]

	print("Rent per month: " + d["rent_per_month"])

	d["short_form_id"] = "NA"
	
	if (mode == "R" and pd.isnull(df["Address"][index])) or mode == "U":
		try:
			info = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/div[2]/span").text.split(", ")
			d["address"] = info[0]
			d["city"] = info[1]
			d["state"] = info[2].split(" ")[0]
			d["zip code"] = "\"" + info[2].split(" ")[1] + "\""
		except:
			try:
				info = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/div[2]").text.split("\n")
				d["address"] = info[0]
				d["city"] = info[1].split(", ")[0]
				d["state"] = info[1].split(", ")[1].split(" ")[0]
				d["zip code"] = info[1].split(", ")[1].split(" ")[1]
			except:
				try:
					info = driver.find_element_by_xpath("/html/body/footer/div[1]/div[1]/div").text
					try:
						d["address"] = info.split(". ")[0].split("located at ")[1].split(", ")[0]
						d["city"] = info.split(". ")[0].split("located at ")[1].split(", ")[1]
						d["state"] = info.split(". ")[0].split("located at ")[1].split(", ")[2]
					except:
						d["address"] = driver.find_element_by_xpath("//*[@id='address']/h1/div[1]/span").text
						d["city"] = info.split(". ")[0].split("located at ")[1].rsplit(" ", 2)[0]
						d["state"] = info.split(". ")[0].split("located at ")[1].rsplit(" ", 2)[1]
					zip_index = info.split(". ")[1].split(" ").index("ZIP")
					if info.split(". ")[1].split(" ")[zip_index + 2].isdigit(): 
						d["zip code"] = info.split(". ")[1].split(" ")[zip_index + 2]
					elif info.split(". ")[1].split(" ")[zip_index - 1].isdigit():
						d["zip code"] = info.split(". ")[1].split(" ")[zip_index - 1]
				except:
					try:
						d["address"] = driver.find_element_by_xpath("//*[@id='propertySummary']/div[2]/div[1]/div[1]/div/h1/div").text
						city_state = driver.find_element_by_xpath("//*[@id='propertySummary']/div[2]/div[1]/div[1]/div/h1/span").text
						d["city"] = city_state.split(", ")[0]
						d["state"] = city_state.split(", ")[1].split(" ")[0]
						d["zip code"] = city_state.split(" ")[-1]
					except:
						try:
							d["address"] = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[1]/div/h1/div").text
							city_state = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[1]/div/h1/span").text
							d["city"] = city_state.split(", ")[0]
							d["state"] = city_state.split(", ")[1].split(" ")[0]
							d["zip code"] = city_state.split(" ")[-1]
						except:
							try:
								d["address"] = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div[1]/div[1]/h1/span[1]").text
								city_state = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div[1]/div[1]/h1/span[2]").text
								d["city"] = city_state.split(", ")[0]
								d["state"] = city_state.split(", ")[1].split(" ")[0]
								d["zip code"] = city_state.split(" ")[-1]
							except:
								try:
									d["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/h1/span[1]').text
									city_state = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[1]/div/div/div[1]/h1/span[2]").text
									d["city"] = city_state.split(", ")[0]
									d["state"] = city_state.split(", ")[1].split(" ")[0]
									d["zip code"] = city_state.split(" ")[-1]
								except Exception as error:
									print("Caught this error: " + repr(error))

		print("address: " + d.get("address", "NA"), 
			"city: " + d.get("city", "NA"), 
			"state: " + d.get("state", "NA"), 
			"zip code: " + d.get("zip code", "NA"))

		if mode == "R":
			df.at[index, "Address"] = d.get("address", "NA")
			df.at[index, "City"] = d.get("city", "NA")
			df.at[index, "State"] = d.get("state", "NA")
			df.at[index, "Zip_Code"] = d.get("zip code", "NA")

	if add and mode != "R":
		df_address = add.rsplit(", ", 3)

		d["address"] = df_address[0]
		d["city"] = df_address[1]
		d["state"] = df_address[2]
		d["zip code"] = df_address[3]

		print(d["address"] + " " + d["city"] + " " + d["state"] + " " + d["zip code"])

	if is_off_market == 2:
		sleep(5)
		try:
			detail = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/ul").text.split("\n")
		except:
			try:
				detail = driver.find_element_by_xpath("//*[@id='__next']/div/section/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/ul").text.split("\n")
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

		if mode == "R":
			df.at[index, "Days_on_Trulia"] = d.get("days", "NA")
			df.at[index, "Sqft"] = d.get("sqft", "NA")
			df.at[index, "Year"] = d.get("year", "NA")
			df.at[index, "Type"] = d.get("type", "NA")
			df.at[index, "Bedroom_min"] = d.get("bedroom_min", "NA")
			df.at[index, "Bedroom_max"] = d.get("bedroom_max", "NA")
			df.at[index, "Bathroom_min"] = d.get("bathroom_min", "NA")
			df.at[index, "Bathroom_max"] = d.get("bathroom_max", "NA")

		print("bedroom_min: " + d.get("bedroom_min", "NA"), 
			"bedroom_max: " + d.get("bedroom_max", "NA"), 
			"bathroom_min: " + d.get("bathroom_min", "NA"), 
			"bathroom_max: " + d.get("bathroom_max", "NA"), 
			"sqft: " + d.get("sqft", "NA"))
	else:
		try:
			property_detail = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/ul[1]").text.split("\n")
		except:
			try:
				property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[4]").text.split("\n")
				if "overview" in property_detail[0].lower():
					property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[5]").text.split("\n")
			except:
				try:
					property_detail = driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[1]/ul").text.split("\n")
					property_detail += driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[2]/ul").text.split("\n")
				except:
					try:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[1]/ul").text.split("\n")
						property_detail += driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[2]/ul").text.split("\n")
					except:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[3]/div[2]/div/div[1]/ul").text.split("\n")

		bedroom = ""
		bathroom = ""

		for detail in property_detail:
			if "bed" in detail.lower():
				bedroom = detail.rsplit(" ", 1)[0]
			elif "bath" in detail.lower():
				bathroom = detail.rsplit(" ", 2)[0]
			elif "day" in detail.lower():
				d["days"] = detail.split(" ")[0]

		#if bedroom != "":
		#	bedroom = property_detail[0].rsplit(" ", 1)[0]
		#if bathroom != "":
		#	bathroom = property_detail[1].rsplit(" ", 2)[0]

		if " - " in bedroom:
			d["bedroom_min"] = bedroom.split(" - ")[0]
			d["bedroom_max"] = bedroom.split(" - ")[1]
		elif "-" in bedroom:
			d["bedroom_min"] = bedroom.split("-")[0]
			d["bedroom_max"] = bedroom.split("-")[1]
		elif bedroom != "":
			d["bedroom_min"] = bedroom[0]
			d["bedroom_max"] = bedroom[0]
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
			d["bathroom_min"] = bathroom[0]
			d["bathroom_max"] = bathroom[0]
		else:
			d["bathroom_min"] = "NA"
			d["bathroom_max"] = "NA"

		print("bedroom_min: " + d.get("bedroom_min", "NA"), 
			"bedroom_max: " + d.get("bedroom_max", "NA"), 
			"bathroom_min: " + d.get("bathroom_min", "NA"), 
			"bathroom_max: " + d.get("bathroom_max", "NA"), 
			"days on Trulia: " + d.get("days", "NA"))

		if mode == "R":
			df.at[index, "Bedroom_min"] = d.get("bedroom_min", "NA")
			df.at[index, "Bedroom_max"] = d.get("bedroom_max", "NA")
			df.at[index, "Bathroom_min"] = d.get("bathroom_min", "NA")
			df.at[index, "Bathroom_max"] = d.get("bathroom_max", "NA")
			df.at[index, "Days_on_Trulia"] = d.get("days", "NA")

		try:
			property_detail = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/ul[2]").text.split("\n")
		except:
			try:
				property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[4]").text.split("\n")
				if "overview" in property_detail[0].lower():
					property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[5]").text.split("\n")
			except:
				try:
					property_detail = driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[1]/ul").text.split("\n")
					property_detail += driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[2]/ul").text.split("\n")
				except:
					try:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[1]/ul").text.split("\n")
						property_detail += driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[2]/ul").text.split("\n")
					except:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[3]/div[2]/div/div[1]/ul").text.split("\n")

		for s in property_detail:
			if "sqft" in s and "/sqft" not in s:
				d["sqft"] = s.split(" ")[0]
			elif "Built" in s:
				d["year"] = s.split(" ")[2]
			elif "Home" in s or "Apartment" in s or "Family" in s or "loft" in s.lower():
				d["type"] = s

		if mode == "R":
			df.at[index, "Sqft"] = d.get("sqft", "NA")
			df.at[index, "Year"] = d.get("year", "NA")
			df.at[index, "Type"] = d.get("type", "NA")

		print("sqft: " + d.get("sqft", "NA"), 
			"Year Built: " + d.get("year", "NA"), 
			"Type of housing: " + d.get("type", "NA"))

		try:
			phone = driver.find_element_by_xpath("//*[@id='contactAside']/div/h3").text
			if "Contact" in phone:
				d["phone_number"] = driver.find_element_by_xpath("//*[@id='contactAside']/div/div/span").text
			elif "Ask" in phone:
				d["phone_number"] = driver.find_element_by_xpath("//*[@id='contactAside']/div/div/div/div/div/div[2]").text
			else:
				d["phone_number"] = "NA"
		except:
			try:
				phone = driver.find_element_by_xpath("//*[@id='topPanelLeadForm']/div/div/div/div[2]/div[2]/span").text
				d["phone_number"] = phone
			except:
				try:
					phone = driver.find_element_by_xpath("//*[@id='topPanelLeadFormContainer']/div/div/form/div[1]/div[1]/div[2]/div/div[3]").text
				except:
					try:
						phone = driver.find_element_by_xpath("//*[@id='topPanelLeadForm']/div/form/div/div/div/div[2]/div[2]/span").text
					except:
						print ("no phone available")
						d["phone_number"] = "NA"

		print("phone number: " + d.get("phone_number", "NA"))

	if mode == "R":
		if index < 5:
			print(df[["Address", "Bedroom_min", "Bedroom_max", "Bathroom_min", "Bathroom_max"]].iloc[:5])
		else:
			print(df[["Address", "Bedroom_min", "Bedroom_max", "Bathroom_min", "Bathroom_max"]].iloc[index-5:index + 2])

	if mode == "R":
		return True

	if is_off_market == 2:
		sleep(5)
		extract_sold_rental_crime(driver, d)
	else:
		try:
			driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[4]/div[2]/div[2]/div[2]").click()
		except:
			try:
				driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[3]/div[2]/div[2]/div[2]").click()
			except:
				try:
					driver.find_element_by_xpath("//*[@id='crimeCard']/div/div[2]").click()
				except:
					driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div[1]/div/div[4]/button").click()
		
		sleep(15)

		try:
			crime = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]/div/table/tbody").text.split("\n")[1::3]
			d["assault"] = crime.count("Assault")
			d["arrest"] = crime.count("Arrest")
			d["theft"] = crime.count("Theft")
			d["burglary"] = crime.count("Burglary")
			d["vandalism"] = crime.count("Vandalism")
			d["crime_other"] = crime.count("Other")
		except:
			try:
				one = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div/div[2]/div/ul/li[1]/div").text.split("\n")
				two = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div/div[2]/div/ul/li[2]/div").text.split("\n")
				three = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div/div[2]/div/ul/li[3]/div").text.split("\n")
				print(one[1], two[1], three[1])
				print(one[0], two[0], three[0])
				d[one[1].lower()] = one[0]
				d[two[1].lower()] = two[0]
				d[three[1].lower()] = three[0]
			except:
				d["assault"] = "NA"
				d["arrest"] = "NA"
				d["theft"] = "NA"
				d["burglary"] = "NA"
				d["vandalism"] = "NA"
				d["crime_other"] = "NA"
	
	try:
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	except:
		driver.find_element_by_xpath("//*[@id='propertyTitleBar']/ul/li[3]/button/i").click()

	print("change to school")
	sleep(5)

	if is_off_market == 2:
		extract_sold_rental_school(driver, d)
	else:
		extract_rental_school(driver, d)

	has_commute = False

	extract_commute(driver, d, has_commute)

	if is_off_market == 2:
		extract_sold_rental_shop_eat(driver, d)
	else:
		extract_rental_shop_eat(driver, d)

	if not is_off_market:
		if d["restaurant"] != "NA" and d["driving"] == "NA":
			# print("commute missing")
			driver.quit()
			raise Exception('commute missing!')

		if d["driving"] != "NA" and d["restaurant"] == "NA":
			# print("shop and eat missing")
			driver.quit()
			raise Exception('shop and eat missing!')
	return True

