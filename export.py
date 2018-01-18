#!/usr/bin/python
#coding:utf-8
import sys
from selenium.webdriver.support.select import Select
import sf
import mysf
reload(sf)
reload(mysf)

from sf import *
from mysf import *

sys.setdefaultencoding('utf8')
from selenium.webdriver.common.by import By 

if cmd == 'click':
	buttons = browser.find_elements_by_xpath("//input[@value=\"Export\"]")
	if len(buttons) == 0:
		buttons = browser.find_elements_by_xpath("//input[@value=\"Export Details\"]")
		if len(buttons) == 0:
			report_id = '00O3A000009OpFh' #today
			url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % report_id
			browser.get(url)
			WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'fchArea')))
		print "click export detail..."
		click_timeout(browser, "//input[@value=\"Export Details\"]")
		WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'bottomButtonRow')))
	print "click export report..."
	click_timeout(browser, "//input[@value=\"Export\"]", 2)
elif cmd == 'export':
	if data == 'rules':
		url = "http://aquaprod04.qualcomm.com/caseassignment/"
		browser.get(url)
		title =  "//a[@title='Export to Excel']"
		WebDriverWait(browser,300, 1).until(EC.presence_of_element_located((By.XPATH, title)))
		print "Rule page open, click export rules..."
		click_timeout(browser,  title)
	elif data == 'kid':
		url = "https://aggregator.qualcomm.com/Views/Pages/KnowledgeBases.aspx"
		browser.get(url)
		xpath = "//a[@class='k-button k-button-icontext k-grid-excel']"
		WebDriverWait(browser,10, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
		sleep(2)
		cols = parse_kba(browser)
		insert_kba(cols)
	elif data == 'kba':
		url = "https://aggregator.qualcomm.com/Views/Pages/KnowledgeBases.aspx"
		browser.get(url)
		xpath = "//a[@class='k-button k-button-icontext k-grid-excel']"
		WebDriverWait(browser,10, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
		print "Find xpath:", xpath
		is_quit = 20
		while is_quit > 0:
			sleep(1)
			is_quit -= 1
			rows = browser.find_elements_by_xpath(xpath)
			if rows == []:
				continue
			print rows
			for onerow in rows:
				print "click export KBA..." 
				onerow.click()
				is_quit = 0
				break
	else: #SF report
		if data == 'today' or data == '':
			report_id = '00O3A000009OpFh' #today
		elif data == 'yesterday':
			report_id = '00O3A000009OqB7' #yesterday
		else:
			report_id = data
		url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % report_id
		browser.get(url)
		WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'fchArea')))
		click_timeout(browser, "//input[@value=\"Export Details\"]")
		WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'bottomButtonRow')))
		click_timeout(browser, "//input[@value=\"Export\"]")
