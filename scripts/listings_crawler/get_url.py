import os
import sys
import os.path
import csv
import datetime
import psutil
import random
import json
import pandas as pd

from subprocess import call
from sys import exit
from time import sleep
from re import sub

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
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.proxy import Proxy

from utils import start_firefox, restart
trulia = "https://www.trulia.com"

# def start_firefox(URL, geckodriver_path):
# 	DesiredCapabilities.FIREFOX["proxy"] = {
# 		"proxyType" : "pac",
# 		"proxyAutoconfigUrl" : "http://www.freeproxy-server.net/"
# 	}

# 	options = Options()
# 	options.add_argument("--headless")
# 	fp = webdriver.FirefoxProfile()
# 	fp.set_preference("general.useragent.override", UserAgent().random)
# 	fp.update_preferences()
# 	driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options, capabilities = webdriver.DesiredCapabilities.FIREFOX, executable_path = geckodriver_path)
# 	#driver = webdriver.Remote(desired_capabilities = webdriver.DesiredCapabilities.FIREFOX)

# 	driver.install_addon("/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi")
# 	driver.install_addon("/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi")
# 	#driver.install_addon("I:\\adblock_plus-3.0.2-an+fx.xpi")
# 	#driver.install_addon("I:\\uBlock0@raymondhill.net.xpi")

# 	driver.wait = WebDriverWait(driver, 5)
# 	driver.delete_all_cookies()
# 	driver.get(URL)
# 	print(driver.title)
# 	return driver

# def restart(crawler_log, debug_mode):
# 	import sys
# 	print("argv was",sys.argv)
# 	print("sys.executable was", sys.executable)
# 	print("restart now")

# 	if not debug_mode:
# 		sleep(300)

# 	for proc in psutil.process_iter():
# 		if "firefox" in proc.name():
# 			proc.kill()
# 		if "geckodriver" in proc.name():
# 			proc.kill()

# 	import os

# 	if os.path.isfile(log_name) == True:
# 		with open(log_name) as f:
# 			lines = f.readlines() 
# 	else:
# 		lines = [start]

# 	print (sys.argv)
# 	arg = []

# 	for i, n in enumerate(sys.argv):
# 		if i == 1:
# 			arg.append(str(int(lines[-1].rstrip())+1) if os.path.isfile(log_name) == True else lines[-1].rstrip())
# 		else:
# 			arg.append(n)

# 	print arg
# 	os.execv(sys.executable, ['python'] + arg)

def query(driver, pro_type, address):
	driver.get("https://www.trulia.com/")

	# Address bar
	city_input_cond = EC.presence_of_element_located((By.XPATH, "//*[@id='homepageSearchBoxTextInput']"))
	city_input_handle = WebDriverWait(driver, 10).until(city_input_cond)

	if pro_type == "buy":
		driver.find_element_by_xpath("//*[@id='homepageApp']/div/div[1]/div/div/div[1]/div/button[1]").click()
	elif pro_type == "rent":
		driver.find_element_by_xpath("//*[@id='homepageApp']/div/div[1]/div/div/div[1]/div/button[2]").click()
	elif pro_type == "sold":
		driver.find_element_by_xpath("//*[@id='homepageApp']/div/div[1]/div/div/div[1]/div/button[3]").click()

	sleep(3)

	city_input_handle.send_keys(address)

	# Search button
	driver.find_element_by_xpath("//*[@id='homepageApp']/div/div[1]/div/div/div[2]/div/div/div[1]/button[1]").click()

	sleep(5)

	print(driver.current_url)

	return driver.current_url

def main(input_file, output_file, start, end, crawler_log, geckodriver_path, debug_mode, adblock_path, uBlock_path):
	urls = []

	df = pd.read_csv(input_file)

	driver = start_firefox(trulia, geckodriver_path, adblock_path, uBlock_path)
	sleep(5)

	try:
		driver.switch_to_window(driver.window_handles[1])
		driver.close()
		driver.switch_to_window(driver.window_handles[0])
	except:
		print ("switching window failed??")
		driver.quit()
		restart(crawler_log, debug_mode, start)

	i = int(start)
	count = 0
	for address in df["full"][int(start):int(end)]:
		if count == 60:
			os.system("sudo tmpreaper -m 1h /tmp")
			restart()
		try:
			print(i, address)

			# url1 = query(driver, "buy", address)
			url1 = ""
			url2 = query(driver, "rent", address)
			url3 = ""
			# url3 = query(driver, "sold", address)

			urls.append([url1, url2, url3])

			with open(output_file, "ab") as log:
		  		filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		  		filewriter.writerow([url1, url2, url3])
			with open(crawler_log, "ab") as log:
		  		filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		  		filewriter.writerow([i])

			i += 1
			count += 1
			
		except:
			if debug_mode:
				driver.quit()
				for proc in psutil.process_iter():
					if proc.name() == "firefox" or proc.name() == "geckodriver":
						proc.kill()
				raise
			else:
				driver.quit()
				restart(crawler_log, debug_mode, start)
	driver.quit()

if __name__ == "__main__":
	import argparse
	import platform
	from argparse import RawTextHelpFormatter

	parser = argparse.ArgumentParser(description = 'Crawl Trulia URLs given addresses', formatter_class = RawTextHelpFormatter)
	parser.add_argument("input_file", help = "Path of input file")
	parser.add_argument("output_file", help = "Path of output file")
	parser.add_argument("start", help = "Start of Input file", type = int)
	parser.add_argument("end", help = "End of Input file", type = int)
	parser.add_argument("log", help = "Name of the log")
	parser.add_argument("--debug", help = "Turn on debug mode or not. Default False", type = bool, default = False)
	parser.add_argument("--geckodriver", help = "Path of geckodriver.\nDefault ../../stores/", default = "../../stores/")
	parser.add_argument("--adblock", help = "Path of adblock.xpi.\nDefault ../../stores/", default = "../../stores/")
	parser.add_argument("--uBlock", help = "Path of uBlock0.xpi.\nDefault ../../stores/", default = "../../stores/")

	args = parser.parse_args()

	if args.debug:
		print(args)

	geckodriver_path = args.geckodriver + "geckodriver" + (".exe" if "Windows" in platform.system() else "")
	if not os.path.exists(geckodriver_path):
		sys.exit("geckodriver does not exist in path. Aborting.")

	adblock_path = args.adblock + "adblock_plus-3.3.1-an+fx.xpi"
	if not os.path.exists(adblock_path):
		sys.exit("adblock_plus does not exist in path. Aborting.")

	uBlock_path = args.uBlock + "uBlock0@raymondhill.net.xpi"
	if not os.path.exists(uBlock_path):
		sys.exit("uBlock does not exist in path. Aborting.")
	try:
		main(args.input_file, args.output_file, args.start, args.end, args.log, geckodriver_path, args.debug, adblock_path, uBlock_path)
	except:
		for proc in psutil.process_iter():
			if proc.name() == "firefox" or proc.name() == "geckodriver":
				proc.kill()
		raise