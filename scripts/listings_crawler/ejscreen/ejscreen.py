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

def wait_for(condition_function):
	start_time = time.time() 
  	while time.time() < start_time + 60: 
    		if condition_function(): 
      			return True 
    		else: 
      			time.sleep(0.1) 
  	raise Exception('Timeout waiting')

def handle_ejscreen_input(driver, address):
	"""Send Address to ejscreen
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    address (String): String of the address
	
	Returns:
	    Bool: True if success, False otherwise
	"""
	
	sleep(5)
	print(address)
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div[1]/a'))).click()

	sleep(3)
	driver.save_screenshot('screenie-menu.png')
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div[1]/ul/li[1]/a'))).click()
	#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='webmap-toolbar-center']/span[1]"))).click()
	sleep(2)
	text = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchNavDiv"]/div/div[2]/form/input')))
        text.send_keys(address)
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchNavDiv"]/div/div[3]'))).click()
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="infowg"]/form/input[7]'))).click()
	driver.switch_to_window(driver.window_handles[-1])
	#flag = True
	#while flag:
	#	try:
	#		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='dijit_anchorMenuItem_0_text']"))).click()
	#		flag = False
	#	except:
	#		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='webmap-toolbar-center']/span[1]"))).click()
	#		print("reclick")
	#sleep(2)

	#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/input[2]"))).click()
	#text = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/div[2]/input[1]")))
	#text.send_keys(address)
	#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/div[2]/input[2]"))).click()
	#sleep(3)
	#f = True
	#while f == True:
	#	try:
	#		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='ejsrpt']"))).click()
	#		f = False
	#	except:
	#		print("zooming out")
	#		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='map_zoom_slider']/div[2]"))).click()
	#		sleep(3)
	return True

def extract_pollution_from_report(driver, d):
	driver.save_screenshot("report.png")
	info =  WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="headerDiv"]'))).text
	print(info)
	info = info.split("\n")
	d["epa_region"] = info[1].split(" ")[-1]
        population = info[2].split(" ")[-1]
        d["population"] = sub(r'[^\d.]', '', population)
        d["input area(sq. miles)"] = info[3].split(" ")[-1]
        d["Particulate Matter"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="envindDiv"]/table/tbody/tr[3]/td[2]'))).text
        d["Ozone"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="envindDiv"]/table/tbody/tr[4]/td[2]'))).text
        d["NATA* Diesel PM"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="envindDiv"]/table/tbody/tr[5]/td[2]'))).text
        d["NATA* Air Toxics Cancer Risk"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[6]/td[2]"))).text
        d["NATA* Respiratory Hazard Index"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[7]/td[2]"))).text
        d["Traffic Proximity and Volume"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[8]/td[2]"))).text
        d["Lead Paint Indicator"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[9]/td[2]"))).text
        d["Superfund Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[10]/td[2]"))).text
        d["RMP Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[11]/td[2]"))).text
        d["Hazardous Waste Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[12]/td[2]"))).text
        d["Wastewater Discharge Indicator"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envindDiv']/table/tbody/tr[13]/td[2]"))).text

        d["Demographic Index"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[3]/td[2]'))).text.replace("%","")
        d["Minority Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[4]/td[2]'))).text.replace("%","")
        d["Low Income Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[5]/td[2]'))).text.replace("%","")
        d["Linguistically Isolated Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[6]/td[2]'))).text.replace("%","")
        d["Population with Less Than High School Education"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[7]/td[2]'))).text.replace("%","")
        d["Population under Age 5"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[8]/td[2]'))).text.replace("%","")
        d["Population over Age 64"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="demogDiv"]/table/tbody/tr[9]/td[2]'))).text.replace("%","")

        driver.close()
        driver.switch_to_window(driver.window_handles[1])


def extract_pollution(driver, d):
	"""Extract the pollution data from ejscreen
	
	Args:
	    driver (Firefox Driver): The Firefox driver
	    d (dict): Dictionary that holds all the data
	
	Returns:
	    None
	"""

	try:
		driver.switch_to_window(driver.window_handles[2])
	except:
		print("reclicking")
		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='ejsrpt']"))).click()
	sleep(20)

	f = True
	while f == True:
		try:
			info = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//*[@id='headerDiv']"))).text
			f = False
		except:
			print ("refreshing")
			driver.refresh()

	text = driver.find_element_by_xpath("//*[@id='EJindexDiv']").text
	if "too small" in text:
		print("area too small")
		driver.close()
		driver.switch_to_window(driver.window_handles[1])
		return
	#f = True
	#while f == True:
	#  try:
	
	print(info)
	while len(info) < 3:
		#print("trying")
		info = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='headerDiv']"))).text
	info = info.split("\n")

	d["lat"] = info[0].split(" ")[-1].split(",")[0]
	d["lon"] = info[0].split(" ")[-1].split(",")[1]
	d["epa_region"] = info[1].split(" ")[-1]
	population = info[2].split(" ")[-1]
	d["population"] = sub(r'[^\d.]', '', population)
	d["input area(sq. miles)"] = info[3].split(" ")[-1]

	d["Particulate Matter"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[3]/td[2]"))).text
	d["Ozone"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[4]/td[2]"))).text
	d["NATA* Diesel PM"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[5]/td[2]"))).text
	d["NATA* Air Toxics Cancer Risk"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[6]/td[2]"))).text
	d["NATA* Respiratory Hazard Index"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[7]/td[2]"))).text
	d["Traffic Proximity and Volume"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[8]/td[2]"))).text
	d["Lead Paint Indicator"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[9]/td[2]"))).text
	d["Superfund Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[10]/td[2]"))).text
	d["RMP Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[11]/td[2]"))).text
	d["Hazardous Waste Proximity"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[12]/td[2]"))).text
	d["Wastewater Discharge Indicator"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[13]/td[2]"))).text

	d["Demographic Index"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[15]/td[2]"))).text.replace("%","")
	d["Minority Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[16]/td[2]"))).text.replace("%","")
	d["Low Income Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[17]/td[2]"))).text.replace("%","")
	d["Linguistically Isolated Population"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[18]/td[2]"))).text.replace("%","")
	d["Population with Less Than High School Education"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[19]/td[2]"))).text.replace("%","")
	d["Population under Age 5"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[20]/td[2]"))).text.replace("%","")
	d["Population over Age 64"] = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='envdemogDiv']/table/tbody/tr[21]/td[2]"))).text.replace("%","")

	driver.close()
	driver.switch_to_window(driver.window_handles[1])
