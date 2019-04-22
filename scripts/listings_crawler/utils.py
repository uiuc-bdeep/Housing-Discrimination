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

def restart(crawler_log, debug_mode, start):
	print("argv was",sys.argv)
	print("sys.executable was", sys.executable)
	print("restart now")

	if not debug_mode:
		sleep(5)

	for proc in psutil.process_iter():
		if "firefox" in proc.name():
			proc.kill()
		if "geckodriver" in proc.name():
			proc.kill()

	if os.path.isfile(crawler_log) == True:
		with open(crawler_log) as f:
			lines = f.readlines() 
	else:
		lines = [start]

	print (sys.argv)
	arg = []

	find_start = False
	for i, n in enumerate(sys.argv):
		if n.isdigit() and not find_start:
			arg.append(str(int(lines[-1].rstrip())+1) if os.path.isfile(crawler_log) == True else lines[-1].rstrip())
			find_start = True
		else:
			arg.append(n)

	print(arg)
	os.execv(sys.executable, ['python'] + arg)

def start_firefox(URL, geckodriver_path, adblock_path, uBlock_path):
	DesiredCapabilities.FIREFOX["proxy"] = {
		"proxyType" : "pac",
		"proxyAutoconfigUrl" : "http://www.freeproxy-server.net/"
	}

	options = Options()
	options.add_argument("--headless")
	fp = webdriver.FirefoxProfile()
	fp.set_preference("general.useragent.override", UserAgent().random)
	fp.update_preferences()
	driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options, capabilities = webdriver.DesiredCapabilities.FIREFOX, executable_path = geckodriver_path)
	#driver = webdriver.Remote(desired_capabilities = webdriver.DesiredCapabilities.FIREFOX)

	driver.install_addon(adblock_path)
	driver.install_addon(uBlock_path)
	#driver.install_addon("I:\\adblock_plus-3.0.2-an+fx.xpi")
	#driver.install_addon("I:\\uBlock0@raymondhill.net.xpi")

	driver.wait = WebDriverWait(driver, 5)
	driver.delete_all_cookies()
	driver.get(URL)
	print(driver.title)
	return driver