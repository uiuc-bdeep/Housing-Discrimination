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

def extract_sold_school(driver, d):
        """Extract Assigned Schools score and get the average

        Args:
            driver (Firefox Driver): The Firefox driver
            d (dict): Dictionary that holds all the data
        """
	print("School off market")
        for i in range(3, 6):
                try:
                        text = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div/div[{}]'.format(i)).text.split(' ')
                        count = int(text[0])
                        key = "{}_school_count".format(text[1].lower())
                        d[key] = count
                        print(key, count)
                except:
                        print("Not all schools in the area")
                        break
        if d != {}:
                try:
                        if driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div/div[2]').text == "Schools":
                                driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[3]/div').click()
                                print("Clicked School")
                                sleep(3)
				compute_averages(driver, d)
                                return 0
                except:
                        print("ERROR - Not able to click school")
        else:
                print("Nothing added to d")
        return 1

def extract_rental_school(driver, d):
	"""Extract Assigned Schools score and get the average
	
	Args:
            driver (Firefox Driver): The Firefox driver
            d (dict): Dictionary that holds all the data
	"""
	print("School on market")
	for i in range(3, 6):
		try:
                	text = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[{}]'.format(i)).text.split(' ')
			count = int(text[0])
			key = "{}_school_count".format(text[1].lower())
			d[key] = count
                	print(key, count)
            	except:
                	print("Not all schools in the area")
			break
        if d != {}:
            	try:
                	if driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div/div[2]').text == "Schools":
                        	driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[3]/div').click()
                        	print("Clicked School")
				sleep(3)
				compute_averages(driver, d)
                        	return 0
            	except:
                	print("ERROR - Not able to click school")
        else:
            	print("Nothing added to d")
        return 1

def compute_averages(driver, d):
	if "high_school_count" in d.keys():
		high_avg = high_school_average(driver, d["high_school_count"])
		d["high_school_average_score"] = high_avg
		print("high school average: {}".format(high_avg))
	else:
		d["high_school_count"] = 0
		d["high_school_average_score"] = 0
	if "middle_school_count" in d.keys():
		middle_avg = middle_school_average(driver, d["middle_school_count"])
		d["middle_school_average_score"] = middle_avg
		print("middle school average: {}".format(middle_avg))
	else:
		d["middle_school_count"] = 0
		d["middle_school_average_score"] = 0
	if "elementary_school_count" in d.keys():
		elem_avg = elem_school_average(driver, d["elementary_school_count"])
		print("elementary school average: {}".format(elem_avg))
	else:
		d["elementary_school_count"] = 0
		d["elementary_school_average_score"] = 0

def high_school_average(driver, count):
        #if driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[3]/div/button/div').text == "High":
	driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[3]/div/button').click()
	total = 0
	for i in range(1, count + 1):
		total += int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
	avg = float(total) / count
	return round(avg, 3)

def middle_school_average(driver, count):
        driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/div/button').click()
        total = 0
        for i in range(1, count + 1):
                total += int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
        avg = float(total) / count
        return round(avg, 3)

def elem_school_average(driver, count):
        driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/div[3]/div/div/div/div[1]/div/button').click()
        total = 0
        for i in range(1, count + 1):
                total += int(driver.find_element_by_xpath('//*[@id="modal-container"]/div/div[2]/div[2]/div/ul/li[{}]/div[1]/div/div/div[1]/div/span[1]/b'.format(i)).text)
        avg = float(total) / count
        return round(avg, 3)

def extra(driver, d):

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

def extra_school(driver, d):
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

