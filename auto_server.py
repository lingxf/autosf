#!/usr/bin/python
import time
import traceback
from selenium import webdriver
import os, sys
import socket
import time  #
import urllib
import urllib2
import ConfigParser
import re
import cookielib
import json
import datetime
import getpass

#from ticket import *
from lxml import etree
from selenium.webdriver.common.keys import Keys
from pymail import send_mail
from pymail import error_mail

import sf
import mysf
from selenium.webdriver.support.select import Select
from sf import *
from mysf import *

#import sys  
reload(sys)  
sys.setdefaultencoding('utf8')	 
#from ClassLog import *

try: 
  import xml.etree.cElementTree as ET 
except ImportError: 
  import xml.etree.ElementTree as ET 

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep	
from selenium.webdriver.support.select import Select

import base64
from Crypto.Cipher import AES

global browser, proxy, reopen, user_name, user_pwd

reopen = 0
user_name = None
user_pwd = None

def start_sock(server_address):
	try:
		os.unlink(server_address)
	except OSError:
		if os.path.exists(server_address):
			raise	
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	print >>sys.stderr, 'starting up on %s' % server_address
	try:
		sock.bind(server_address)
	except:
		print >>sys.stderr, 'bind error %s' % server_address

	#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.listen(1)
	return sock

def parse_cmdline(cmdline):
	cmd = cmdline
	s = re.search("(\S+) (.+)", cmdline)
	if s:
		cmd = s.group(1)
		data = s.group(2)
	else:
		data = ''
	return (cmd, data)

def run_server(server_address):
	server_address = "/var/lock/%s" % server_address
	sock = start_sock(server_address)
	global browser, proxy, server, reopen
	while True:
		print >>sys.stderr, 'waiting for a connection'
		connection, client_address = sock.accept()
		is_quit = False
		try:
			print >>sys.stderr, 'connection from', client_address
	
			while True:
				data = connection.recv(256)
				if data:
					connection.sendall(data)
				else:
					break
				print >>sys.stderr, 'received "%s"' % data
				print >>sys.stderr, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				(cmd, data) = parse_cmdline(data)
				if cmd == 'get':
					try:
						browser.get(data);
					except:
						traceback.print_exc(file=sys.stderr)
				elif cmd == 'click':
					try:
						execfile('export.py')
					except:
						mysf.log_assign_status(0, cmd, 0, data, 0)
						mysf.commit_database()
						error_mail(cmd)
						if server != 'test':
							is_quit = True
						break
				elif cmd == 'export':
					try:
						execfile('export.py')
					except:
						mysf.log_assign_status(0, cmd, 0, data, 0)
						mysf.commit_database()
						error_mail(cmd)
						if server != 'test':
							is_quit = True
						break
				elif cmd == 'clonecheck':
					try:
						execfile('clonecheck.py')
					except:
						mysf.log_assign_status(0, cmd, 0, data, 0)
						mysf.commit_database()
						error_mail(cmd)
						if server != 'test':
							is_quit = True
						break
				elif cmd == 'status':
					case_id, status = data.split(' ')
					url="https://qualcomm-cdmatech-support.my.salesforce.com/%s" % case_id
					browser.get(url)
					WebDriverWait(browser,10,0.5).until(EC.title_contains("Case:"))
					WebDriverWait(browser,10,0.5).until(EC.url_contains(case_id))
					if not change_status(browser, status):
						error_mail("Save case status %s:%s failure, please check" % (case_number, case_id))
				elif cmd == 'fetchid':
					report_id = data
					user_map = sf.fetch_user_id_from_report(browser, report_id)
					print >>sys.stderr, user_map
					print >>sys.stderr, "Total User Id:",len(user_map)
					r = [mysf.set_user_prop(alias, 'sf_id', user_id) for alias, user_id in user_map.iteritems()]
				elif cmd == 'edit':
					try:
						execfile('editcase.py')
					except:
						error_mail(cmd)
						if server != 'test':
							is_quit = True
				elif cmd == 'assign':
					try:
						execfile('assign.py')
					except:
						mysf.log_assign_status(0, cmd, 0, data, 0)
						mysf.commit_database()
						error_mail(cmd)
						if server != 'test':
							is_quit = True
						break
				elif cmd == 'sf':
					if data == '':
						sf_login(browser)
					else:
						sf_login(browser, None, int(data))
				elif cmd == 'restart':
					browser.quit()
					reopen -= 1
					if data != '':
						proxy = set_proxy(data)
					browser = open_browser(proxy)
				elif cmd == 'test':
					try:
						execfile('test.py')
					except:
						traceback.print_exc(file=sys.stderr)
				elif cmd == 'quit':
					is_quit = True
					reopen -= 1
				else:
					break
		except:
			traceback.print_exc(file=sys.stderr)
		finally:
			# Clean up the connection
			connection.close()
			if is_quit:
				break
	try:
		browser.quit()
	except:
		print >>sys.stderr, "Quit exception"

def set_proxy(proxy):
	if proxy == 'proxy':
		proxy = "cedump-sh.ap.qualcomm.com:9090"
	elif proxy == 'sdproxy':
		proxy = "secure-proxy2.qualcomm.com:9090"
	elif proxy == 'noproxy':
		proxy = None
	return proxy

proxy = None
if len(sys.argv) < 2:
	print "%s sync|clonecheck|assign" % sys.argv[0]
	sys.exit()
if len(sys.argv) > 2:
	proxy = set_proxy(sys.argv[2])

timeout = None
if len(sys.argv) > 3:
	timeout = int(sys.argv[3])

server = sys.argv[1]

while(True):
	try:
		if server == 'simple':
			browser = open_browser(proxy)
			browser.get("http://cedump-sh.ap.qualcomm.com/report/show_mysfrule.php")
		else:
			if reopen > 10:
				error_mail("reopen>10")
				break
			print "reopen times:%d" % reopen
			user_name, user_pwd = get_userpwd(user_name, user_pwd)
			if timeout:
				browser = sf_start(None, user_name, user_pwd, proxy, timeout)
			else:
				browser = sf_start(None, user_name, user_pwd, proxy)
			reopen += 1
		run_server(server)
	except:
		print "Login rerun error"
		traceback.print_exc(file=sys.stderr)
		time.sleep(24)
	time.sleep(6)
