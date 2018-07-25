import os
import sys
import os.path
import csv
import datetime
import psutil
import random
import json

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
trulia = "https://www.trulia.com"
pollution = "https://www3.epa.gov/myem/envmap/find.html"

def restart(blocked = False):
	#if blocked == True:
	#	print "got blocked. Sleeping"
	#	sleep(2700)
	#	print "restarting"
	import sys
	print("argv was",sys.argv)
	print("sys.executable was", sys.executable)
	print("restart now")

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

	print arg
	os.execv(sys.executable, ['python'] + arg)

def wait_and_get(browser, cond, maxtime): 
	flag = True

	while flag:
		try: 
			ret = WebDriverWait(browser, maxtime).until(cond)
			sleep(2)
			ret = WebDriverWait(browser, maxtime).until(cond)
			flag = False
			return ret
		except TimeoutException:
			print "Time out"
			flag = False
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True
			if not flag:
				try:
					browser.find_elements_by_id("searchID").click()
					flag = True
				except:
					print "Time out without pop-ups. Exit."
					exit()


		except ElementNotVisibleException:
			print "Element Not Visible, presumptuously experienced pop-ups"
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True

def start_firefox(URL):
	DesiredCapabilities.FIREFOX["proxy"] = {
		"proxyType" : "pac",
		"proxyAutoconfigUrl" : "http://www.freeproxy-server.net/"
	}

	options = Options()
	options.add_argument("--headless")
	fp = webdriver.FirefoxProfile()
	fp.set_preference("general.useragent.override", UserAgent().random)
	fp.update_preferences()
	driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options, capabilities = webdriver.DesiredCapabilities.FIREFOX,executable_path = '/usr/local/bin/geckodriver')
	#driver = webdriver.Remote(desired_capabilities = webdriver.DesiredCapabilities.FIREFOX)

	driver.install_addon("/home/ubuntu/trulia/stores/adblock_plus-3.0.2-an+fx.xpi")
	driver.install_addon("/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi")
	#driver.install_addon("I:\\adblock_plus-3.0.2-an+fx.xpi")
	#driver.install_addon("I:\\uBlock0@raymondhill.net.xpi")

	driver.wait = WebDriverWait(driver, 5)
	driver.delete_all_cookies()
	driver.get(URL)
	print driver.title
	return driver#, display

