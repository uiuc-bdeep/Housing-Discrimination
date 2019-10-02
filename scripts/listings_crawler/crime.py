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


def extract_rental_crime(driver, d):
	"""Extract number of Crimes from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	#d = {"theft": "NA", "burglary": "NA", "assault": "NA", "arrest": "NA", "vandalism": "NA", "crime_other": "NA"}
	try:
		driver.find_element_by_xpath("//*[@id='crimeCard']/div/div[2]").click()
	except:
		try:
			driver.find_element_by_xpath("//*[@id='__next']/div/section/div[1]/div[2]/div[3]/div[2]/div[1]/div/div[4]/button").click()
		except:
			try:
				driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[4]').click()
			except:
				try:
					driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[4]').click()
				except:
					print("Could not find Crime button")
					return 
	
	print("Crime button found")
	sleep(11)
	driver.save_screenshot("crime.png")

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
		print("Could not find Theft")
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
		print("Count not find Assault")
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
		print("Count not find assault")
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
		print("Count not find Vandalism")
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
		print("Could not find Burglary")
                d["burglary"] = "NA"

        d["crime_other"] = "NA"

	print("assult: " + str(d.get("assault", "NA")), "arrest: " + str(d.get("arrest", "NA")), "theft: " + str(d.get("theft", "NA")), "burglary: " + str(d.get("burglary", "NA")), "vandalism: " + str(d.get("vandalism", "NA")))
