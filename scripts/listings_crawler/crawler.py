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

from save_to_file import save_rental
from ejscreen import handle_ejscreen_input, extract_pollution
from extract_data import extract_rental

trulia = "https://www.trulia.com"
pollution = "https://www3.epa.gov/myem/envmap/find.html"

def restart():
	import sys
	print("argv was",sys.argv)
	print("sys.executable was", sys.executable)
	print("restart now")
	sleep(300)

	for proc in psutil.process_iter():
		if "firefox" in proc.name():
			proc.kill()
		if "geckodriver" in proc.name():
			proc.kill()

	import os

	if os.path.isfile(city + number + ".log") == True:
		with open(city + number + ".log") as f:
			lines = f.readlines() 
	else:
		lines = [sys.argv[2]]

	print (sys.argv)
	arg = []

	for i, n in enumerate(sys.argv):
		if i == 2:
			arg.append(str(int(lines[-1].rstrip())+1) if os.path.isfile(city + number + ".log") == True else lines[-1].rstrip())
		else:
			arg.append(n)

	print(arg)
	os.execv(sys.executable, ['python'] + arg)

def start_firefox(URL, geckodriver_path):
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

	driver.install_addon("/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi")
	driver.install_addon("/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi")
	#driver.install_addon("I:\\adblock_plus-3.0.2-an+fx.xpi")
	#driver.install_addon("I:\\uBlock0@raymondhill.net.xpi")

	driver.wait = WebDriverWait(driver, 5)
	driver.delete_all_cookies()
	driver.get(URL)
	print(driver.title)
	return driver

def main(crawl_type, input_file, output_file, start, end, crawler_log, geckodriver_path, repair, debug_mode):
	# return None
	# crawl_type = sys.argv[1]
	# start = sys.argv[2]
	# end = sys.argv[3]
	# number = sys.argv[4]
	# city = sys.argv[5]

	# if crawl_type == "sold":
	# 	input = "/home/ubuntu/trulia/stores/LA.csv"
	# 	output = "/home/ubuntu/trulia/stores/LA" + str(number) + ".csv"
	# 	#input = "/home/ubuntu/trulia/stores/urls.csv"
	# 	#output = "/home/ubuntu/trulia/stores/availunit_houses" + str(number) + ".csv"
	# elif crawl_type == "new":
	# 	input = "/home/ubuntu/share/projects/Trulia/stores/" + city + "/new_listing/" + city.lower() + "_new_urls.csv"
	# 	output = "/home/ubuntu/share/projects/Trulia/stores/" + city + "/new_listing/" + city.lower() + "_new_house.csv"
	# elif crawl_type == "rental":
	# 	input = "/home/ubuntu/trulia/stores/" + city + ".csv"
	# 	output = "/home/ubuntu/trulia/stores/" + city + "_rental_houses" + str(number) + ".csv"

	driver = start_firefox(trulia, geckodriver_path)

	sleep(5)

	try:
		driver.switch_to_window(driver.window_handles[1])
		driver.close()
		driver.switch_to_window(driver.window_handles[0])
	except:
		print ("switching window failed??")
		driver.quit()
		restart()

	# if city == "ej":
	# 	workbook = []
	# 	with open("/home/ubuntu/trulia/stores/availunit_address.csv", 'rU') as f:
	# 		d = [row for row in csv.reader(f.read().splitlines())]
	# 		for i in d:
	# 			s = i[0]
	# 			workbook.append(s)

	df = pd.read_csv(input_file)

	urls = df["URL"]

	if "L" in crawl_type:
		location = df["LatLon"]

	if "A" in crawl_type:
		address_col = df["Address"]

	if repair:
		df['Sqft'] = df['Sqft'].astype(str)
		df['Type'] = df['Type'].astype(str)
		df["Address"] = df["Address"].astype(str)
		df["City"] = df["City"].astype(str)
		df["State"] = df["State"].astype(str)
		df["Zip_Code"] = df["Zip_Code"].astype(str)
		df["Year"] = df["Year"].astype(str)
		df["Days_on_Trulia"] = df["Days_on_Trulia"].astype(str)
		df["Bedroom_min"] = df['Bedroom_min'].astype(str)
		df["Bedroom_max"] = df['Bedroom_max'].astype(str)
		df["Bathroom_min"] = df['Bathroom_min'].astype(str)
		df["Bathroom_max"] = df['Bathroom_max'].astype(str)
		df["Phone_Number"] = df['Phone_Number'].astype(str)
		df["URL"] = df["URL"].astype(str)

	try:
		for i in range(int(start), int(end)):
			print(i)
			print(urls[i])
			driver.delete_all_cookies()
			d = {}
			# crawled_trulia = False

			# if "sold" in urls[i]:
			# 	crawled_trulia = True
			# 	driver.get(urls[i])
			# 	print(driver.title)
			# 	sleep(3)
			# 	flag = extract_data(driver, d, crawl_type)
			# 	if flag != False:
			# 	  sleep(3)
			# 	  extract_school_and_crime(driver, d)
			# 	else:
			# 	  crawled_trulia = False
			# else:

			crawled_trulia = True
			driver.get(urls[i])
			print(driver.title)
			sleep(3)
			if "Real Estate, " in driver.title or "Not Found" in driver.title:
				print ("404 in trulia")
				crawled_trulia = False
			# elif ("rental" in driver.current_url or "Rent" in driver.title) and "Not Disclosed" not in driver.title:
			elif "Trulia" in driver.title:
				print ("Start crawling")
				try:
					if repair:
						flag = extract_rental(driver, d, "R", address_col[i], df, i)
					elif "A" in crawl_type:
						flag = extract_rental(driver, d, "A", address_col[i], index = i)
					else:
						flag = extract_rental(driver, d, "U")
				except:
					if debug_mode:
						driver.quit()
						for proc in psutil.process_iter():
							if proc.name() == "firefox" or proc.name() == "geckodriver":
								proc.kill()
						raise
					else:
				 		driver.quit()
				 		restart()
				if flag == False:
					crawled_trulia = False
			elif "this page" in driver.title.lower():
				print ("Being blocked from accessing Trulia. Restarting...")
				driver.quit()
				restart()
			else:
				crawled_trulia = False
				address = driver.title.split(" - ")[0]
				print("Trulia is not available. Continuing")

			print("Trulia crawling done. Crawling ejscreen now")

			if repair:
				df.to_csv(input_file, index = False)
				with open(crawler_log, "ab") as log:
					filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
					filewriter.writerow([i])
				print("Repair done. going Next...")
				sleep(random.randint(10,40))
				continue
			else:
				if "L" in crawl_type:
					address = location[i]
				elif "A" in crawl_type:
					address = address_col[i]
				elif "A" not in crawl_type:
					if crawled_trulia == False:
						address = driver.title.split(" - ")[0]
						if address.find("#") != -1:
							address = address[:address.find("#")]
						else:
							address = address[:address.find("For")]
					else:
						if d["address"].find('#') != -1:
							add = d["address"][:d["address"].find('#')]
						else:
							add = d["address"]
							address = add + ", " + d["city"] + ", " + d["state"] + " " + d["zip code"]
					if crawled_trulia == False and "Real Estate, " in driver.title:
						address = "NA"

			driver.execute_script("window.open('https://ejscreen.epa.gov/mapper/', 'new_tab')")
			sleep(5)
			driver.switch_to_window(driver.window_handles[1])

			# if (len(address) < 10):
			# 	save_data(d, urls[i], output_file, crawl_type)
			# 	with open(crawler_log, "ab") as log:
			# 		filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
			# 		filewriter.writerow([i])
			# 	continue

			# try:
			# 	handle_ejscreen_input(driver, address)
			# 	sleep(5)
		 # 		extract_pollution(driver, d)
		 # 	except:
		 # 		driver.quit()
		 # 		restart()

			# save_rental(d, urls[i], output_file)

			with open(crawler_log, "ab") as log:
			  filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
			  filewriter.writerow([i])
		    
			driver.close()
			driver.switch_to_window(driver.window_handles[0])

			sleep(random.randint(10,40))
	except:
		if debug_mode:
			driver.quit()
			for proc in psutil.process_iter():
				if proc.name() == "firefox" or proc.name() == "geckodriver":
					proc.kill()
			raise
		else:
			driver.quit()
			restart()

	driver.quit()
	return None

