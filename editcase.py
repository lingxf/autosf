#!/usr/bin/python
#coding:utf-8
import sys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import *
import sf
import traceback
import mysf
import pymail

reload(sf)
reload(mysf)
reload(pymail)

from sf import *
from mysf import *

#sys.setdefaultencoding('utf8')
from selenium.webdriver.common.by import By 
if __name__=='__main__':
	if len(sys.argv) > 4:
		data = sys.argv[1]

if data.startswith('pa '):
	idpa = [ "pg:frm:blk:pbView:problemCode1", "pg:frm:blk:pbView:problemCode2", "pg:frm:blk:pbView:problemCode3" ] 
	pas = data[3:].split(':')
	print pas
	case_id = pas[0].strip()
	edit_case(browser, case_id)
	fill_options(browser,idpa, pas[1:]) 
	click_timeout(browser, '//input[@value="Save"]', 20);

if data.startswith('rcabatch'):
	try:
		cmds = data.split(' ')
		if len(cmds) > 1:
			if cmds[1].isdigit():
				queue = mysf.get_rcatask(cmds[1])
			elif(cmds[1] == 'error'):
				queue = mysf.get_rcatasks(2)
			else:
				queue = []
		else:
			queue = mysf.get_rcatasks(0)
		print queue
		for task in queue:
			if task['action'] == 1:
				rcas = task['rca'].split(':')
				if len(rcas) < 4:
					print "Not enough field, Skip one task:%s " % task
					continue
				if len(rcas) == 4:
					summary = "Resolved"
				else:
					summary = rcas[4]
				complexity = rcas[0]
				onsite = rcas[1]
				if onsite != 'Yes':
					onsite = 'No'
				main = rcas[2]
				detail = rcas[3]
				if task['rcateam'] == 'BSP/HLOS':
					detail2 = 'No QC'
				else:
					detail2 = '*'
				print task, rcas
				sf.error_msg = ''
				if sf.change_case_rca(browser, task['case_id'], complexity, onsite, task['rcateam'], task['subteam'], summary, main, detail, detail2 ):
					mysf.finish_rcatask(task['jobid'], 1)
				else:
					mysf.finish_rcatask(task['jobid'], 2, sf.error_msg)
			elif task['action'] == 2:
				subject = task['rca']
				print "Change title %s" % subject
				if sf.change_case_subject(browser, task['case_id'], subject):
					mysf.finish_rcatask(task['jobid'], 1)
				else:
					mysf.finish_rcatask(task['jobid'], 2, sf.error_msg)
			mysf.commit_database()
	except:
		traceback.print_exc(file=sys.stderr)
		
if data.startswith('rca '):
	try:
		rcas = data[4:].split(':')
		print rcas
		case_id = rcas[0].strip()
		team = 'BSP'
		sub = 'Linux'
		complexity = rcas[1]
		onsite = rcas[2]
		if onsite != 'Yes':
			onsite = 'No'
		main = rcas[3]
		detail = rcas[4]
		detail2 = 'No QC'
		summary = rcas[5]
		change_case_rca(browser, case_id, complexity, onsite, team, sub, summary, main, detail, detail2)
	except UnexpectedAlertPresentException:
		print "Alert Window"
		alert = browser.switch_to.alert
		alert.accept()
	except:
		traceback.print_exc(file=sys.stderr)

if data.startswith('summary '):
	words = data[9:].split(':')
	case_id = words[0].strip()
	summary = words[1]
	change_resolution_summary(browser, case_id, summary)

if data.startswith('subject '):
	words = data[8:].split(':')
	case_id = words[0].strip()
	summary = words[1]
	change_case_subject(browser, case_id, summary)

if data.startswith('enumpa'):
	cmds = data.split(' ')
	idpa = [ "pg:frm:blk:pbView:problemCode1", "pg:frm:blk:pbView:problemCode2", "pg:frm:blk:pbView:problemCode3" ] 
	level = 0
	if len(cmds) > 1:
		select_option_with(browser, idpa[0], cmds[1])
		sleep(2)
		level += 1
	if len(cmds) > 2:
		select_option_with(browser, idpa[1], cmds[2])
		sleep(2)
		level += 1
	edit_case(browser, '03292574')
	f = open("pa-options.txt", "w")
	enum_options(browser, idpa, level, f)
	f.close()

if data.startswith('enumrca') or data.startswith('enumrca2'):
	cmds = data.split(' ')
	if cmds[0] == 'enumrca' :
		ids = [ "pg:frm:blk:resolution:rcaTeam", "pg:frm:blk:resolution:rcaSubTeam", "pg:frm:blk:resolution2:rcaDetailRootCause", "pg:frm:blk:resolution3:pgblkSctItemRCADetailRC:selRCADetailRC", "pg:frm:blk:resolution3:pgblkSctItemRCA2DetailRC2:selRCA2DetailRC" ]
	if cmds[0] == 'enumrca2':
		ids = [ "pg:frm:blk:resolution:rcaTeam", "pg:frm:blk:resolution:rcaSubTeam", "pg:frm:blk:resolution2:rcaDetailRootCause", "pg:frm:blk:resolution3:pgblkSctItemRCADetailRC:selRCADetailRC" ]
	edit_case(browser, '03292574')
	level = 0
	if len(cmds) > 1:
		select_option_with(browser, ids[0], cmds[1])
		sleep(2)
		level += 1
	if len(cmds) > 2:
		select_option_with(browser, ids[1], cmds[2])
		sleep(2)
		level += 1
	if len(cmds) > 3:
		select_option_with(browser, ids[2], cmds[3])
		sleep(2)
		level += 1
	f = open("rca.txt", "w")
	enum_options(browser, ids, level, f)
	f.close()

if data.startswith('list'):
	if len(sys.argv) > 2:
		queue = mysf.get_rcatasks(1, 1, sys.argv[2])
	else:
		queue = mysf.get_rcatasks(1)
	for task in queue:
		print "%s:%s" % (task['case_number'], task['rca'])
