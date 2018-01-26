#!/usr/bin/python
#coding:utf-8
import sys
import re
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import ProxyType

import mysf
from pymail import *
from mysf import *
from Crypto.Cipher import AES
from time import sleep	
import base64
import traceback
try: 
  import xml.etree.cElementTree as ET 
except ImportError: 
  import xml.etree.ElementTree as ET 

def click_timeout(browser, xpath, seconds=10):
	while(True):
		try:
			browser.find_element_by_xpath(xpath).click()
			break
		except:
			if seconds <= 0:
				traceback.print_exc()
				break
			sleep(1);
			seconds -= 1

def sendkey_timeout(browser, xpath, value, seconds=10):
	while(True):
		try:
			browser.find_element_by_xpath(xpath).send_keys(value)
			break
		except:
			if seconds <= 0:
				traceback.print_exc()
				break
			sleep(1);
			seconds -= 1

status_list = {
 'hold':'Hold-Customer Information Required',
 'researchi':'Research-Internal Support',
 'research':'Research-General',
 'closep':'Closed-Pending Your Approval',
}

def find_element_by_id_timeout(browser, eid, seconds=10):
	while(True):
		try:
			ele = browser.find_element_by_id(eid)
			return ele
		except:
			if seconds <= 0:
				traceback.print_exc()
				return False
			sleep(1);
			seconds -= 1

def change_status(browser, status, option=None):
	str_status = status_list[status]
	els = browser.find_elements_by_xpath("//*[@id='ep']/div[2]/div[2]/table/tbody/tr[10]/td[2]")
	if len(els) > 0:
		old_status = els[0].text
		if old_status == str_status:
			print "old status is already %s " % old_status
			return True
		else:
			print "change from %s => %s " % (old_status, str_status)
	print("Edit...")
	click_timeout(browser,'//*[@id="topButtonRow"]/input[1]')
	eid = "pg:frm:blk:title:StatusSection:selStatus"
	WebDriverWait(browser,10, 1).until(EC.presence_of_element_located((By.ID, eid)))
	select_option(browser, eid, str_status)
	try:
		WebDriverWait(browser,6, 1).until(EC.visibility_of_element_located((By.ID, 'pg:frm:blk:title:StatusSection:statusforStatus.start')))
		WebDriverWait(browser,6, 1).until(EC.invisibility_of_element_located((By.ID, 'pg:frm:blk:title:StatusSection:statusforStatus.start')))
	except:
		print("Wait Timeout")
	sleep(2)
	print("Saving ...")
	click_timeout(browser, '//*[@id="pg:frm:blk:navBtns:btnSave"]', 20);
	#click_timeout(browser, '//*[@id="pg:frm:blk:navBtns"]/input[3]');#cancel
	try:
		WebDriverWait(browser,10,0.5).until(EC.title_contains("Case:"))
	except:
		print "Save case failure, please check"
		return False
	return True

def add_comments(browser, comments, case_id = None, is_public=False):
	if comments=='':
		return ;

	if case_id and len(case_id) == len("5003A00000mr3Hh"):
		new_comment_url="https://qualcomm-cdmatech-support.my.salesforce.com/00a/e?parent_id=%s&retURL="%(case_id) + "%2F" + case_id
		browser.get(new_comment_url);
	else:
		click_timeout(browser,'//*[@id="topButtonRow"]/input[1]')
		sleep(5)
	try:
		WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'CommentBody')))
		browser.find_element_by_xpath("//*[@id=\"CommentBody\"]").send_keys(unicode(comments, "utf-8"))
		if is_public:
			click_timeout(browser, '//*[@id="IsPublished"]', 2);
		#click_timeout(browser, '//*[@id="bottomButtonRow"]/input[2]');#取消
		click_timeout(browser, "//*[@id=\"topButtonRow\"]/input[1]", 3);#保存
	except:
		print "click save or cancel failed"
		traceback.print_exc();
	try:
		WebDriverWait(browser,10,0.5).until(EC.title_contains("Case:"))
	except:
		print "Save case comments failure, please check"
		return False
	return True

def open_browser(proxy=None, download=None):
	profile = webdriver.FirefoxProfile(r'/home/xling/.mozilla/firefox/nw3oghgt.auto/')
	profile.native_events_enabled = True
	if download:
		profile.set_preference("browser.download.dir", download);


