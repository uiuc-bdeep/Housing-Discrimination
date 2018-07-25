import os
import re
import csv
import sys
import random
import signal
import base64
import pickle
import psutil
import imaplib
import getpass
import datetime
import webbrowser
import linecache
import numpy as np
import pandas as pd
from time import sleep 
from selenium import webdriver
from pyvirtualdisplay import Display 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# COMMAND TO RUN THIS SCRIPT: python trulia_rental_message_sender.py trulia_rental_message_sender_data.txt <THE DAY YOU ARE RUNNING THIS SCRIPT[1-3]>

CUST_MSG = "I'm looking for a place in this neighborhood."

NUM_RACIAL_CAT = 3

NAME_CSS    = "#nameInput"  
EMAIL_CSS   = "#emailInput"
PHONE_CSS   = "#phoneInput"
SEND_CSS    = '#topPanelLeadForm > div > div > span > div > button'
MESSAGE_CSS = '#topPanelLeadForm > div > div > span > div > div.madlibsForm.form > div:nth-child(6) > a'
TEXTB_CSS   = '#textarea'

def signal_handler(signum, frame):
	print('//////////////////////////////////////////////////////////////////////////////')
	print('//////////////////////// Timed out ... Killing process ///////////////////////')
	print('//////////////////////////////////////////////////////////////////////////////')
	for proc in psutil.process_iter():								# check if there is another instance of this script running 
		if 'python' in proc.name():
			proc.kill()
		if 'firefox' in proc.name():
			proc.kill()
		if 'geckodriver' in proc.name():
			proc.kill()
		if 'Xvfb' in proc.name(): 
			proc.kill()
	print('------------------------------------Killed------------------------------------')
	exit()

def get_LPI(df_timestamp): 
	df_headers = list(df_timestamp)
	LPI        = int(df_headers[-1][-2:])/NUM_RACIAL_CAT
	return int(LPI)

def get_dataframes(status): 
	if os.path.isfile(status) == False: 				# check if the status sheet exists
		print('WRONG TIMESTAMP FILE PATH')
		exit()

	# create a dataframe from saved status sheet csv
	df_timestamp = pd.read_csv(status)
	LPI          = get_LPI(df_timestamp)

	return df_timestamp,LPI

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
			print("Time out")
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
					print("Time out without pop-ups. Exit.")
					return 0

		except ElementNotVisibleException:
			print("Element Not Visible, presumptuously experienced pop-ups")
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True

def send_message(name, email, phone_num, address,url,send):
	fail_count = 0 # counter for how many times this script fails
	while True: 
		page_restart = 0 # tracker for restarting the finction
		options = Options() 
		options.add_argument("--headless") # run in window less mode
		driver = webdriver.Firefox(firefox_options = options, executable_path='/usr/local/bin/geckodriver')
		#driver.set_page_load_timeout(30) # set a time out for 30 secons
		display = Display(visible=0, size=(1024, 768)) # start display
		display.start() # start the display
		print('Drive Launched!') 
		try:
			driver.get(url) # start the driver window
			print(driver.title) # print the title of the page
			if driver.title == 'Access to this page has been denied.':
				driver.quit()
				display.stop()
				print('GOT BLOCKED... RESTARTING ' + str(address) + ': ' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
				return "RESTART DRIVER"
			
		except WebDriverException: # check for webdriver exception
			print('WebDriverException: Restarting... ')
			driver.quit()  
			display.stop()
			return "RESTART DRIVER" # "NEED NEW ADDRESS"

		
		send_handle = None # variable for the button click
		try: 
			waitlist_check = driver.find_element_by_css_selector('#WaitlistFormBottom > div:nth-child(1) > button:nth-child(1)')
			if waitlist_check: 
				driver.quit()
				display.stop()
				print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
				print("Waitlisted: " + str(address))
				print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
				return "WAITLIST"
		except NoSuchElementException:
			try: 
				name_handle = driver.find_element_by_css_selector(NAME_CSS)
			except NoSuchElementException:
				driver.quit()
				display.stop()
				print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
				print('Listing Already Sold: ' + str(address))
				print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
				return "SOLD"

			# set the variables
			name_css  = NAME_CSS
			email_css = EMAIL_CSS
			phone_css = PHONE_CSS
			send_css  = SEND_CSS

			#while name_handle == 0: 
			name_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,name_css))				
			name_handle = wait_and_get(driver, name_cond, 30)
			name_handle.send_keys(name) # once it is found, send the name string to it 

			# send the email string
			email_handle = driver.find_element_by_css_selector(email_css)
			email_handle.send_keys((str(email) + '@gmail.com'))

			# send the phone string
			phone_handle = driver.find_element_by_css_selector(phone_css)
			phone_handle.send_keys(str(phone_num))

			# if custom_msg_bool != True: 
			# 	message_handle = driver.find_element_by_css_selector(MESSAGE_CSS)
			# 	message_handle.click()
			# 	text_box       = driver.find_element_by_css_selector(TEXTB_CSS)
			# 	text_box.send_keys(Keys.COMMAND + 'a')
			# 	text_box.send_keys(Keys.BACKSPACE) 
			# 	text_box.send_keys(CUST_MSG)


			send_handle = driver.find_element_by_css_selector(send_css)

			# Send inquiry. This should be commented out until ready to test
			if send == 1:
				print('Clicking...')
				send_handle.click()
			else: 
				print('Not Clicking...')

			# save the current time and date
			time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print('Message Sent')
			# sleep incase the page doesn't finish sending the inquiry
			sleep(2)
			#quit the driver and display
			driver.quit()
			display.stop()

			return time_sent

