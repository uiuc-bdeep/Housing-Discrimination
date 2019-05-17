import random
import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from wait_and_get import wait_and_get

NAME_CSS    = "#nameInput"
EMAIL_CSS   = "#emailInput"
PHONE_CSS   = "#phoneInput"
SEND_CSS    = '.ctaButton'
MESSAGE_CSS = '#topPanelLeadForm > div > div > span > div > div.madlibsForm.form > div:nth-child(6) > a'
TEXTB_CSS   = '#textarea'

def try_page_element(driver, element, element_text):
	for text in element_text:
		try:
		 	check = driver.find_element_by_css_selector(element).text
		 	if text in check:
		 		print('Page Status: ' + check)
		 		return 1
		except NoSuchElementException:
			return 0
	return 0

def send_message(driver,name, email, phone_num, address,url,send):
	print('Address    : ' + address)
	print('URL        :' + url)

	try:
		driver.get(url) # start the driver window
		# sleep(100)
		print('Page Title : ' + driver.title) # print the title of the page
		if driver.title == 'Access to this page has been denied.':
			print('Page Status: Blocked' + '\n' + str(address) + ': ' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
			return "RESTART DRIVER"
		elif driver.title == 'Page Not Found | Trulia':
			print('Page Status: 404 Error')
			return 'SOLD'

	except WebDriverException: # check for webdriver exception
		print('WebDriverException: Restarting... ')
		driver.quit()
		return "RESTART DRIVER" # "NEED NEW ADDRESS"

	# wait for the page to load the map on listing page
	# status_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,'#mapViewCard > div > div.cardDescription.pam > div > p.typeEmphasize.activeLink.mtn.ptn'))
	# status_handle = wait_and_get(driver, status_cond, 10)

	form_check = try_page_element(driver,SEND_CSS, ['Request Sent'])

	if form_check > 0:
		print('No Send Button')
		return 'RESTART DRIVER'

	error = 0

	element = '#__next > div > section > div > div.HomeDetailsHero__Container-hubkl0-0.eFsGnT > div > div.HomeDetailsHero__HomeInfoBanner-hubkl0-4.eiQVQP > div:nth-child(1) > div > div.Text__TextContainerBase-s1cait9d-1.krEVrP.Text__TextBase-s1cait9d-0-div.lgawpF'
	error  += try_page_element(driver, element,['Off Market','Recently Sold'])

	element = '#main-content > div.BasicPageLayout__BasicPageLayoutContainer-mfegza-0.fVMZGj > div.HomeDetailsHero__Container-hubkl0-0.bbKmZG > div > div > div.HomeDetailsHero__HomeInfoBanner-hubkl0-4.bHObIE > div.HomeDetailsHero__HomeStatusTitle-hubkl0-7.eLIcbC > span > span'
	error  += try_page_element(driver,element,['OFF MARKET'])

	element = '#main-content > div.BasicPageLayout__BasicPageLayoutContainer-mfegza-0.fVMZGj > div.HomeDetailsHero__Container-hubkl0-0.bbKmZG > div > div > div.HomeDetailsHero__HomeInfoBanner-hubkl0-4.bHObIE > div.HomeDetailsHero__HomeStatusTitle-hubkl0-7.eLIcbC > span.PropertyTag-sc-5t90lx-0.ebIvTY.Tag__TagBase-sc-1rp6fz0-1.clFGBQ.Text__TextBase-sc-1cait9d-0.dJEjin > span'
	error  += try_page_element(driver,element,['SOLD'])

	element = '#__next > div > section > div.BasicPageLayout__BasicPageLayoutContainer-mfegza-0.fVMZGj > div.HomeDetailsHero__Container-hubkl0-0.bOZPCt > div > div > div.HomeDetailsHero__HomeInfoBanner-hubkl0-5.cUoBll > div.HomeDetailsHero__HomeStatusTitle-hubkl0-8.jNtMuF > span > span'
	error  += try_page_element(driver,element,['SOLD'])

	if error > 0:
		return 'SOLD'

	# if status_handle == 0:
	# 	print('Page Could Not load')
	# 	return "RESTART DRIVER"

	element = '#marketStatusLabel'
	error  += try_page_element(driver,element, ['OFF MARKET','RECENTLY SOLD'])

	element = '#propertySummary > div > div > div.xsCol24.smlCol24.mdCol8.lrgCol8.pan.ptxsXxsVisible.ptlSmlVisible > div > div:nth-child(1) > div > span'
	error  += try_page_element(driver,element, ['PENDING'])

	element = 'div.mdCol8:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)'
	error  += try_page_element(driver,element, ['INCOME RESTRICTED'])

	element = 'span.typeCaps:nth-child(1)'
	error  += try_page_element(driver,element, ['FOR SALE','FORECLOSURE'])

	element = 'div.pvl:nth-child(3) > button:nth-child(1)'
	error  += try_page_element(driver,element, ['Notify Me When Available'])

	element = '#propertySummary > div > div.row.man.positionRelative.summaryDetails > div.xsCol24.smlCol24.mdCol8.lrgCol8 > div > div.typeLowlight.typeEmphasize.mvn.h6.miniHidden.xxsHidden > span:nth-child(2)'
	error  += try_page_element(driver,element, ['SENIOR HOUSING'])

	if error > 0:
		return 'SOLD'

	print('Page Status: Available')


	name_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,NAME_CSS))
	name_handle = wait_and_get(driver, name_cond, 10)
	if name_handle == 0:
		print('Name Cond: No Such Element')
		return 'RESTART DRIVER'

	name_handle.send_keys(name) # once it is found, send the name string to it

	# send the email string
	email_handle = driver.find_element_by_css_selector(EMAIL_CSS)
	email_handle.send_keys((str(email) + '@gmail.com'))
	# send the phone string
	phone_handle = driver.find_element_by_css_selector(PHONE_CSS)
	phone_handle.send_keys(str(phone_num))

	send_handle = driver.find_element_by_css_selector(SEND_CSS)

	if send == 1:
		print('Clicking...')
		driver.save_screenshot("/home/ubuntu/trulia/scripts/confirmation.png")
		send_handle.click()

		time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		print('Send Status: Sent')
		sleep(random.randint(10,20))
		return time_sent
	else:
		print('Send Status: Not Sent')
		return ''
