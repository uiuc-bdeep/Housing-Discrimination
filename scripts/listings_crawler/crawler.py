"""Summary

Attributes:
    pollution (str): Description
    trulia (str): Description
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

from save_to_file import save_rental
from ejscreen.ejscreen import handle_ejscreen_input, extract_pollution_from_report
from extract.extract_data import extract_rental
from util.util import start_firefox, restart

trulia = "https://www.trulia.com"
pollution = "https://www3.epa.gov/myem/envmap/find.html"

def main(crawl_type, input_file, output_file, start, end, crawler_log, geckodriver_path, repair, debug_mode, adblock_path, uBlock_path):
	"""Main function to do the crawling
	
	Args:
	    crawl_type (List of String): default ["U"]. Can add ["A", "L"]
	    input_file (String): Name of the input file
	    output_file (String): Name of the output file
	    start (int): Starting index of the crawling
	    end (int): Ending index of the crawling
	    crawler_log (String): Name of the log
	    geckodriver_path (String): Path to the geckodriver
	    repair (Bool): Wheather this crawling is repair mode or not
	    debug_mode (Bool): Wheater this crawling is debug mode or not
	    adblock_path (String): Path to the adblock
	    uBlock_path (String): Path to the uBlock
	"""
	
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

			crawled_trulia = True
			driver.get(urls[i])
			print(driver.title)
			sleep(3)
			if "Real Estate, " in driver.title or "Not Found" in driver.title:
				print ("404 in trulia")
				crawled_trulia = False
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
						print("Reached EXCEPT after extract_rental")
				 		restart(crawler_log, debug_mode, start)
				if flag == False:
					crawled_trulia = False
			elif "this page" in driver.title.lower():
				print ("Being blocked from accessing Trulia. Restarting...")
				driver.quit()
				restart(crawler_log, debug_mode, start)
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

			driver.execute_script("window.open('https://ejscreen.epa.gov/mapper/mobile/', 'new_tab')")
			sleep(5)
			driver.switch_to_window(driver.window_handles[1])

			# if (len(address) < 10):
			# 	save_data(d, urls[i], output_file, crawl_type)
			# 	with open(crawler_log, "ab") as log:
			# 		filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
			# 		filewriter.writerow([i])
			# 	continue

			try:
				handle_ejscreen_input(driver, address)
				sleep(5)
				extract_pollution_from_report(driver, d)
				#print("Skipping ejscreen")
			except:
				if debug_mode:
					driver.quit()
					for proc in psutil.process_iter():
						if proc.name() == "firefox" or proc.name() == "geckodriver":
							proc.kill()
					raise
				else:
					print("cannot extract pollution. Restarting")
					driver.quit()
					restart(crawler_log, debug_mode, start)

			save_rental(d, urls[i], output_file)

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
			restart(crawler_log, debug_mode, start)

	driver.quit()

if __name__ == "__main__":
	# <cmd + alt + '> will update a docstring for the first module/class/function preceding the cursor.
	# <cmd + alt + shift + '> will update docstrings for every class/method/function in the current file
	import argparse
	import platform
	from argparse import RawTextHelpFormatter

	parser = argparse.ArgumentParser(description = 'Crawl Trulia apartment listings and ejscreen given Trulia URLs or Address (optional)', formatter_class=RawTextHelpFormatter, epilog = "Note that input_file must be a CSV file that contains a column 'URL'. \nIt can also contain (A)ddress or (L)atLon")
	#parser.add_argument("type", help = "Whether the input file contains column (A)ddress or (L)atLon", choices = ["U", "A", "L"], nargs = "+")
	parser.add_argument("input_file", help = "Path of input file")
	parser.add_argument("output_file", help = "Path of output file")
	parser.add_argument("log", help = "Name of the log")
	parser.add_argument("start", help = "Start of Input file", type = int)
	parser.add_argument("end", help = "End of Input file", type = int)
	parser.add_argument("--repair", help = "whether we try to repair the Trulia listings in the input_file or not.\noutput_file will be ignored if this is enabled", type = bool, default = False)
	parser.add_argument("--debug", help = "Turn on debug mode or not. Default False", type = bool, default = False)
	#parser.add_argument("--geckodriver", help = "Path of geckodriver.\nDefault ../../stores/", default = "../../stores/")
	#parser.add_argument("--adblock", help = "Path of adblock.xpi (need ABSOLUTE PATH!!).\nDefault /home/ubuntu/Housing-Discrimination/stores/", default = "/home/ubuntu/Housing-Discrimination/stores/")
	#parser.add_argument("--uBlock", help = "Path of uBlock0.xpi (need ABSOLUTE PATH!!).\nDefault /home/ubuntu/Housing-Discrimination/stores/", default = "/home/ubuntu/Housing-Discrimination/stores/")

	args = parser.parse_args()

	crawl_type = ["U"]
	#if "U" not in args.type:
	#	sys.exit("Must at least choose U for URL. A and L are optional. Aborting.")

	if args.debug:
		print(args)

	#geckodriver_path = args.geckodriver + "geckodriver" + (".exe" if "Windows" in platform.system() else "")
	geckodriver_path = '/usr/bin/geckodriver'
	if not os.path.exists(geckodriver_path):
		sys.exit("geckodriver does not exist at {}\nAborting.".format(geckodriver_path))

	#adblock_path = args.adblock + "adblock_plus-3.3.1-an+fx.xpi"
	adblock_path = "/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi"
	if not os.path.exists(adblock_path):
		sys.exit("adblock_plus does not exist at {}\nAborting.".format(adblock_path))

	#uBlock_path = args.uBlock + "uBlock0@raymondhill.net.xpi"
	uBlock_path = "/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi"
	if not os.path.exists(uBlock_path):
		sys.exit("uBlock does not exist at {}\nAborting.".format(uBlock_path))

	try:
		main(crawl_type, args.input_file, args.output_file, args.start, args.end, args.log, geckodriver_path, args.repair, args.debug, adblock_path, uBlock_path)
	except:
		for proc in psutil.process_iter():
			if proc.name() == "firefox" or proc.name() == "geckodriver":
				proc.kill()
		raise