def extract_data(driver, d, crawl_type):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	sleep(3)

	try:
		#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@data-role='address']"))).text
		address = driver.find_element_by_xpath("//*[@data-role='address']").text
		d["address"] = address
	except:
		print("Address Not Disclosed")
		d["address"] = "Address Not Disclosed"
		return False

	if crawl_type != "sold":
	  try:
	    agent_name = driver.find_element_by_xpath("//*[@id='topPanelLeadFormContainer']/div/div/form/div[1]/div[1]/div[1]/img").get_attribute("alt").split(",")[0]
	    print(agent_name)
	    d["agent_name"] = agent_name
	  except:
	    print("agent unavailable")
	    d["agent_name"] = "NA"

	city_state = driver.find_element_by_xpath("//*[@data-role='cityState']").text
	city, state = city_state.split(", ")
	print(state)
	state, zip_code = state.split(" ")
	d["city"] = city
	d["state"] = state
	d["zip code"] = "\"" + zip_code + "\""

	price = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]").text.split("\n")[1]
	d["price"] = sub(r'[^\d.]', '', price)


	if crawl_type != "sold":
		details = driver.find_element_by_xpath("//div[7]/div[2]/div/div[2]/div[1]").text.split("\n")
	else:
		#d["sold_on"] = " ".join(driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]/div/div[1]/div/span[3]").text.split(" ")[1:])
		try:
			details = driver.find_element_by_xpath("//div[7]/div[3]/div/div[2]/div[1]").text.split("\n")
		except:
			print("It's not sold")
			return False

	for detail in details:
		if "Bed" in detail:
			d["bedroom"] = detail.split(" ")[0]
		if "Bath" in detail:
			d["bathroom"] = detail.split(" ")[0]
		if "Built in " in detail:
			d["year"] = detail.split(" ")[-1]
		if crawl_type != "sold":
			if "days" in detail:
				d["days"] = detail.split(" ")[0]
	home = details[0]
	d["type"] = home

	try:
		details = driver.find_element_by_xpath("//div[7]/div[2]/div/div[2]/div[2]").text.split("\n")
	except:
		print("house already sold")
		if crawl_type == "sold":
			details = driver.find_element_by_xpath("//div[7]/div[3]/div/div[2]/div[2]").text.split("\n")
		else:
			return False

	for detail in details:
		if "/sqft" in detail:
			d["dolloar_per_sqft"] = sub(r'[^\d.]', '', detail.split("/")[0])
		if " sqft" in detail:
			d["sqft"] = sub(r'[^\d.]', '', detail.split(" ")[0])
		if "lot size" in detail:
			d["lot_size"] = sub(r'[^\d.]', '', detail.split(" ")[0])
			d["lot_size_unit"] = detail.split(" ")[1]
		if "view" in detail:
			d["views"] = detail.split(" ")[0]

	sleep(3)

	if crawl_type == "sold":
		ele = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[7]/div[3]/div/div[6]"))).text.split("\n")[3:]
		i = 0
		f = False
		while i < 5:
			try:
				index = ele.index("Sold")
				d["sold_on"] = ele[index - 2]
				i = 5
			except:
				driver.refresh()
				print("refresh")
				sleep(5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				ele = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[7]/div[3]/div/div[6]"))).text.split("\n")[3:]
				i += 1
		try:
			index = ele.index("Listed for sale")
			d["last_listed_date"] = ele[index - 2]
			d["last_listed_price"] = sub(r'[^\d.]', '', ele[index - 1])
			d["days"] = str(datetime.datetime.strptime(d["sold_on"], "%m/%d/%Y").date() - datetime.datetime.strptime(d["last_listed_date"], "%m/%d/%Y").date()).split(" ")[0]
		except:
			print("last listed date unavailable")

		try:
			tmp = ele[index+1:]
			index = tmp.index("Sold")
			d["prior_sales_date"] = tmp[index - 2]
			d["prior_sales_price"] = sub(r'[^\d.]', '', tmp[index - 1])
		except:
			print("prior sales unavailable")
			d["prior_sales_date"] = "NA"
			d["prior_sales_price"] = "NA"

		try:
			mortgage = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='mortgage-calculators-home-price']/div/span/input")))
			driver.execute_script("arguments[0].scrollIntoView();", mortgage)
			mortgage.clear()
			mortgage.send_keys(d["price"])
		except:
			print("no affordability available")
			return True
		sleep(1)
        #driver.save_screenshot('screenie.png')
        tmp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='moduleAccordion']/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]"))).text
        #print(hello)
	#affordability = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "affordabilityModule")))
	#tmp = WebDriverWait(affordability, 30).until(EC.presence_of_element_located((By.XPATH, "//div/div/div[2]/div[1]/div/div/div[2]"))).text
	#tmp = affordability.find_element_by_xpath("//div/div/div[2]/div[1]/div/div/div[2]").text.split("\n")
	tmp = tmp.split("\n")
        #print(tmp)
	if len(tmp) == 1:
		print("no affordability")
		return True

	for i in range(0, 9, 2):
		d[tmp[i].strip()] = sub(r'[^\d.]', '', tmp[i+1].replace("(", "").replace(")",""))
                print(d[tmp[i].strip()], tmp[i].strip())

	return True

