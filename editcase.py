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
			else:
				queue = []
		else:
			queue = mysf.get_rcatasks(0)
			queue += mysf.get_rcatasks(2)

		for task in queue:
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
			if sf.fill_case_rca(browser, task['case_id'], complexity, onsite, task['rcateam'], task['subteam'], summary, main, detail, detail2 ):
				mysf.finish_rcatask(task['jobid'], 1)
			else:
				mysf.finish_rcatask(task['jobid'], 2)
		mysf.commit_database()
	except:
		traceback.print_exc(file=sys.stderr)
		
if data.startswith('rca '):
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
	fill_case_rca(browser, case_id, complexity, onsite, team, sub, summary, main, detail, detail2)


if data == 'enumpa':
	idpa = [ "pg:frm:blk:pbView:problemCode1", "pg:frm:blk:pbView:problemCode2", "pg:frm:blk:pbView:problemCode3" ] 
	edit_case(browser, '03292574')
	select_option_with(browser, pas[0], "BSP")
	sleep(2)
	select_option_with(browser, pas[1], "Stability")
	sleep(2)
	f = open("options.txt", "w")
	enum_options(browser, pas, 0, f)
	f.close()

if data == 'enumrca':
	ids = [ "pg:frm:blk:resolution:rcaTeam", "pg:frm:blk:resolution:rcaSubTeam", "pg:frm:blk:resolution2:rcaDetailRootCause", "pg:frm:blk:resolution3:pgblkSctItemRCADetailRC:selRCADetailRC", "pg:frm:blk:resolution3:pgblkSctItemRCA2DetailRC2:selRCA2DetailRC" ]
	#ids = [ "pg:frm:blk:resolution:rcaTeam", "pg:frm:blk:resolution:rcaSubTeam", "pg:frm:blk:resolution2:rcaDetailRootCause", "pg:frm:blk:resolution3:pgblkSctItemRCADetailRC:selRCADetailRC" ]
	edit_case(browser, '03292574')
	select_option_with(browser, ids[0], "BSP")
	sleep(2)
	select_option_with(browser, ids[1], "Linux")
	sleep(2)
	f = open("rca.txt", "w")
	enum_options(browser, ids, 0, f)
	f.close()
