#!/usr/bin/python
#/root/letsencrypt/letsencrypt-auto -c mail.kali-quebec.org.ini -d mail.kali-quebec.org certonly

"""
Script to Auto-Renew Let's encrypt cert and send mail in failure case
"""

import subprocess
import smtplib
import time

version = 1.0

############################CHANGE LOG#############################################
#
#-Modify script to be use with the new certbot-auto client
#-Change the email Message to contain the output of command instead of the custom message if succeful
#-Change the domains list to fit the new requirement of the certbot-auto
#-.ini file no longer needed
#
###################################################################################

############################SET YOUR DOMAIN HERE###################################

"""
declare domain to renew cert in a dictionnary 
"""

domains={}#create an empty dictionnary
"""
form : domains['DOMAINNAME']=['webroot of website', 'DOMAIN NAME FOR -d OPTION', 'OTHER -d OPTION']
"""
domains['mail.kali-quebec.org'] = ['/opt/www/roundcubemail/', 'mail.kali-quebec.org']


domains['kali-quebec.org'] = ['/var/www/html/kali-quebec.org/', 'kali-quebec.org', "www.kali-quebec.org"]

####################################################################################

#create a list of the service you want to restart

services = ["apache2","dovecot","postfix"]

#############Start of program function#####################

def testError(out, err):
	"""
	Function to test if any error occured when running the command
	"""
	global mailMessage#accessing the global variable
	
	if out.find("""Congratulations!"""):
		mailMessage = mailMessage + out
	else :
		mailMessage = mailMessage + """An error occured renewing the ssl cert for the domain, See above error message:\n{0}\n\n""".format(err)

def sendReport(mailMessage):
	"""
	Function to send the report by mail
	"""
	
	###########Function variable#######
	to=["To@domain.com"]#######
	server="localhost"#################
	senders="from@domain.com"##
	userPwd="password"#################
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
	command.append('/usr/local/sbin/certbot-auto')
	command.append('certonly')
	command.append('--force-renewal')#force renewal of the cert
	command.append('-n')#non interactive mode
	command.append('--webroot')
	i=1
	
	while (i < len(domains[domain])):
		command.append('-d')
		command.append(domains[domain][i])
		i = i + 1
	command.append("--webroot-path")
	command.append(domains[domain][0])
		
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	out, err = p.communicate()
	testError(out, err)
restartService(services)
time.sleep(10)#wait 10 second for service to restart
sendReport(mailMessage)

########################################################
