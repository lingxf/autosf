#!/usr/bin/python
#coding:utf-8
import sys
from selenium.webdriver.support.select import Select
import sf
import mysf
import pymail
import MySQLdb
import traceback

reload(sf)
reload(mysf)
reload(pymail)

from sf import *
from mysf import *

#sys.setdefaultencoding('utf8')
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
				rp = mysf.get_rules_for_report(arg)
			else:
				rp = mysf.get_rules_for_queue(arg)
			print rp
		else:
			rp = mysf.get_assign_rules(case_id)
	except:
		traceback.print_exc(file=sys.stderr)
		rp = {}
	for report_id, rules in rp.iteritems():
		if len(report_id) != len('00O3A000009OxKq'):
			print "Invalid report id", report_id
			continue
		caselist = sf.fetch_case_from_report(browser, report_id)
		print "Report %s New Case:%d" % (report_id, len(caselist))
		noassignlist= []
		for case in caselist:
			if case == {}:
				continue
			is_match = False
			for rule in rules:
				if not mysf.check_rule_permission(case, rule):
					print "No permission for this case ", case
					continue
				if case_id == 'test':
					print [ i[1] for i in case.items() ]
				matched = mysf.match_rule(case, rule['condition'])
				if matched == -1:
					rules.remove(rule)
					print "Rule exception", rule['queue_name'], rule['condition']
					pymail.error_mail("Error condition(%s:%s)" % (rule['queue_name'], rule['condition']))
				if matched:
					alias, user_id = get_assignee(rule['queue_id'], rule['assignee'], rule['next'])
					print "assign case %s:%s to %s:%s by condition:%s" % (case['Case Number'],case['Case ID'],  alias, user_id, rule['condition'] )
					if case_id != 'test':
						if user_id == '':
							print "[%s] has no user_id set yet" % rule['assignee']
						else:
							log_assign_status(case['Case Number'], case['Case ID'], rule['queue_id'], alias, 100)
							if r == 0:
								log_assign(case['Case Number'], case['Case ID'], rule['queue_id'], alias)
							elif r == -1:
								print "assignee %s is out of office" % alias
							else:
								print "assign case fail"
							log_assign_status(case['Case Number'], case['Case ID'], rule['queue_id'], alias, r)
					else:
						print "Test:skip assign"
					is_match = True
					break
			if not is_match:
				noassignlist.append(case)
		if noassignlist != []:
			print "not match case %s" % len(noassignlist)
			if case_id == 'test':
				print "not match in %s case list:" % report_id
				for case in noassignlist:
					#print [ i[1] for i in case.items() ]
					print case['Case Number'], case['Case ID'], case['Chipset'], case['Case Owner Alias'], case['Problem Area 1'], case['Problem Area 2'], case['Problem Area 3'],  case['Account Name'][0:16] 
			print "======================================="
		sleep(2)
elif case_id == 'verify':
	try:
		if check_sfid():
			print "All assignee has id set"
	except:
		traceback.print_exc(file=sys.stderr)
else:
	user_id = arg
	if user_id.startswith('c_') or user_id.find('_') == -1:
		user_id = get_user_prop(arg, 'sf_id')
	if case_id.isdigit():
		case_id = get_case_by_number('Case ID', case_id)
	r = assign_case(browser, case_id, user_id)	
	if r == 0:
		print "assign %s to %s sucessfully " % (case_id, user_id)
	elif r == -1:
		print "assignee %s is out of office" % arg
	else:
		print "assign case fail"

mysf.commit_database()