#	profile.set_preference("browser.download.useDownloadDir", "true");
#	profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain, application/vnd.ms-excel, text/csv, text/comma-separated-values, application/octet-stream")
	if proxy is not None:
		raw = {'proxyType':{ 'ff_value':1, 'string': 'manual'}, 'httpProxy':proxy, 'sslProxy':proxy}
		proxy = webdriver.Proxy(raw)
		profile.set_proxy(proxy)

	#browser = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNIT.copy())
	browser = webdriver.Firefox(profile, executable_path="/usr/bin/geckodriver")
	#brwser.implicitly_wait(60)
	return browser

def sf_start(url, proxy=None, timeout=60):
	browser = open_browser(proxy)
	sf_login(browser, url, timeout) 
	return browser

def sf_login(browser, url=None, timeout = 60):
	default_url = "https://qualcomm-cdmatech-support.my.salesforce.com/00O3A000009OpFh"
	user_name = "xling"
	f = open("passwd", "rb")
	user_pwd = f.readline().strip()
	browser.get(default_url)

	ciphertext = base64.b64decode(user_pwd)
	obj2 = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	user_pwd = obj2.decrypt(ciphertext)

	print "login...."
	state = 0
	while timeout > 0:
		sleep(1)
		timeout -= 1
		title = browser.title.encode('ascii')
		if timeout % 10 == 0:
			title = browser.title
			print "10 seconds pass..., title:",title
		try:
			if state == 0 and title.rfind("CreatePoint") != -1:
				print "Find Login UI"
				state = 1
				sendkey_timeout(browser, "//*[@id=\"frmLogin\"]/input[4]",user_name)
				sendkey_timeout(browser, "//*[@id=\"frmLogin\"]/input[5]", user_pwd)
				click_timeout(browser, "//*[@id=\"frmLogin\"]/input[8]")
			if (state == 0 or state == 1) and "china-update-" in title:
				print "Login Sucessfully"
				for cookie in browser.get_cookies():
					print "%s -> %s" % (cookie['name'], cookie['value'])
				if url != None:
					browser.get(url)
				return True
		except:
			print "SF login exception"
			traceback.print_exc(file=sys.stderr)
	print "Timeout, login fail..."
	return False

def select_option_with(browser, eid, text):
	ele = find_element_by_id_timeout(browser, eid)
	ops = ele.find_elements_by_xpath("./option")
	for op in ops:
		value = op.text
		selected = op.get_attribute('selected')
		if text in op.text:
			if selected:
				return 2
			sel = Select(ele)
			sel.select_by_visible_text(value)
			return 1
	return 0

def select_option(browser, eid, text):
	ele = find_element_by_id_timeout(browser, eid)
	sel = Select(ele)
	sel.select_by_visible_text(text)

def fill_options(browser, ids, options):
	i = 0
	result = False
	for text in options:
		result = True
		r = select_option_with(browser, ids[i], text)
		if r == 0:
			return False
		elif r == 2:
			i += 1
			continue
		sleep(3)
		i += 1
	return result

def edit_case(browser, case_id):
	if case_id.isdigit():
		case_id = get_case_by_number('Case ID', case_id)
	browser.get("https://qualcomm-cdmatech-support.my.salesforce.com/%s" % case_id)
	click_timeout(browser,'//*[@id="topButtonRow"]/input[1]')
	visit = "pg:frm:blk:resolution:resolvedSection:selResolved"
	WebDriverWait(browser,10, 1).until(EC.presence_of_element_located((By.ID, visit)))


def assign_case(browser, case_id, user_id):
	assign_url = "https://qualcomm-cdmatech-support.my.salesforce.com/apex/caseOwnerChange?Id=%s" % case_id
	browser.get(assign_url)
	click_timeout(browser, '//*[@id="pg:frm:j_id27:j_id30"]')
	sleep(2)
	select_option(browser, "pg:frm:pbOwner:ownerSelectionType", "User")
	sleep(1)
	ele = browser.find_element_by_id("pg:frm:pbOwner:newOwnerName")
	ele.clear()
	#ele.send_keys("Xiaofeng Ling")
	print ele.get_attribute('value')
	ele = browser.find_element_by_id("pg:frm:pbOwner:newOwnerId")
	browser.execute_script("arguments[0].value = '%s';" % user_id, ele)
	sleep(1)
	click_timeout(browser,'//*[@id="bottomButtonRow"]/input[1]', 3)
	return True

