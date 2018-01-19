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

global server_address, kba_server_address, rule_server_address



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
						error_mail(cmd)
						break
				elif cmd == 'export':
					try:
						execfile('export.py')
					except:
						error_mail(cmd)
						break
				elif cmd == 'clonecheck':
					try:
						execfile('clonecheck.py')
					except:
						error_mail(cmd)
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
				elif cmd == 'assign':
					try:
						execfile('assign.py')
					except:
						error_mail(cmd)
						break
				elif cmd == 'sf':
					if data == '':
						sf_login(browser)
					else:
						sf_login(browser, None, int(data))
				elif cmd == 'test':
					try:
						execfile('test.py')
					except:
						traceback.print_exc(file=sys.stderr)
				elif cmd == 'quit':
					is_quit = True
				else:
					break
		except:
			traceback.print_exc(file=sys.stderr)
		finally:
			# Clean up the connection
			connection.close()
			if is_quit:
				break
	browser.quit()

def set_proxy(proxy):
	if proxy == 'proxy':
		proxy = "cedump-sh.ap.qualcomm.com:9090"
	elif proxy == 'sdproxy':
		proxy = "secure-proxy2.qualcomm.com:9090"
	elif proxy == 'noproxy':
		proxy = None
	return proxy


global browser

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
	if timeout:
		browser = sf_start(None, proxy, timeout)
	else:
		browser = sf_start(None, proxy)
	run_server(server)
	time.sleep(6)
