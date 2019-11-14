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
import crime, school, shop, basic_info as basic

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
				rent = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[2]/div/h3/div').text
			except:
				try:
					rent = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[2]/div/h3/div').text
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
			d["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/h1/span[1]').text
			city_state = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/h1/span[2]').text
			d["city"] = city_state.split(", ")[0]
                       	d["state"] = city_state.split(", ")[1].split(" ")[0]
                        d["zip code"] = city_state.split(" ")[-1]

		except:
			try:
				d["address"] = driver.find_element_by_xpath('//*[@id="home-details-page-city-state-element"]').text
				city_state = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/h1/span[3]').text
				d["city"] = city_state.split(", ")[0]
				d["state"] = city_state.split(", ")[1].split(" ")[0]
				d["zip code"] = city_state.split(" ")[-1]
			except:
				try:
					d["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/h1/span[1]').text
					city_state = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/h1/span[2]').text
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
								except:
									try:
										d["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/h1/span[2]').text
										city_state = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/h1/span[3]').text
                                                                                d["city"] = city_state.split(", ")[0]
                                                                              	d["state"] = city_state.split(", ")[1].split(" ")[0]
                                                                                d["zip code"] = city_state.split(" ")[-1]
									except 	Exception as error:
										print("Unable to find ADDRESS")
										print("Caught this error: " + repr(error))

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

	if mode == "R":
		if index < 5:
			print(df[["Address", "Bedroom_min", "Bedroom_max", "Bathroom_min", "Bathroom_max"]].iloc[:5])
		else:
			print(df[["Address", "Bedroom_min", "Bedroom_max", "Bathroom_min", "Bathroom_max"]].iloc[index-5:index + 2])

	if mode == "R":
		return True
        is_off_market = check_off_market(driver)
        if not is_off_market:
            print("On the market")
	extract_basic_info(driver, d, is_off_market)
        extract_crime(driver, d, is_off_market)
        extract_school(driver, d, is_off_market)
        extract_shop_and_eat(driver, d, is_off_market)
        return True

def click_escape(driver):
	try:
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	except:
		driver.find_element_by_xpath("//*[@id='propertyTitleBar']/ul/li[3]/button/i").click()
        sleep(1)

def extract_basic_info(driver, d, off_market):
	print("Extracting Basic Info")
	basic.extract_basic_info(driver, d, off_market)
	return 0

def extract_crime(driver, d, off_market):
        print("Extracting Crime Data")
        crime.extract_crime(driver, d, off_market)
	click_escape(driver)
        return 0

def extract_school(driver, d, off_market):
        print("Extracting School Data")
        school.extract_school(driver, d, off_market)
	click_escape(driver)
        return 0

def extract_shop_and_eat(driver, d, off_market):
        print("Extracting Shop & Eat")
        shop.extract_shop(driver, d, off_market)
        return 0