def extract_rental(driver, d):
	try:
		off_market = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div/div[2]/div/div[1]/div/span[1]").text
		if "OFF" in off_market:
			print "Off Market"
			return False
	except:
		print ("in market")

	try:
		rent = driver.find_element_by_xpath("//*[@id='rentalPdpContactLeadForm']/div[1]/div").text
		#rent = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='rentalPdpContactLeadForm']/div[1]/div"))).text
	except:
		try:
			rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div[3]/div[1]/div/div[2]/span").text
		except:
			try:
				rent = driver.find_element_by_xpath("//*[@id='propertySummary']/div/div[3]/div[1]/div/div[2]/span[1]").text
			except:
				rent = "NA"
		#rent = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='propertySummary']/div/div[3]/div[1]/div/div[2]/span"))).text
	d["rent_per_month"] = rent.split("/")[0]
	print (rent)

	# short_form_id = driver.find_element_by_xpath("/html/body/script[3]").text
	print("short form")
	sleep(15)
	short_form_id = driver.execute_script("return window.propertyWeb;")["INITIAL_ACTIONS"][0]["data"]["id"]
	d["short_form_id"] = short_form_id

	try:
		info = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/div[2]/span").text.split(", ")
		d["address"] = info[0]
		d["city"] = info[1]
		d["state"] = info[2].split(" ")[0]
		d["zip code"] = "\"" + info[2].split(" ")[1] + "\""
	except:
		try:
			info = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/div[2]").text.split("\n")
			d["address"] = info[0]
			d["city"] = info[1].split(", ")[0]
			d["state"] = info[1].split(", ")[1].split(" ")[0]
			d["zip code"] = info[1].split(", ")[1].split(" ")[1]
		except:
			try:
				info = driver.find_element_by_xpath("/html/body/footer/div[1]/div[1]/div").text
				try:
					d["address"] = info.split(". ")[0].split("located at ")[1].split(", ")[0]
					d["city"] = info.split(". ")[0].split("located at ")[1].split(", ")[1]
					d["state"] = info.split(". ")[0].split("located at ")[1].split(", ")[2]
				except:
					d["address"] = driver.find_element_by_xpath("//*[@id='address']/h1/div[1]/span").text
				#	d["address"] = info.split(". ")[0].split("located at ")[1].rsplit(" ", 2)[0]
					d["city"] = info.split(". ")[0].split("located at ")[1].rsplit(" ", 2)[0]
					d["state"] = info.split(". ")[0].split("located at ")[1].rsplit(" ", 2)[1]
				zip_index = info.split(". ")[1].split(" ").index("ZIP")
				if info.split(". ")[1].split(" ")[zip_index + 2].isdigit(): 
					d["zip code"] = info.split(". ")[1].split(" ")[zip_index + 2]
				elif info.split(". ")[1].split(" ")[zip_index - 1].isdigit():
					d["zip code"] = info.split(". ")[1].split(" ")[zip_index - 1]
			except:
				driver.save_screenshot('screenie.png')
				driver.quit()
				restart()

	print(d["address"], d["city"], d["state"], d["zip code"])

	try:
		property_detail = driver.find_element_by_xpath("//*[@id='propertyDetails']/div/ul[1]").text.split("\n")
	except:
		property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[4]").text.split("\n")

	print(property_detail)
	bedroom = ""
	bathroom = ""

	for detail in property_detail:
		if "bed" in detail.lower():
			bedroom = detail.rsplit(" ", 1)[0]
			print('1.bed')
			print(bedroom)
		elif "bath" in detail.lower():
			bathroom = detail.rsplit(" ", 2)[0]
			print('2.bath')
			print(bathroom)
		elif "day" in detail.lower():
			d["days"] = detail.split(" ")[0]

	print(bedroom, bathroom, d["days"])
	#if bedroom != "":
	#	bedroom = property_detail[0].rsplit(" ", 1)[0]
	#if bathroom != "":
	#	bathroom = property_detail[1].rsplit(" ", 2)[0]

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
		d["bedroom_min"] = "NA"

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
		property_detail = driver.find_element_by_xpath("//*[@id='lowerBlockRight']/div[4]").text.split("\n")

	for s in property_detail:
		if "sqft" in s:
			d["sqft"] = s.split(" ")[0]
		elif "Built" in s:
			d["year"] = s.split(" ")[2]
		elif "Home" in s or "Apartment" in s or "Family" in s or "loft" in s.lower():
			d["type"] = s

	print (d.get("sqft", "NA"), d.get("year", "NA"), d.get("type", "NA"))

	try:
		phone = driver.find_element_by_xpath("//*[@id='contactAside']/div/h3").text
		if "Contact" in phone:
			d["phone_number"] = driver.find_element_by_xpath("//*[@id='contactAside']/div/div/span").text
		elif "Ask" in phone:
			d["phone_number"] = driver.find_element_by_xpath("//*[@id='contactAside']/div/div/div/div/div/div[2]").text
		else:
			d["phone_number"] = "NA"
	except:
		try:
			phone = driver.find_element_by_xpath("//*[@id='topPanelLeadForm']/div/div/div/div[2]/div[2]/span").text
			d["phone_number"] = phone
		except:
			print ("no phone available")
			d["phone_number"] = "NA"
	print(d["phone_number"])

	try:
		driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[4]/div[2]/div[2]/div[2]").click()
	except:
		try:
			driver.find_element_by_xpath("//*[@id='listingHomeDetailsContainer']/div[3]/div[2]/div[2]/div[2]").click()
		except:
			driver.find_element_by_xpath("//*[@id='crimeCard']/div/div[2]").click()

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
			d["assault"] = 0
			d["arrest"] = 0
			d["theft"] = 0
			d["burglary"] = 0
			d["vandalism"] = 0
			d["crime_other"] = 0
	
	try:
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	except:
		driver.find_element_by_xpath("//*[@id='propertyTitleBar']/ul/li[3]/button/i").click()
	print("change to school")

	try:
		driver.find_element_by_xpath("//*[@id='schoolsCard']").click()
	except:	
		try:
			driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
		except:
			driver.refresh()
			driver.find_element_by_xpath("//*[@id='schoolsAtAGlance']/div[3]/a").click()
			
	try:
		print ("try part for school")
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
			for s in range(1, len(high_school), 5):
				if high_school[s] == u'-': 
					score += int(high_school[s])
			d["high_school_average_score"] = score / int(d["high_school_count"])

		print(d["elementary_school_count"], d["middle_school_count"], d["high_school_count"])
		print(d["elementary_school_average_score"], d["middle_school_average_score"], d["high_school_average_score"])
	except:
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

	has_commute = False
	try:
		try:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[6]").click()
			print "change to commute"
			driver.save_screenshot('screenie.png')
			driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
			#driving = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]
		except:
			try:
				driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[5]").click()
				print "commute button"
				driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
				#driving = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]
			except:
				driver.find_element_by_xpath("//*[@id='commuteCard']").click()
				print "commute card"
				driving = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='commuteTab']/div[2]/div/div[1]/p"))).text.split("%")[0]
				#driving = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		sleep(5)
		
		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[2]").click()

		transit = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[3]").click()

		walking = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		driver.find_element_by_xpath("//*[@id='commuteTypeButtonsContainer']/button[4]").click()

		cycling = driver.find_element_by_xpath("//*[@id='commuteTab']/div[2]/div/div[1]/p").text.split("%")[0]

		d["driving"] = driving
		d["transit"] = transit
		d["walking"] = walking
		d["cycling"] = cycling
		has_commute = True
		print (driving, transit, walking, cycling)
	except:
		d["driving"] = "NA"
		d["transit"] = "NA"
		d["walking"] = "NA"
		d["cycling"] = "NA"
		print("commute not available")

	try:
		try:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[7]").click()
			print "change to shop and eat"
			restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
			#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]
		except:
			driver.find_element_by_xpath("//*[@id='localInfoTabs']/div[1]/div/div/button[6]").click()
			print "shop and eat button"
			restaurant = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='amenitiesSubTitle']/span"))).text.split(" ")[0]
			#restaurant = driver.find_element_by_xpath("//*[@id='amenitiesSubTitle']/span").text.split(" ")[0]

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
		if has_commute == True:
			driver.quit()
			restart()
		d["restaurant"] = "NA"
		d["groceries"] = "NA"
		d["nightlife"] = "NA"
		d["cafe"] = "NA"
		d["shopping"] = "NA"
		d["entertainment"] = "NA"
		d["beauty"] = "NA"
		d["active_life"] = "NA"
		print("shop and eat not available")

	if d["restaurant"] != "NA" and d["driving"] == "NA":
		print "commute missing"
		driver.quit()
		restart()

	if d["driving"] != "NA" and d["restaurant"] == "NA":
		print "shop and eat missing"
		driver.quit()
		restart()
	return True

