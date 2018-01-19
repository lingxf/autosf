#!/usr/bin/python
# _*_ coding: utf-8 -*-
import smtplib	
import os
import sys
import traceback
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
 
# python 2.3.*: email.Utils email.Encoders
from email.utils import COMMASPACE,formatdate
from email import encoders

mailto_list=['xling@qti.qualcomm.com']
mailto_list=['ce.cps.cn.labsp.qc@qti.qualcomm.com']
#mailto_list=['xling@cedump-sh.ap.qualcomm.com']
mail_host="localhost"  #设置服务器
#mail_host="smtp.qualcomm.com"	#设置服务器
mail_host="cedump-sh.ap.qualcomm.com"	#设置服务器
mail_user="xling"	 #用户名
mail_pass=""   #口令 
mail_postfix="qti.qualcomm.com"  #发件箱的后缀
  
def send_mail(to_list,sub, text, files=[]):  
	me="Admin"+"<"+mail_user+"@"+mail_postfix+">"  
	#msg = MIMEText(content,_subtype='text/html',_charset='utf-8')	
	msg = MIMEMultipart() 
	msg['Subject'] = sub  
	msg['From'] = me  
	msg['To'] = ";".join(to_list)  
	msg['From'] = me
	msg['Date'] = formatdate(localtime=True) 
	msg.attach(MIMEText(text)) 
	for file in files: 
	   part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
	   part.set_payload(open(file, 'rb'.read())) 
	   encoders.encode_base64(part) 
	   part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file)) 
	   msg.attach(part) 

	try:  
		server = smtplib.SMTP()  
		server.connect(mail_host)  
		#server.login(mail_user,mail_pass)	
		server.sendmail(me, to_list, msg.as_string())  
		server.close()	
		return True  
	except Exception, e:  
		print str(e)  
		return False  

def error_mail(cmd):
	subject = "Auto server run error:%s" % cmd
	f = open("error.tmp", "w+")
	traceback.print_exc(file=sys.stderr)
	traceback.print_exc(file=f)
	f.close()
	f = open("error.tmp", "r")
	msg = ""
	for line in f:
		msg += line + '\r'
	send_mail(['xling@qti.qualcomm.com'], subject, msg )

if __name__ == '__main__':	
	#f = os.popen("php std_report.php l01")
	#rp = "\r".join(f.readlines())
	rp = "Test"
	if send_mail(mailto_list,"Test", rp): 
		print "发送成功"  
	else:  
		print "发送失败"  

