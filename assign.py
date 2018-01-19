#!/usr/bin/python
#coding:utf-8
import sys
from selenium.webdriver.support.select import Select
import sf
import mysf
import pymail

reload(sf)
reload(mysf)
reload(pymail)

from sf import *
from mysf import *

sys.setdefaultencoding('utf8')
from selenium.webdriver.common.by import By 

words = data.split(' ')
case_id = words[0]
if len(words) > 1:
	arg = words[1]
else:
	arg = None 

if case_id == 'all' or case_id == 'test' or case_id == 'run':
	try:
		if arg:
			print case_id, arg
			if arg.startswith('00'):
				rp = get_rules_for_report(arg)
			else:
				rp = get_rules_for_queue(arg)
			print rp
		else:
			rp = get_assign_rules(case_id)
	except:
		traceback.print_exc(file=sys.stderr)
	for report_id, rules in rp.iteritems():
		if len(report_id) != len('00O3A000009OxKq'):
			print "Invalid report id", report_id
			continue
		caselist = sf.fetch_case_from_report(browser, report_id)
		print "Report %s New Case:%d" % (report_id, len(caselist))
		noassighlist= []
		for case in caselist:
			if case == {}:
				continue
			is_match = False
			for rule in rules:
				if not mysf.check_rule_permission(case, rule):
					print "No permission for this case ", case
					continue
				if mysf.match_rule(case, rule['condition']):
					alias, user_id = get_assignee(rule['queue_id'], rule['assignee'], rule['next'])
					print "assign case %s:%s to %s:%s by condition:%s" % (case['Case Number'],case['Case ID'],  alias, user_id, rule['condition'] )
					if case_id != 'test':
						assign_case(browser, case['Case ID'], user_id)	
					else:
						print "Test:skip assign"
					is_match = True
					break
			if not is_match:
				noassighlist.append(case)
		if noassighlist != []:
			print "not match in %s case list:" % report_id
			for case in noassighlist:
				print [ i[1] for i in case.items() ]
			print "======================================="
		sleep(2)
else:
	user_id = get_user_prop(arg, 'sf_id')
	if case_id.isdigit():
		case_id = get_case_by_number('Case ID', case_id)
	assign_case(browser, case_id, user_id)	