def extract_school_and_crime(driver, d):
	go = driver.find_element_by_id("crimeCard")
	go.click()

	#crime = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div")
	has_crime_report = False

	try:
		crime = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='crimeTab']/div[2]/div/div[2]/div/ul")))
		#crime = driver.find_element_by_xpath("//*[@id='crimeTab']/div[2]/div/div[2]/div/ul")
		has_crime_report = True
	except:
		print ("no crime report")

	if has_crime_report == False:
		d["Theft"] = 0
		d["Assault"] = 0
		d["Arrest"] = 0
	else:
		crimes = crime.text.split("\n")
		for i in range(0, len(crimes) - 1, 2):
			d[crimes[i+1]] = crimes[i]

	go = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Schools')]")))
#	go = driver.find_element_by_xpath("//button[contains(text(), 'Schools')]")
	go.click()
	sleep(5)

	button = Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/form/div/span/div/select"))))
	#button = Select(driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/form/div/span/div/select"))
	button.select_by_value("Assigned")

	try:
		#elementary = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span"))).text
		elementary = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(elementary)):
			if (i + 1) % 5 == 0:
				tmp.append(elementary[i])
		index = elementary.index(min(tmp))
		d["elementary_name"] = elementary[index - 3]
		d["elementary"] = elementary[index - 4]
		
		#elementary = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span").text
		#d["elementary"] = elementary
		if d["elementary"] == "-":
			d["elementary"] = "NA"
	except:
		print("No elementary scahool available")
		d["elementary"] = "NA"
		d["elementary_name"] = "NA"

	go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[2]/div")
	go.click()

	try:
		#middle = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span"))).text
		#middle = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div/div[1]/div[1]/span").text
		#d["middle"] = middle
		middle = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(middle)):
			if (i + 1) % 5 == 0:
				tmp.append(middle[i])
		index = middle.index(min(tmp))
		d["middle_name"] = middle[index - 3]
		d["middle"] = middle[index - 4]
		if d["middle"] == "-":
			d["middle"] = "NA"
	except:
		print("No middle school available")
		d["middle"] = "NA"
		d["middle_name"] = "NA"

	go = driver.find_element_by_xpath("//*[@id='schoolsTab']/div[2]/div/div[2]/div/ul/li[3]/div")
	go.click()

	try:
		high_school = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='schoolsTab']/div[2]/div/div[2]/div/div/ul/li/div"))).text.split("\n")[1:-1]
		tmp = []
		for i in range(1, len(high_school)):
			if (i + 1) % 5 == 0:
				tmp.append(high_school[i])
		index = high_school.index(min(tmp))
		d["high_school_name"] = high_school[index - 3]
		d["high school"] = high_school[index - 4]
	except:
		print("No high school available")
		d["high school"] = "NA"
		d["high_school_name"] = "NA"