#---------------------------------------------------------------------------------------
# input: 
			# 1) path of names_market.csv 
			# 2) path of <city>_timestamp_status_sheet_<date>.csv
			# 3) path of <city>_email_status_sheet_<date>.csv
			# 4) path of <city>_phone_status_sheet_<date>.csv
			# 5) path of <city>_rentals_<date>.csv
			# 6) path of pickle txt file for sold listings
# output:  
			# 1) inquiries sent out to listings in <city>_rentals_<date>.csv
			# 2) <city>_timestamp_status_sheet_<date>.csv
			# 3) <city>_email_status_sheet_<date>.csv
			# 4) <city>_phone_status_sheet_<date>.csv
#---------------------------------------------------------------------------------------
def main():
	parameter_file_name = str(sys.argv[1])
	parameter_day_trial = int(sys.argv[2]) # can be a value of 1,2,3. The will tell the script which partition to use for a race. 
	parameter_send      = int(sys.argv[3]) # can be a value of 0 or 1. This will tell the script whether or not to actually send out inquiries
	line_num = 1
	while True:
		file_line = linecache.getline(parameter_file_name, line_num)
		if file_line is '':
			break
		else:
			file_line = re.sub('\n','',file_line)
			parameters = file_line.split(",") # parse the text file by the \ character

			# set the string passed in from the text files
			time_status_sheet  = parameters[0] 					# timestamp output csv

			df_status,LPI = get_dataframes(time_status_sheet)	# get all required dataframes 
			
			values = list(df_status['handled'].values)																																		# find the where the script left off last and set it to row_index
			row_index = values.index(min(values)) 

			# store the row of the dataframe where the script last left off
			row              = df_status.iloc[row_index]

			# store information about the person 
			handled_state    = row['handled']
			name             = row['first name'] + ' ' + row['last name']
			email            = row['email']
			phone_num        = row['phone number']
			race             = row['racial category']
			person_id        = row['person id']

			address          = row['address ' + str(handled_state + 1)].split(',')[0][1:]
			url              = str(row['address ' + str(handled_state + 1)].split(',')[1][:-1])
			
			if int(handled_state) > (int(LPI) * int(parameter_day_trial)): 
				print('All names have been handled\nexiting...')
				exit()

			print("HANDLING STATE " + str(handled_state) + '/' + str(LPI * parameter_day_trial) + '\n' +  str(person_id) + '. ' + str(name) + '\n' + '---------------------------------')

			# create strings that will be used to located where to store data in df
			time_stamp_col  = str('timestamp ' + str(handled_state+1))

			# keep trying new address until a valid address is found
			print('Sending message to ' + address)
			time_stamp     = send_message(name, email, phone_num, address, url,parameter_send)  	# send out the inquiry and return the timestamp of when the inquiry was sent out

			while time_stamp == "RESTART DRIVER": 
				time_stamp = send_message(name, email, phone_num, address, url,parameter_send)
				
			if time_stamp == "SOLD" or time_stamp == 'WAITLIST':
				time_stamp = 'NA'

			# increment the handled 
			df_status.at[row_index,'handled'] += 1

			# update address/url and timstamp
			df_status.at[row_index,time_stamp_col] = time_stamp

			#write back to csv 
			df_status.to_csv(time_status_sheet,mode='w',index=False)

			print(time_stamp)
			print('=================================================================================')
			for proc in psutil.process_iter():								# check if there is another instance of this script running 
				if 'firefox' in proc.name():
					proc.kill()
				if 'geckodriver' in proc.name():
					proc.kill()
				if 'Xvfb' in proc.name(): 
					proc.kill()
		#sleep(40)
		line_num+=1

#---------------------------------------------------------------------------------------
# 		-to run: 
#				- python trulia_rental_messsage_sender.py trulia_rental_message_sender_data.txt <day trial> <send>
#			
#				- day trial : can be a value of 1, 2, or 3. 
# 				- send      : can be a value of 0 or 1. 0 for do not send inquiries. 1 for send inquiries 
#---------------------------------------------------------------------------------------
for proc in psutil.process_iter():								# check if there is another instance of this script running 
	if 'python' in proc.name() and proc.pid != os.getpid():
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		print('_-_-_-_-_-_-_-_-_-_Second process running... Killing process_-_-_-_-_-_-_-_-_-')
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		exit()
signal.signal(signal.SIGALRM, signal_handler)
signal.alarm(60) 
main()