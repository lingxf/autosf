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

if data.startswith('rca '):
	ids = [ "pg:frm:blk:resolution:rcaTeam", "pg:frm:blk:resolution:rcaSubTeam", "pg:frm:blk:resolution2:rcaDetailRootCause", "pg:frm:blk:resolution3:pgblkSctItemRCADetailRC:selRCADetailRC", "pg:frm:blk:resolution3:pgblkSctItemRCA2DetailRC2:selRCA2DetailRC" ]
	rcas = data[4:].split(':')
	print rcas
	case_id = rcas[0].strip()
	edit_case(browser, case_id)

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
	done = False
	ele = find_element_by_id_timeout(browser,"pg:frm:blk:resolution3:caseResolutionSummary")
	browser.execute_script("arguments[0].value = '%s';" % summary, ele)
 	idcmplx = "pg:frm:blk:resolution:j_id56:selCaseComplexity"
	done = select_option_with(browser, idcmplx, complexity)
	visit = "pg:frm:blk:resolution:resolvedSection:selResolved"
	done = select_option(browser, visit, onsite)
	print >>sys.stderr, "Choose RCA.."
	done = fill_options(browser,ids, [team, sub, main, detail, detail2]) 

	ele = find_element_by_id_timeout(browser, "pg:frm:blk:resolution:totalHrsCaseOwners")
	hour = 0.5
	#browser.execute_script("arguments[0].value = '%s';" % hour, ele)
	if not done:
		print >>sys.stderr, case_id, " Fail RCA"
	print("Saving ...")
	click_timeout(browser, '//input[@value="Save"]', 20);

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
