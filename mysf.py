#!/usr/bin/python
import datetime
import traceback
import sys
import MySQLdb
import pymail

#coding:utf-8
import MySQLdb

def get_wrong_clone_case():
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()

	child_cond =  " Status not like 'Closed%' ";
	cond_parent = "  Status = 'Closed-Pending Your Approval' and `Owner Region` like 'China' ";
	cond_icloned = " `Was Cloned` = 1 and `Created By Internal or Portal` = 0 ";
	sql_child = '''select `Leader Case Number`, `Date/Time Closed` as Child_Date, `Problem Area 2` as Child_PA2, Status as Child_Status 
		 from clonecase where (%s and %s) group by `Leader Case Number` ''' % (cond_icloned, child_cond)
	sql = " select `Case ID`, `Case Number` from mysf.clonecase a right join (%s) e on a.`Case Number` = e.`Leader Case Number` where %s" % (sql_child, cond_parent) 
	c.execute(sql)
	rows = c.fetchall()
	return rows


def get_rules_for_queue(queue_name):
	sql = "select * from rules where queue_name = '%s' order by priority asc " % queue_name
	return get_rules_from_sql(sql)

def get_rules_for_report(report_id):
	sql = "select * from rules where report_id = '%s' order by priority asc " % report_id
	return get_rules_from_sql(sql)

def get_assign_rules(is_test = 'all'):
	if is_test == 'test':
		sql = "select * from rules order by priority asc "
	else:
		sql = "select * from rules where active = 1 order by priority asc "
	return get_rules_from_sql(sql)

def get_rules_from_sql(sql):
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	c.execute(sql)
	columns = tuple( [d[0].decode('utf8') for d in c.description] )
	result = []
	for row in c.fetchall():
		result.append(dict(zip(columns, row)))
	rp = {}
	for row in result:
		report_id = row['report_id']
		if not report_id in rp.keys():
			rp[report_id] = [] 
		rp[report_id].append(row)
	return rp

def check_rule_permission(case, rule):
	pa1 = case[u'Problem Area 1']
	pa2 = case[u'Problem Area 2']
	pa3 = case[u'Problem Area 3']
	alias = rule['owner']
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	sql = " select * from mysf.rule_permission where pa1 = '%s' and pa2 = '%s' and alias = '%s' " % (pa1, pa2, alias)
	n = c.execute(sql)
	rows = c.fetchall()
	if len(rows) > 0:
		return True
	if alias == 'xling':
		return True
	return True

def match_rule(case, condition):
	owner = case['Case Owner Alias']
	chipset = case['Chipset']
	customer = case['Account Name']
	project = case['Customer Project']
	city = case['China OEM City']
	pa1 = case['Problem Area 1']
	pa2 = case['Problem Area 2']
	pa3 = case['Problem Area 3']
	rating = ''
	sb = ''
	ces = 1
	if case['Customer Location'] != 'China' and not customer.rfind("Xiaomi") and not customer.rfind("OPPO"):
		print "Non China case in assign except for OPPO/Xiaomi", case
		return False
	try:
		matched = eval(condition)
	except:
		matched = False
		print "Rule exception", condition
		error_mail("Match rule")
	return matched


def get_user_prop(user, prop):
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	sql = " select `%s` from user.user where user_id = '%s' " % (prop, user)
	c.execute(sql)
	return c.fetchone()[0]

def set_user_prop(user, prop, value):
	print user, value
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	sql = " update user.user set `%s` = '%s' where user_id = '%s' " % (prop, value, user)
	c.execute(sql)
	db.commit()
	return True

def get_assignee(queue_id, assignee, no):
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	li = assignee.split(',')
	sql = " select `next` from mysf.rules where queue_id = {} ".format(queue_id)
	c.execute(sql)
	no = c.fetchone()[0]
	sql = " update mysf.rules set `next` = `next` + 1 where queue_id = {} ".format(queue_id)
	c.execute(sql)
	c.close()
	db.commit()
	db.close()
	total = len(li)
	no = no % total
	alias = li[no]
	user_id = get_user_prop(alias, 'sf_id')
	return (alias, user_id)

def get_case_by_number(field, case_number):
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	sql = " select `%s` from mysf.clonecase where `Case Number` = '%s' " % (field, case_number)
	c.execute(sql)
	return c.fetchone()[0]

def insert_kba(kbas):
	db = MySQLdb.connect(host="10.231.249.45", user="weekly", passwd="week2pass", db="mysf", charset="utf8")
	c=db.cursor()
	total_update = 0
	total_insert = 0
	for cols in kbas:
		kid =       cols[0]
		title =		cols[1]
		kba_id = cols[2]
		rev = cols[3]
		dcn = cols[4]
		status = cols[5]
		content_group = cols[6]
		createdby= cols[7]
		modifiedby= cols[8]
		modifiedon= cols[9]
		title = title.replace("'","''", 10) 
		modifiedon = datetime.datetime.strptime(modifiedon, "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")

		sql_update = " update cnsf.kba_stock set status = '%s', rev = %s, kid = %s, related = '%s', author = '%s', modified = '%s', modified_date = '%s' where kba_id = '%s' and rev <= %s  " % (status, rev, kid, dcn, createdby, modifiedby, modifiedon, kba_id, rev ) 
		ct = c.execute(sql_update)
		total_update += ct

		sql = " insert into cnsf.kba_stock (kba_id, kid, title, rev, related, status, author, modified, modified_date, importer) values ( '%s', %s,'%s', '%s', '%s','%s','%s','%s','%s', 'auto' )" % (kba_id, kid, title, rev, dcn, status, createdby, modifiedby, modifiedon) 
		insert_fail = False
		try:
			c.execute(sql)
		except:
			insert_fail = True
		if not insert_fail:
			total_insert += 1
			print sql
	print >>sys.stderr,"Total Update:%d, Total Insert:%d" % (total_update, total_insert)
	db.commit()
	db.close()
