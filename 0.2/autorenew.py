#!/usr/bin/python

"""
Script to Auto-Renew Let's encrypt cert and send mail in failure case
"""

import subprocess
import smtplib
import time

version = 0.2
############################SET YOUR DOMAIN HERE###################################

"""
declare domain to renew cert in a dictionnary 
"""

domains={}#create an empty dictionnary
"""
form : domains['DOMAINNAME']=['FULL PATH OF .INI FILE', 'DOMAIN NAME FOR -d OPTION', 'OTHER -d OPTION']
"""
domains['DOMAIN NAME'] = ['/PATH/TO/FILE.ini', 'DOMAIN']

####################################################################################

#create a list of the service you want to restart

services = ["apache2","dovecot","postfix"]

#############Start of program function#####################

def testError(err):
	"""
	Function to test if any error occured when running the command
	"""
	global mailMessage#accessing the global variable
	if err:
		mailMessage = mailMessage + """An error occured renewing the ssl cert for the domain. See above error Message:\n{0}\n""".format(err)
	else:
		mailMessage = mailMessage + """The ssl cert for the domain as succefully renewed\n """

def sendReport(mailMessage):
	"""
	Function to send the report by mail
	"""
	
	###########Function variable#######
	to=["TO@DOMAIN.ORG"]#######
	server="localhost"#################
	senders="FROM@DOMAIN.ORG"##
	userPwd="PASSWORD"#################
	###################################

	message = """FROM: Reports {0}
To: admin {1}
Subject: SSL Certificate Renewal Report

{2}

""".format(senders, to[0], mailMessage)
	smtpObj = smtplib.SMTP('localhost')
	smtpObj.sendmail(senders, to, message)
	
def restartService(services):
	"""
	function to restart service and logo data
	"""
	global mailMessage

	mailMessage = mailMessage + """
	Service restart report:\n
	Following you will got the report of service restart and the error if any occured.\n
	"""

	for service in services:
		prog = ('/usr/sbin/service')
		action = "restart"
		command = [prog, service, action]
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		if err:
			 mailMessage = mailMessage + """{0} : {1}\n """.format(service, err)
		
		else:
			mailMessage = mailMessage + """{0} : OK\n""".format(service)
	
###########################################################

################Start of main function#####################

"""
let's encrypt executable
"""
letsEncrypt = "/root/letsencrypt/letsencrypt-auto"

mailMessage = """SSL Certificate Renewal Report\nScript version: {0}\n\n""".format(version)

#loop to renew all domain
for domain in domains:
	mailMessage = mailMessage + """For domain {0}:\n""".format(domain)
	command = []
	command.append('/root/letsencrypt/letsencrypt-auto')
	command.append('-c')
	command.append(domains[domain][0])
	i=1
	
	while (i < len(domains[domain])):
		command.append('-d')
		command.append(domains[domain][i])
		i = i + 1
	command.append("auth")
	
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	out, err = p.communicate()
	testError(err)
restartService(services)
time.sleep(10)#wait 10 second for service to restart usefull if you send mail with the server you're refreshing cert
sendReport(mailMessage)
########################################################