if __name__ == "__main__":
	# <cmd + alt + '> will update a docstring for the first module/class/function preceding the cursor.
	# <cmd + alt + shift + '> will update docstrings for every class/method/function in the current file
	import argparse
	import platform
	from argparse import RawTextHelpFormatter

	parser = argparse.ArgumentParser(description = 'Crawl Trulia apartment listings and ejscreen given Trulia URLs or Address (optional)', formatter_class=RawTextHelpFormatter, epilog = "Note that input_file must be a CSV file that contains a column 'URL'. \nIt can also contain (A)ddress or (L)atLon")
	parser.add_argument("type", help = "Whether the input file contains column (A)ddress or (L)atLon", choices = ["A", "L"], nargs = "+")
	parser.add_argument("input_file", help = "Path of input file")
	parser.add_argument("output_file", help = "Path of output file")
	parser.add_argument("start", help = "Start of Input file", type = int)
	parser.add_argument("end", help = "End of Input file", type = int)
	parser.add_argument("log", help = "Name of the log")
	parser.add_argument("--repair", help = "whether we try to repair the Trulia listings in the input_file or not.\noutput_file will be ignored if this is enabled", type = bool, default = False)
	parser.add_argument("--debug", help = "Turn on debug mode or not. Default False", type = bool, default = False)
	parser.add_argument("--geckodriver", help = "Path of geckodriver.\nDefault current directory", default = ".")
	args = parser.parse_args()

	if args.debug:
		print(args)

	if args.geckodriver:
		geckodriver_path = args.geckodriver + "geckodriver" + (".exe" if "Windows" in platform.system() else "") 
		if not os.path.exists(geckodriver_path):
			sys.exit("geckodriver does not exist in path. aborting.")

	try:
		main(args.type, args.input_file, args.output_file, args.start, args.end, args.log, geckodriver_path, args.repair, args.debug)
	except:
		for proc in psutil.process_iter():
			if proc.name() == "firefox" or proc.name() == "geckodriver":
				proc.kill()
		raise