def handle_input(driver, address):
	sleep(10)
	#driver.save_screenshot('screenie.png')
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='webmap-toolbar-center']/span[1]"))).click()
	sleep(2)
	flag = True
	while flag:
		try:
			WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='dijit_anchorMenuItem_0_text']"))).click()
			flag = False
		except:
			WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='webmap-toolbar-center']/span[1]"))).click()
			print("reclick")
	sleep(2)
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/input[2]"))).click()
	text = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/div[2]/input[1]")))
	text.send_keys(address)
	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='siteform']/div[2]/input[2]"))).click()
	sleep(3)
        f = True
        while f == True:
          try:
          	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='ejsrpt']"))).click()
          	f = False
          except:
            print("zomming out")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='map_zoom_slider']/div[2]"))).click()
            sleep(3)
    
	return True

def extract_pollution(driver, d):
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

def save_rental(d, url, name):
	has_csv = os.path.isfile(name)

	if has_csv:
		fd = open(name, "ab")
	else:
		fd = open(name, "wb")

	header = ["Address", "City", "State", "Zip_Code", "Rent_Per_Month", "Year", "Days_on_Trulia", "Type", "Sqft", "Phone_Number"]
	header = header + ["Bedroom_min", "Bedroom_max","Bathroom_min", "Bathroom_max"]
	header = header + ["Assault", "Arrest", "Theft", "Vandalism", "Burglary", "Crime_Other"]
	header = header + ["Elementary_School_Count", "Elementary_School_Avg_Score", 
	"Middle_School_Count", "Middle_School_Avg_Score", 
	"High_School_Count", "High_School_Avg_Score", "Driving", "Transit", "Walking", "Cycling", 
	"Restaurant", "Groceries", "Nightlife", "Cafe", "Shopping", "Entertainment", "Beauty", "Active_life"]

	header = header + ["Latitude", "Longitude",
	"EPA_Region", "Population", "Input_area(sq. miles)",
	"Particulate_Matter", "Ozone", "NATA*_Diesel_PM",
	"NATA*_Air_Toxics_Cancer_Risk", "NATA*_Respiratory_Hazard_Index", "Traffic_Proximity_and_Volume",
	"Lead_Paint_Indicator", "Superfund_Proximity", "RMP_Proximity",
	"Hazardous_Waste_Proximity", "Wastewater_Discharge_Indicator", "Demographic_Index%",
	"Minority_Population%", "Low_Income_Population%", "Linguistically_Isolated_Population%",
	"Population_with_Less_Than_High_School_Education%", "Population_under_Age_5%", "Population_over_Age_64%",
	"URL", "Short_form_ID"]

	value = [d.get("address", "NA"), d.get("city", "NA"), d.get("state", "NA"), 
	d.get("zip code", "NA"), d.get("rent_per_month", "NA"), d.get("year", "NA"), 
	d.get("days", "NA"), d.get("type", "NA"), d.get("sqft", "NA"), d.get("phone_number", "NA")]

	value = value + [d.get("bedroom_min", "NA"), d.get("bedroom_max", "NA"), d.get("bathroom_min", "NA"), d.get("bathroom_max", "NA")]
	value = value + [d.get("assault", "NA"), d.get("arrest", "NA"), d.get("theft", "NA"), 
	d.get("vandalism", "NA"), d.get("burglary", "NA"), d.get("crime_other", "NA")]
	value = value + [d.get("elementary_school_count", "NA"), d.get("elementary_school_average_score", "NA"), 
	d.get("middle_school_count", "NA"), d.get("middle_school_average_score", "NA"),
	d.get("high_school_count", "NA"), d.get("high_school_average_score", "NA"), 
	d.get("driving", "NA"), d.get("transit", "NA"), d.get("walking", "NA"), d.get("cycling", "NA"), d.get("restaurant", "NA"),
	d.get("groceries", "NA"), d.get("nightlife", "NA"), d.get("cafe", "NA"), d.get("shopping", "NA"), d.get("entertainment", "NA"),
	d.get("beauty", "NA"), d.get("active_life", "NA")]

	value = value + [d.get("lat", "NA"), d.get("lon", "NA"),
	d.get("epa_region", "NA"), d.get("population", "NA"), d.get("input area(sq. miles)", "NA"),
	d.get("Particulate Matter", "NA"), d.get("Ozone", "NA"), d.get("NATA* Diesel PM", "NA"),
	d.get("NATA* Air Toxics Cancer Risk", "NA"), d.get("NATA* Respiratory Hazard Index", "NA"), d.get("Traffic Proximity and Volume", "NA"),
	d.get("Lead Paint Indicator", "NA"), d.get("Superfund Proximity", "NA"), d.get("RMP Proximity", "NA"),
	d.get("Hazardous Waste Proximity", "NA"), d.get("Wastewater Discharge Indicator", "NA"), d.get("Demographic Index", "NA"),
	d.get("Minority Population", "NA"), d.get("Low Income Population", "NA"), d.get("Linguistically Isolated Population", "NA"),
	d.get("Population with Less Than High School Education", "NA"), d.get("Population under Age 5", "NA"), d.get("Population over Age 64", "NA"),
	url, d.get("short_form_id", "NA")]

	with fd as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		if has_csv == False:
			filewriter.writerow(header)
		filewriter.writerow(value)

