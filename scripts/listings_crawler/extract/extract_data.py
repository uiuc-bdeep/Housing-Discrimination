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

from sold_rental.extract_sold_rental_data import *
from rental.extract_rental_data import *

def extract_commute(driver, d):
	"""Extract commute score from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	
	Returns:
	    Bool: True if have commute, False otherwise
	"""

	has_commute = False

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
					try:
						print("Trying to click commute image")
						driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[1]/div/div[1]/div/div[6]/div/button').click()
                                                print("Clicked one")
						driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
					except:
						print("EXCEPT commute")
						driver.find_element_by_xpath("//*[@id='tabButtonContainer']/button[5]").click()
						driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
                                                print("Successfully ended commute except")

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

	return has_commute

def check_off_market(driver):
	"""Check wheather if the listing is off market (or new/old type of layout, if you prefer)
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	
	Returns:
	    int: 0 if on market, 1 if old layout off market, 2 if new layout
	"""

	is_off_market = 0

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
						try:
							off_market = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[1]/div/div/div[3]/div[1]/span/span").text
							if "off" in off_market.lower() or "sold" in off_market.lower():
								print("off_market = 2")
								is_off_market = 2
						except:
							print ("in market")

	return is_off_market

def get_rent(driver, is_off_market):
	"""Extract the rent from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    is_off_market (int): Wheather the listing is off market
	
	Returns:
	    String: The rent
	"""

	# is_apartment = True
	# recently_sold = False

	if is_off_market > 0:
		try:
			rent = driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[6]/div/div/div[3]/div[1]/div[2]").text
		except:
			try:
				rent = driver.find_element_by_xpath("//*[@id='main-content']/div[2]/div[2]/div[1]/div/div/div[2]/h3/div").text
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
						# is_apartment = False
					except:
						try:
							rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div[2]/div[2]/div[1]/div[1]/span").text
							# recently_sold = True
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
										try:
											rent = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[2]/h3/div').text
										except:
											print("Unable to find RENT")
											rent = "NA"

	return rent

def get_address(driver, d):
	"""Extract the address from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

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
							except:
								try:
									d["address"] = driver.find_element_by_xpath("//*[@id='address']/h1/div[1]/span").text
									city_state = driver.find_element_by_xpath("//*[@id='address']/h1/div[2]/span[1]").text
									d["city"] = city_state.split(", ")[0]
									d["state"] = city_state.split(", ")[1].split(" ")[0]
									d["zip code"] = city_state.split(" ")[-1]
								except:
									try:
										d["address"] = driver.find_element_by_xpath('//*[@id="address"]/h1/div[1]/span').text
										city_state = driver.find_element_by_xpath('//*[@id="address"]/h1/div[2]/span[1]').text
										d["city"] = city_state.split(", ")[0]
                                                                        	d["state"] = city_state.split(", ")[1].split(" ")[0]
                                                                        	d["zip code"] = city_state.split(" ")[-1]
									except:
										try:
											d["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/h1/span[1]').text
                                                                                	city_state = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/h1/span[2]').text
                                                                                	d["city"] = city_state.split(", ")[0]
                                                                                	d["state"] = city_state.split(", ")[1].split(" ")[0]
                                                                                	d["zip code"] = city_state.split(" ")[-1]
										except Exception as error:
											d["address"] = "NA"
											d["city"] = "NA"
											d["state"] = "NA"
											d["zip code"] = "NA"
											print("Unable to find ADDRESS")
											print("Caught this error: " + repr(error))

def extract_phone(driver, d):
	"""Extract phone number from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

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

def extract_rental(driver, d, mode, add = None, df = None, index = None):
	"""Extract all information from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	    mode (String): One of "U", "R", "A"
	    add (None, optional): Address from csv if available
	    df (None, optional): Dataframe from csv if available and is in R mode
	    index (None, optional): Starting index from csv
	
	Returns:
	    Bool: True if success, False otherwise
	
	Raises:
	    Exception: Description
	"""
	
	is_off_market = check_off_market(driver)

	rent = get_rent(driver, is_off_market)

	d["rent_per_month"] = rent.split("/")[0]

	if (mode == "R" and pd.isnull(df["Rent_Per_Month"][index])):
		df.at[index, "Rent_Per_Month"] = d["rent_per_month"]

	print("Rent per month: " + d["rent_per_month"])

	d["short_form_id"] = "NA"
	
	if (mode == "R" and pd.isnull(df["Address"][index])) or mode == "U":
		get_address(driver, d)

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

		extract_sold_rental_detail(driver, d)

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
		extract_rental_detail(driver, d)

		print("bedroom_min: " + d.get("bedroom_min", "NA"), 
			"bedroom_max: " + d.get("bedroom_max", "NA"), 
			"bathroom_min: " + d.get("bathroom_min", "NA"), 
			"bathroom_max: " + d.get("bathroom_max", "NA"), 
			"days on Trulia: " + d.get("days", "NA"))

		print("sqft: " + d.get("sqft", "NA"), 
			"Year Built: " + d.get("year", "NA"), 
			"Type of housing: " + d.get("type", "NA"))

		if mode == "R":
			df.at[index, "Bedroom_min"] = d.get("bedroom_min", "NA")
			df.at[index, "Bedroom_max"] = d.get("bedroom_max", "NA")
			df.at[index, "Bathroom_min"] = d.get("bathroom_min", "NA")
			df.at[index, "Bathroom_max"] = d.get("bathroom_max", "NA")
			df.at[index, "Days_on_Trulia"] = d.get("days", "NA")
			df.at[index, "Sqft"] = d.get("sqft", "NA")
			df.at[index, "Year"] = d.get("year", "NA")
			df.at[index, "Type"] = d.get("type", "NA")

		extract_phone(driver, d)

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
		extract_rental_crime(driver, d)
	
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

	has_commute = extract_commute(driver, d)

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
