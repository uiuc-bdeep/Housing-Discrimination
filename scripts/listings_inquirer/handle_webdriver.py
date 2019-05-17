import os
import sys
import psutil
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def restart(blocked,driver):
	if blocked:
		driver.quit()
		for proc in psutil.process_iter():
			if "firefox" in proc.name():
				proc.kill()
			if "geckodriver" in proc.name():
				proc.kill()
		os.execv(sys.executable, ['python'] + sys.argv)

def start_firefox():
	DesiredCapabilities.FIREFOX["proxy"] = {
		"proxyType" : "pac",
		"proxyAutoconfigUrl" : "http://www.freeproxy-server.net/"
	}

	options = Options()
	options.add_argument("--headless")
	fp = webdriver.FirefoxProfile()
	#fp.set_preference("general.useragent.override", UserAgent().random)
	fp.update_preferences()
	driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options,
								capabilities = webdriver.DesiredCapabilities.FIREFOX,
								executable_path = '/usr/bin/geckodriver')

	driver.install_addon("/home/ubuntu/trulia/stores/adblock_plus-3.3.1-an+fx.xpi")
	driver.install_addon("/home/ubuntu/trulia/stores/uBlock0@raymondhill.net.xpi")

	driver.wait = WebDriverWait(driver, 5)
	driver.delete_all_cookies()
	return driver