def save_data(d, url, name, crawl_type):
	has_csv = os.path.isfile(name)

	if has_csv:
		fd = open(name, "ab")
	else:
		fd = open(name, "wb")

	header = ["Address", "City", "State", "Zip_Code", "Price", "Year", "Days_on_Trulia", "Type"]
	if crawl_type != "sold":
		header.append("Bedrooms")
		header.append("Agent_Name")

	header += ["Bathrooms", "Sqft"]
	if crawl_type != "sold":
		header.append("Dollars_per_Sqft") 
	header.append("Lot_Size")
	if crawl_type == "sold":
		header.append("Lot_Size_Unit")
		header.append("Sales_Day")
		header.append("Last_Listed_Date")
		header.append("Last_Listed_Price")
		header += ["Prior_Sales_Date"]
		header += ["Prior_Sales_Price"]
	if crawl_type != "sold":
		header.append("Number_of_views")

	header = header + ["Principal_and_Interest", 
	"Property_Taxes", "Home_Insurance", "HOA", 
	"Mortgage Ins. & other", "Theft", "Assault", 
	"Arrest", "Elementary_School_Score", "Elementary_School_Name", 
	"Middle_School_Score", "Middle_School_Name", "High_Schol_Score", 
	"High_Schol_Name", "Latitude", "Longitude",
	"EPA_Region", "Population", "Input_area(sq. miles)",
	"Particulate_Matter", "Ozone", "NATA*_Diesel_PM",
	"NATA*_Air_Toxics_Cancer_Risk", "NATA*_Respiratory_Hazard_Index", "Traffic_Proximity_and_Volume",
	"Lead_Paint_Indicator", "Superfund_Proximity", "RMP_Proximity",
	"Hazardous_Waste_Proximity", "Wastewater_Discharge_Indicator", "Demographic_Index%",
	"Minority_Population%", "Low_Income_Population%", "Linguistically_Isolated_Population%",
	"Population_with_Less_Than_High_School_Education%", "Population_under_Age_5%", "Population_over_Age_64%",
	"URL"]

	value = [d.get("address", "NA"), d.get("city", "NA"), d.get("state", "NA"), 
	d.get("zip code", "NA"), d.get("price", "NA"), d.get("year", "NA"), 
	d.get("days", "NA"), d.get("type", "NA")]

	if crawl_type != "sold":
		value.append(d.get("bedroom", "NA"))
		value.append(d.get("agent_name", "NA"))

	value = value + [d.get("bathroom", "NA"), d.get("sqft", "NA")]
	
	if crawl_type != "sold":
		value.append(d.get("dolloar_per_sqft", "NA"))

	value.append(d.get("lot_size", "NA"))

	if crawl_type == "sold":
		value.append(d.get("lot_size_unit", "NA"))
		value.append(d.get("sold_on", "NA"))
		value.append(d.get("last_listed_date", "NA"))
		value.append(d.get("last_listed_price", "NA"))
		value += [d.get("prior_sales_date")]
		value += [d.get("prior_sales_price")]

	if crawl_type != "sold":
		value.append(d.get("views", "NA"))
	
	value = value + [d.get("Principal & interest", "NA"), 
	d.get("Property taxes", "NA"), d.get("Home insurance", "NA"), d.get("HOA", "NA"), 
	d.get("Mortgage Ins. & other", "NA"), d.get("Theft", "NA"), d.get("Assault", "NA"), 
	d.get("Arrest", "NA"), d.get("elementary", "NA"), d.get("elementary_name", "NA"), 
	d.get("middle", "NA"), d.get("middle_name", "NA"), d.get("high school", "NA"), 
	d.get("high_school_name", "NA"), d.get("lat", "NA"), d.get("lon", "NA"),
	d.get("epa_region", "NA"), d.get("population", "NA"), d.get("input area(sq. miles)", "NA"),
	d.get("Particulate Matter", "NA"), d.get("Ozone", "NA"), d.get("NATA* Diesel PM", "NA"),
	d.get("NATA* Air Toxics Cancer Risk", "NA"), d.get("NATA* Respiratory Hazard Index", "NA"), d.get("Traffic Proximity and Volume", "NA"),
	d.get("Lead Paint Indicator", "NA"), d.get("Superfund Proximity", "NA"), d.get("RMP Proximity", "NA"),
	d.get("Hazardous Waste Proximity", "NA"), d.get("Wastewater Discharge Indicator", "NA"), d.get("Demographic Index", "NA"),
	d.get("Minority Population", "NA"), d.get("Low Income Population", "NA"), d.get("Linguistically Isolated Population", "NA"),
	d.get("Population with Less Than High School Education", "NA"), d.get("Population under Age 5", "NA"), d.get("Population over Age 64", "NA"),
	url]

	with fd as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		if has_csv == False:
			filewriter.writerow(header)
		filewriter.writerow(value)

