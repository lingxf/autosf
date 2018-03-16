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

#sys.setdefaultencoding('utf8')
from selenium.webdriver.common.by import By 

case_id = data
comments = ''
f = open("clone_sop.txt", "r")
for line in f:
	comments += line + '\r'
try:
	if case_id == 'all' or case_id == '':
		case_list = get_wrong_clone_case()
		except_list = get_except_clone_case()
		print case_list
		print "exception:"
		print except_list
	else:
		case_list = []
		case_list.append([case_id, 0])
	for (case_id, case_number) in case_list:
		print "vio case:", case_number, case_id
		if int(case_number, 10) in except_list:
			print("%s is approved as exception" % case_number)
			continue
		url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % case_id
		print "change status for case %s " % case_number
		browser.get(url)
		WebDriverWait(browser,10,0.5).until(EC.title_contains("Case:"))
		WebDriverWait(browser,10,0.5).until(EC.url_contains(case_id))
		try:
			if not change_status(browser, 'researchi'):
				error_mail("Clonecheck:Save case status %s:%s failure, please check" % (case_number, case_id))
				continue
			if not add_comments(browser, comments, case_id):
				error_mail("Clone check Save case comments %s:%s failure, please check" % (case_number, case_id))
				continue
		except:
			print >>sys.stderr, "Fail to handle this case"
		sleep(3)
except:
	traceback.print_exc(file=sys.stderr)