def fetch_user_id_from_report(browser, report_id):
	url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % report_id
	browser.get(url)
	WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'headerRow_0')))
	ele = browser.find_element_by_id('headerRow_0')
	heads = ele.find_elements_by_xpath(".//th[*]/a/strong")
	fields = [ f.text for f in heads ]
	
	caselist = []
	rows = ele.find_elements_by_xpath("..//tr[@class='even' and position()<500]")
	for onerow in rows:
		cols = onerow.find_elements_by_xpath("./td")
		caselist.append(dict(zip(fields, [ col.get_attribute("innerHTML") for col in cols])))
	caselist = filter(lambda x: x != {}, caselist)	
	user_map = {}
	for case in caselist:
		raw = case['Case Owner Alias']
		s = re.search("href\=\"\/(\w+)\"\>(\w+)\<\/a\>", raw)
		if s:
			user_id = s.group(1)
			alias = s.group(2)
			user_map[alias] = user_id
	return user_map

def fetch_case_from_report(browser, report_id):
	url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % report_id
	browser.get(url)
	WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.ID, 'headerRow_0')))
	ele = browser.find_element_by_id('headerRow_0')
	heads = ele.find_elements_by_xpath(".//th[*]/a/strong")
	fields = [ f.text for f in heads ]
	
	caselist = []
	rows = ele.find_elements_by_xpath("..//tr[(@class='even' or @class='odd') and position()<100]")
	for onerow in rows:
		cols = onerow.find_elements_by_xpath("./td")
		caselist.append(dict(zip(fields, [ col.text for col in cols])))
	caselist = filter(lambda x: x != {}, caselist)	
	return caselist		

def parse_kba(browser):
	lines = browser.find_elements_by_xpath("//div[@id='gridKnowledgeBases']/table[@class='k-selectable']/tbody[@role='rowgroup']/tr[*]")
	if lines == []:
		return False;
	print >>sys.stderr,"Find %s lines" % len(lines)
	kbas = []
	for line in lines:
		tds = line.find_elements_by_xpath("./td")
		cols = []
		kid =  tds[0].get_attribute("innerHTML")
		cols.append(kid)
		try:
			for i in xrange(1, 10):
				cols.append(tds[i].get_attribute("innerHTML"))
		except:
			print >>sys.stderr, "exception column:", i
		kbas.append(cols)
	return kbas

def parse_kba_pages(browser, n):
	for i in xrange(1, n+1):
		print "page:", i
		cols = parse_kba(browser)
		mysf.insert_kba(cols)
		xpath = "//div[@id='gridKnowledgeBasesPgr']/a[@title='Go to the next page']/span"
		tds = browser.find_elements_by_xpath(xpath)
		if tds != []:
			print tds[0].get_attribute("innerHTML")
			tds[0].click()
			xpath = "//a[@class='k-button k-button-icontext k-grid-excel']"
			WebDriverWait(browser,300, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
			sleep(4)
			cols = parse_kba(browser)
			mysf.insert_kba(cols)
	mysf.commit_database()

def print_select(ele, out = None):
	option = ele.find_elements_by_xpath("./option")
	ops = []
	for o in option:
		ops.append(o.text)
		if out:
			print >>out, o.text
	return ops

def print_next_select(browser, layer, ids, out = None):
	global print_select, print_next_select
	ele =  find_element_by_id_timeout(browser, ids[layer])
	if not ele:
		return
	ops = print_select(ele)
	for text in ops:
		if 'None' in text or 'Choose' in text:
			continue
		tab = ' '.join([ ' ' for i in xrange(layer)])
		print >>out, layer, tab, text
		ele =  find_element_by_id_timeout(browser, ids[layer])
		try:
			sel = Select(ele) 
			sel.select_by_visible_text(text)
		except:
			print "except skip", layer,  ids[layer]	
			return
			
		if layer + 1 >= len(ids):
			continue
		WebDriverWait(browser,6, 1).until(EC.visibility_of_element_located((By.ID, ids[layer + 1])))
		sleep(3)
		print_next_select(browser, layer + 1, ids, out)


def enum_options(browser, ids, n = 0, out = None):
	print_next_select(browser, n, ids, out)