crawl_type = sys.argv[1]
start_at = sys.argv[2]
end = sys.argv[3]
number = sys.argv[4]
city = sys.argv[5]

if crawl_type == "sold":
	input = "/home/ubuntu/trulia/stores/LA.csv"
	output = "/home/ubuntu/trulia/stores/LA" + str(number) + ".csv"
	#input = "/home/ubuntu/trulia/stores/urls.csv"
	#output = "/home/ubuntu/trulia/stores/availunit_houses" + str(number) + ".csv"
elif crawl_type == "new":
	input = "/home/ubuntu/share/projects/Trulia/stores/" + city + "/new_listing/" + city.lower() + "_new_urls.csv"
	output = "/home/ubuntu/share/projects/Trulia/stores/" + city + "/new_listing/" + city.lower() + "_new_house.csv"
elif crawl_type == "rental":
	input = "/home/ubuntu/trulia/stores/" + city + "_rental_urls.csv"
	output = "/home/ubuntu/trulia/stores/" + city + "_rental_houses" + str(number) + ".csv"

urls = []
with open(input) as f:
	reader = csv.reader(f, delimiter = "\n")
	for i in reader:
		urls.append("https://www.trulia.com/c/ca" + i[0])

driver = start_firefox(trulia)
sleep(5)
try:
	driver.switch_to_window(driver.window_handles[1])
	driver.close()
	driver.switch_to_window(driver.window_handles[0])
