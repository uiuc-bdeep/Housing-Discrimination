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


def extract_rental_detail(driver, d):
	"""Extract rental detail such as number bedrooms and bathrooms, Sqft, Type of Housing, Year Built, etc.
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	try:
		property_detail = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split("\n")
	except:
		try:
			property_detail = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/ul').text.split("\n")
		except:
			try:
				property_detail = driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[1]/ul").text.split("\n")
				property_detail += driver.find_element_by_xpath("/html/body/div[7]/div[1]/div/div[2]/div[2]/ul").text.split("\n")
			except:
				try:
					property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[1]/ul").text.split("\n")
					property_detail += driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[2]/div/div[2]/ul").text.split("\n")
				except:
					try:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[3]/div[2]/div/div[1]/ul").text.split("\n")
					except:
						property_detail = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div/ul').text.split("\n")

	bedroom = ""
	bathroom = ""

	for detail in property_detail:
		if "bed" in detail.lower():
			bedroom = detail.rsplit(" ", 1)[0]
		elif "bath" in detail.lower():
			bathroom = detail.rsplit(" ", 2)[0]
		elif "day" in detail.lower():
			d["days"] = detail.split(" ")[0]

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
					try:
						property_detail = driver.find_element_by_xpath("/html/body/div[5]/div[3]/div[2]/div/div[1]/ul").text.split("\n")
					except:
						try:
					        	ul_path = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[2]/ul')
						except:
							try:
								try:
									ul_path = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[3]/ul')
								except:
									ul_path = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/ul')
                                                		li_options = ul_path.find_elements_by_tag_name("li")
                                                		property_detail = []
                                                		for option in li_options:
                                                    			property_detail.append(option.text)
							except:
								property_detail = []

	for s in property_detail:
		if "sqft" in s and "/sqft" not in s:
			d["sqft"] = s.split(" ")[0]
		elif "Built" in s:
			d["year"] = s.split(" ")[2]
		elif "Home" in s or "Apartment" in s or "Family" in s or "Townhouse" in s or "loft" in s.lower():
			d["type"] = s

def extract_rental_school(driver, d):
	"""Extract Assigned Schools score and get the average
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""
        try:
        	elementary_school_count = int(driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[3]').text.split(' ')[0])
        	middle_school_count = int(driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[4]').text.split(' ')[0])
        	high_school_count = int(driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[5]').text.split(' ')[0])
        	try:
	    		driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div').click()
        	except:
			try:
	   			driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div').click() 
			except:
				driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[4]/div').click()

        	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[1]/div/button'))).click()
        	sleep(3)
        	total = 0
        	for i in range(1, elementary_school_count + 1):
                	score = int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
                	total += score
        	d['elementary_school_count'] = elementary_school_count
        	d['elementary_school_average_score'] = float(total) / elementary_school_count

        	driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/div/button').click()
        	sleep(3)
        	total = 0
        	for i in range(1, middle_school_count + 1):
                	score = int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
                	total += score
        	d['middle_school_count'] = middle_school_count
        	d['middle_school_average_score'] = float(total) / middle_school_count

        	driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[3]/div/button').click()
        	sleep(3)
        	total = 0
        	for i in range(1, high_school_count + 1):
                	score = int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
                	total += score
        	d['high_school_count'] = high_school_count
        	d['high_school_average_score'] = float(total) / high_school_count
        	return

        except:
                print("New method unsuccessful")

	try:
		driver.find_element_by_xpath("//*[@id='schoolsCard']").click()
	except:	
		try:
			driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
		except:
			try:
				driver.refresh()
				driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
			except:
				try:
					extract.extract_sold_rental_school(driver, d)
                                        return
				except:
                                        try:
                                                driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]').click()
                                        except:
					        d["elementary_school_count"] = "NA"
					        d["elementary_school_average_score"] = "NA"
					        d["middle_school_count"] = "NA"
					        d["middle_school_average_score"] = "NA"
					        d["high_school_count"] = "NA"
					        d["high_school_average_score"] = "NA"
					        print("Unable to find any school info")
					        return
					
	try:
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
                try:
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

                except:
                        d["elementary_school_count"] = "NA"
                        d["elementary_school_average_score"] = "NA"
                        d["middle_school_count"] = "NA"
                        d["middle_school_average_score"] = "NA"
                        d["high_school_count"] = "NA"
                        d["high_school_average_score"] = "NA"
                        print("Unable to find any school info")



def extract_rental_crime(driver, d):
	"""Extract number of Crimes from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""

	try:
		driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[4]/div[2]/div[2]/div[2]").click()
	except:
		try:
			driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[3]/div[2]/div[2]/div[2]").click()
		except:
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
        		try:
				try:
                			crime = driver.find_element_by_xpath("//button[@data-id='Theft']").click()
				except:
					crime = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div[1]/div/button').click()

                		try:
                        		theft = driver.find_element_by_xpath("//ul[@data-testid='local-info-tab-cards-list']").find_elements_by_tag_name("li")
                		except:
					try:
                        			theft = driver.find_element_by_xpath("//ul[@data-testid='lil-tab-cards-list']").find_elements_by_tag_name("li")
					except:
						theft = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul').find_elements_by_tag_name("li")

                		d["theft"] = len(theft) - 1
        		except:
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
                		d["burglary"] = "NA"

        		d["crime_other"] = "NA"

	print("assult: " + str(d.get("assault", "NA")), "arrest: " + str(d.get("arrest", "NA")), "theft: " + str(d.get("theft", "NA")), "burglary: " + str(d.get("burglary", "NA")), "vandalism: " + str(d.get("vandalism", "NA")))


def extract_rental_shop_eat(driver, d):
	"""Extract Shop and Eat scores from Trulia
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	"""
	try:
		try:
			driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div/div').click() 
		except:
			driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[2]/button').click() #scroll it into view
				#ERROR: This button ^ is not clickable because something obscures it
			driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[6]/div/div').click()

		driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div/button').click() #restaurant button
		restaurant_counter = driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul')
		restaurants = len(restarurant_counter.find_elements_by_tag_name("li"))
		d["restaurant"] = restaurant
		print(d)
		return
	except:
		print("new shop method unsuccessful")
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
