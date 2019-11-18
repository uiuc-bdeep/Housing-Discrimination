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
sys.path.insert(1, '/home/ubuntu/Housing-Discrimination/scripts/listings_crawler/')
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


def extract_crime(driver, d, off_market):
	#d = {"theft": "NA", "burglary": "NA", "assault": "NA", "arrest": "NA", "vandalism": "NA", "crime_other": "NA"}
	xpath_list = []
	if not off_market:  # Listing is on the market
		xpath_list = [('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div'), ('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[4]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[4]/div')]
	else:  		    # Listing is off the market
		xpath_list = [('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]/div'), ('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div/div[2]', '//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div/div/div[3]/div')]
	result = find_button(driver, xpath_list, d)
	if result == 0:
		print("\tCrime Page Found")
	else:
		print("\tCould NOT find Crime button")
		set_NA(d)
		sleep(1)
		driver.save_screenshot("missing/missing-crime.png")
		return -1
	sleep(3)
	d["Theft"] =     count_crime(driver, "Theft",     '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[1]/div/button')
	sleep(1)
	d["Assault"] =   count_crime(driver, "Assault",   '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[2]/div/button')
	sleep(1)
	d["Arrest"] =    count_crime(driver, "Arrest",    '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[3]/div/button')
	sleep(1)
	d["Vandalism"] = count_crime(driver, "Vandalism", '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[4]/div/button')
	sleep(1)
	d["Burglary"] =  count_crime(driver, "Burglary",  '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[5]/div/button')
	close_page(driver)
	return 0

def close_page(driver):
	driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[1]/div/div[2]/div[2]').click()
	sleep(1)	
		
def find_button(driver, xpath_list, d):
	for pair in xpath_list:
		text, button = pair
		try:
			crime_text = driver.find_element_by_xpath(text).text
			if crime_text == "Crime":
				crime_measure = driver.find_element_by_xpath(text[:-2] + "3]").text
				d["Crime_Relative"] = crime_measure.split(" ")[0]
				print("\t{}".format(crime_measure)) 
				driver.find_element_by_xpath(button).click()
				return 0
		except:
			break
	return -1

def count_crime(driver, crime, xpath):
	try:
		text = driver.find_element_by_xpath(xpath).text
		if text == crime:
			driver.find_element_by_xpath(xpath).click()
			length = len(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")) - 1
			print("\t{}: {}".format(crime, length))
			return length
		else:
			print("\tText does not match button name for {} - setting to -2".format(crime))
			return -2
	except:
		print("\tCould NOT find {} - setting to -1".format(crime))
		return -1

def set_NA(d):
	d["Assault"] = -1
	d["Theft"] = -1
	d["Arrest"] = -1
	d["Vandalism"] = -1
	d["Burglary"] = -1
	d["Crime_Relative"] = -1
	print("\tSetting all crime values to -1")

def extract_crime_old(driver, d):
        try:
		try:
             		crime = driver.find_element_by_xpath("//button[@data-id='Theft']").click() #Currently this is used
		except:
			crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[1]/div/button').click()

                try:
                        theft = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                except:
			try:
                        	theft = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li") #And this one
			except:
				theft = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")

                d["theft"] = len(theft) - 1
        except:
		print("\tCould not find Theft")
                d["theft"] = "NA"

	sleep(3)

	try:
		try:
                	crime = driver.find_element_by_xpath("//button[@data-id='Assault']").click()
		except:
			crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[2]/div/button').click()
                try:
                        assault = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                except:
			try:
                        	assault = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
			except:
				assault = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")

                d["assault"] = len(assault) - 1
        except:
		print("\tCount not find Assault")
                d["assault"] = "NA"

        sleep(3)

        try:
		try:
                	crime = driver.find_element_by_xpath("//button[@data-id='Arrest']").click()
		except:
			crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[3]/div/button').click()

                try:
                        arrest = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                except:
			try:
                        	arrest = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
			except:
				arrest = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")

                d["arrest"] = len(arrest) - 1
        except:
		print("\tCount not find Arrest")
                d["arrest"] = "NA"

        sleep(3)

        try:
		try:
                	crime = driver.find_element_by_xpath("//button[@data-id='Vandalism']").click()
		except:
			crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[4]/div/button').click()
                try:
                        vandalism = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                except:
			try:
                        	vandalism = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
			except:
				vandalism = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")

                d["vandalism"] = len(vandalism) - 1
        except:
		print("\tCount not find Vandalism")
                d["vandalism"] = "NA"

        sleep(3)

        try:
		try:
                	crime = driver.find_element_by_xpath("//button[@data-id='Burglary']").click()
		except:
			crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[5]/div/button').click()

                try:
                        burglary = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                except:
			try:
                        	burglary = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
			except:
				burglary = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")
	
                d["burglary"] = len(burglary) - 1
        except:
		print("\tCould not find Burglary")
                d["burglary"] = "NA"

        d["crime_other"] = "NA"