except:
	print ("switching window failed??")
	driver.quit()
	restart(True)

if city == "ej":
	workbook = []
	with open("/home/ubuntu/trulia/stores/availunit_address.csv", 'rU') as f:
		d = [row for row in csv.reader(f.read().splitlines())]
		for i in d:
			s = i[0]
			workbook.append(s)

#urls = ["https://www.trulia.com/rental-community/9000067234/Windsor-West-2502-Fields-South-Dr-Champaign-IL-61822/"]
#workbook = ["2502 Fields South Dr, Champaign, IL 61822"]

for i in range(int(start_at), int(end)):#len(urls)):
	print (i)
	#print (urls[i])
	driver.delete_all_cookies()
	d = {}
	crawled_trulia = False

	if "sold" in urls[i]:
		crawled_trulia = True
		driver.get(urls[i])
		print(driver.title)
		sleep(3)
		flag = extract_data(driver, d, crawl_type)
		if flag != False:
		  sleep(3)
		  extract_school_and_crime(driver, d)
		else:
		  crawled_trulia = False
	else:
		crawled_trulia = True
		driver.get(urls[i])
		print("rental")
		print(driver.title)
		sleep(3)
		if "Real Estate, " in driver.title:
			print ("404 in trulia")
			crawled_trulia = False
		elif ("rental" in driver.current_url or "Rent" in driver.title) and "Not Disclosed" not in driver.title:
			print ("start crawling")
			try:
				flag = extract_rental(driver, d)
			except:
				driver.quit()
				restart()
			if flag == False:
				crawled_trulia = False
		elif "this page" in driver.title.lower():
			print ("got blocked")
			driver.quit()
			restart(True)
		else:
			crawled_trulia = False
			address = driver.title.split(" - ")[0]
			print("retnal - only ej screen")


	if crawled_trulia == False:
		address = driver.title.split(" - ")[0]
		if address.find("#") != -1:
			address = address[:address.find("#")]
		else:
			address = address[:address.find("For")]

	if crawled_trulia == False and "Real Estate, " in driver.title:
		address = "NA"
		
	driver.execute_script("window.open('https://ejscreen.epa.gov/mapper/', 'new_tab')")
	sleep(5)
	driver.switch_to_window(driver.window_handles[1])
	driver.save_screenshot('screenie.png')

	if crawled_trulia == True:
	  if d["address"].find('#') != -1:
		add = d["address"][:d["address"].find('#')]
	  else:
	    add = d["address"]
	  address = add + ", " + d["city"] + ", " + d["state"] + " " + d["zip code"]
	elif city == "ej":
	  address = workbook[i]
		
	print(address)

	if (len(address) < 10):
		save_data(d, urls[i], output, crawl_type)
		with open(city + number + ".log", "ab") as log:
			filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
			filewriter.writerow([i])
		continue

	try:
		handle_input(driver, address)
		sleep(5)
 		extract_pollution(driver, d)
 	except:
 		driver.quit()
 		restart()
 	#if "rental" not in urls[i]:
	#	save_data(d, urls[i], output, crawl_type)
	#else:
	save_rental(d, urls[i], output)

	print("saved")
	with open(city + number + ".log", "ab") as log:
	  filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
	  filewriter.writerow([i])
    
	driver.close()
	driver.switch_to_window(driver.window_handles[0])
	sleep(random.randint(10,40))
	
driver.quit()
#display.stop()
