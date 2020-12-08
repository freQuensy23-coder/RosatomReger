# This library contains APIs of Temp-Mail services and allows you to use them
# All classes have almost the same structure
# @author XazkerBoy (https://github.com/XazkerBoy/)
#
# Methods:
# __init__() - Initialise class
#	@param email (optional) The first part of an email address before @
#	@param domain (optional, not everywhere) Address domain from the list (see class domains variable)
# newEmail() - Create random new email address. Used on class init without custom email set
# (not everywhere) setEmail() - Set custom email address. Used on class init with custom email set
#	@param email (optional) Custom address. In most cases only the part before @
# getMessages() - Get all messages
# getMessage() - Get message contents
#	@param email_id Id of the email which content has to be fetched
# getAll() - Quickly get all fetched messages without refreshing the whole list (ONLY ONES, THAT WERE ALREADY FETCHED)
# (not everywhere) deleteEmail() - Delete existing email address. Used on class destruction
# getData() - Get email data (sometimes also returns secret key for debugging)
# (not everywhere) resetTime() - Reset time to 10 minutes

import requests as r
import json
import re
import random
import string

class Guerilla:		#guerrillamail.com
	mainurl = 'https://api.guerrillamail.com/ajax.php'	#API URL

	def __init__(self, email=None):		# Library init (email - custom name for mail)
		status = self.newEmail()
		if status != None:
			raise Exception(status)
		if email != None and email != '':
			status = self.setEmail(email)
			if status != None:
				raise Exception(status)
		self.seq = '2'	#Set last message id to 2 (1 - welcome email, we dont want to see it)

	# def __del__(self):	#Library destruct
	# 	self.deleteEmail()

	def newEmail(self):		#Create new email
		self.sess = r.Session()		#New requests session
		self.email = None	#Clear email address
		self.sid_token = None	#Clear sid_token (needed for auth)
		self.messinfo = []	#Clear messages list
		resp = self.sess.post(self.mainurl, data={'f': 'get_email_address'}).json()		#Request email address
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.email = resp['email_addr']	#Set got email
		self.sid_token = resp['sid_token']	#Set sid token (needed for all requests)

	def setEmail(self, email):	#Set custom email name
		if self.sid_token == None:
			return 'ERROR|TOKEN_NOT_SET';
		if email == None or email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if '@' in email:
			email = email.split('@')[0]		#Split email by @ and only use the first part
		resp = self.sess.post(self.mainurl, data={'f': 'set_email_user', 'sid_token': self.sid_token, 'email_user': email}).json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.email = resp['email_addr']
		self.sid_token = resp['sid_token']

	def getMessages(self):	#Get new messages
		if self.sid_token == None or self.sid_token == '':
			return 'ERROR|TOKEN_NOT_SET'
		resp = self.sess.post(self.mainurl, data={'f': 'check_email', 'sid_token': self.sid_token, 'seq': self.seq}).json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		counter = 0
		for info in resp['list']:
			if counter == 0:
				self.seq = info['mail_id']	#set the sequence number to highest id (to avoid showing old emails)
				counter += 1
			self.messinfo.append([info['mail_id'], info['mail_from'], info['mail_subject']])	#Append new message to all 
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_id):		#Get message body
		if self.sid_token == None or self.sid_token == '':
			return 'ERROR|TOKEN_NOT_SET'
		if email_id == None or email_id == '':
			return 'ERROR|ID_NOT_SET'
		resp = self.sess.post(self.mainurl, data={'f': 'fetch_email', 'sid_token': self.sid_token, 'email_id': email_id}).json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		return resp['mail_body']

	def getAll(self):	#Get all fetched messages
		if self.sid_token == None or self.sid_token == '':
			return 'ERROR|TOKEN_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def deleteEmail(self):	#Delete mail (on destruct)
		if self.sid_token == None or self.sid_token == '':
			return 'ERROR|TOKEN_NOT_SET'
		self.sess.post(self.mainurl, data={'f': 'forget_me', 'sid_token': self.sid_token})

	def getData(self):	#Get email data
		if self.sid_token == None or self.sid_token == '':
			return 'ERROR|TOKEN_NOT_SET'
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.email, self.sid_token]

class Fakemail:		#fakemail.net
	mainurl = 'https://www.fakemail.net/index/'

	def __init__(self, email=None):
		if email != None and email != '':
			self.setEmail(email)
		else:
			self.newEmail()

	def __del__(self):
		self.deleteEmail()

	def newEmail(self):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		resp = self.sess.get(self.mainurl + 'index', headers={'X-Requested-With': 'XMLHttpRequest'}).text
		resp = json.loads(resp[1:])		#Decode response without the first char (server-side error)
		self.email = resp['email']

	def setEmail(self, email):	#Set custom email name
		if email == None or email == '':
			return 'ERROR|EMAIL_NOT_SET'
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		if '@' in email:
			email = email.split('@')[0]		#Split email by @ and only use the first part
		resp = self.sess.post(self.mainurl + 'new-email', data={'emailInput': email}, headers={'X-Requested-With': 'XMLHttpRequest'}).text
		if 'ok' in resp:
			self.email = email + '@aallaa.org'
		else:
			return 'ERROR|' + resp

	def getMessages(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		resp = self.sess.post(self.mainurl + 'refresh', headers={'X-Requested-With': 'XMLHttpRequest'}).text
		resp = json.loads(resp[1:])
		self.messinfo = []
		for info in resp:
			self.messinfo.append([info['id'], re.findall('<(.*?)>', info['od'])[0], info['predmet']])	#Regex used to get only the email address
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_id):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if email_id == None or email_id == '':
			return 'ERROR|ID_NOT_SET'
		resp = self.sess.get(self.mainurl.replace('index', 'email') + 'id/' + str(email_id)).text
		return resp[1:]

	def getAll(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def resetTime(self):	#Add 10 minutes
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		self.sess.get(self.mainurl.replace('index', 'expirace/600'))

	def deleteEmail(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		self.sess.get(self.mainurl.replace('index', 'delete'))

	def getData(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return self.email

class NADA:		#getnada.com
	mainurl = 'https://getnada.com/api/v1/'
	domains = ['getnada.com', 'abyssmail.com', 'boximail.com', 'clrmail.com', 'dropjar.com', 'getairmail.com', 'givmail.com', 'inboxbear.com', 'robot-mail.com', 'tafmail.com', 'vomoto.com', 'zetmail.com']	#Mail domains

	def randomString(self, stringLength = 10):	#Random string generator
		letters = 'abcdefghijklmnopqrstuvwxyz'
		return ''.join([random.choice(letters) for n in range(stringLength)])

	def __init__(self, email=None, domain=None):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		if domain != None and 0 <= domain <= 11:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				self.email = email + '@' + self.domains[domain]		#If domain AND email are set
			else:
				self.email = self.randomString() + '@' + self.domains[domain]	#If only domain isset
		else:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				self.email = email + '@' + random.choice(self.domains)	#If only email isset
			else:
				self.email = self.randomString() + '@' + random.choice(self.domains)	#If nothing isset

	def newEmail(self):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		self.email = self.randomString() + '@' + random.choice(self.domains)

	def setEmail(self, email, domain = None):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		if email == None or email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if domain != None and 0 <= domain <= 11:
			if '@' in email:
				email = email.split('@')[0]
			self.email = email + '@' + self.domains[domain]
		else:
			if '@' in email:
				email = email.split('@')[0]
			self.email = email + '@' + random.choice(self.domains)

	def getMessages(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		resp = self.sess.get(self.mainurl + 'inboxes/' + self.email).json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.messinfo = []
		for info in resp['msgs']:
			self.messinfo.append([info['uid'], info['fe'], info['s']])
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_id):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if email_id == None or email_id == '':
			return 'ERROR|ID_NOT_SET'
		resp = self.sess.get(self.mainurl + 'messages/' + email_id).json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		return [resp['html'], resp['text']]

	def getAll(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def getData(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return self.email

class TenMMail:	#10minutemail.com
	mainurl = 'https://10minutemail.com/session/'

	def __init__(self):
		status = self.newEmail()
		if status != None:
			raise Exception(status)

	def newEmail(self):		#Create new email
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		self.messcontent = []
		resp = self.sess.get(self.mainurl + 'address').json()
		self.email = resp['address']	#Set got email

	def getMessages(self):	#Get new messages
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		resp = self.sess.get(self.mainurl.replace('session', 'messages') + 'messagesAfter/0').json()
		self.messinfo = []	#New messages
		self.messcontent = []
		for info in resp:
			self.messinfo.append([info['id'], info['sender'], info['subject']])		#Append new message
			self.messcontent.append([info['id'], info['bodyPlainText'], info['bodyHtmlContent']])	#Append message id and its content
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_id):		#Get message body
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if email_id == None or email_id == '':
			return 'ERROR|ID_NOT_SET'
		retvalue = None
		for message in self.messcontent:
			if message[0] == email_id:
				retvalue = [message[1], message[2]]		#Return content of the message with specified id
				break
		return retvalue

	def getAll(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def resetTime(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		self.sess.get(self.mainurl + 'reset')

	def getData(self):	#Get email data
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return self.email

class TempTop: #tempmail.top
	mainurl = 'https://tempmail.top/'
	domains = ['tempmail.top', 'spambox.win', 'dispomail.win']

	def __init__(self, email=None, domain=None):
		if domain != None and 0 <= domain <= 2:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				status = self.setEmail(email + '@' + self.domains[domain])
			else:
				status = self.newEmail()
		else:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				status = self.setEmail(email + '@' + random.choice(self.domains))
			else:
				status = self.newEmail()
		if status != None:
			raise Exception(status)

	def newEmail(self):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		self.messcontent = []
		resp = self.sess.get(self.mainurl + 'user.php?user=').text
		self.email = resp

	def setEmail(self, email):
		self.sess = r.Session()
		self.email = None
		self.messinfo = []
		self.messcontent = []
		resp = self.sess.get(self.mainurl + 'user.php?user=' + email).text
		self.email = resp

	def getMessages(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		resp = self.sess.get(self.mainurl + 'mail.php?unseen=0').text.replace('\n', '').replace('  ', '')	#Returns html, must be parsed with regex
		self.messinfo = []
		self.messcontent = []
		counter = 0
		for info in re.findall('class=\"subject\">(.*?)</div>', resp):
			self.messinfo.append([info, re.findall('class=\"tmail-email-sender float-left\">(.*?)</div>', resp)[counter]])
			self.messcontent.append([info, re.findall('class=\"body\">(.*?)</div>', resp)[counter]])
			counter+=1
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_subj):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		if email_subj == None or email_subj == '':
			return 'ERROR|ID_NOT_SET'
		retvalue = None
		for message in self.messcontent:
			if message[0].replace(' ', '').lower() == email_subj.replace(' ', '').lower():	#Match passed subject with subject in the content-list
				retvalue = message[1]
				break
		return retvalue

	def getAll(self):
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def getData(self):	#Get email data
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return self.email

class PostShift:	#post-shift.ru
	mainurl = 'https://post-shift.ru/api.php'
	domains = ['post-shift.ru', 'postshift.ru']

	def __init__(self, email=None, domain=None):
		if domain != None and 0 <= domain <= 1:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				status = self.setEmail(email + '@' + self.domains[domain])
			else:
				status = self.newEmail()
		else:
			if email != None and email != '':
				if '@' in email:
					email = email.split('@')[0]
				status = self.setEmail(email + '@' + random.choice(self.domains))
			else:
				status = self.newEmail()
		if status != None:
			raise Exception(status)

	def __del__(self):
		self.deleteEmail()

	def newEmail(self):		#Create new email
		self.sess = r.Session()
		self.email = None
		self.key = None
		self.messinfo = []
		resp = self.sess.get(self.mainurl + '?action=new&type=json').json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.email = resp['email']	#Set got email
		self.key = resp['key']

	def setEmail(self, email):	#Set custom email name
		self.sess = r.Session()
		self.email = None
		self.key = None
		self.messinfo = []
		resp = self.sess.get(self.mainurl + '?action=new&name=' + email.split('@')[0] + '&domain=' + email.split('@')[1] + '&type=json').json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.email = resp['email']
		self.key = resp['key']

	def getMessages(self):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		resp = self.sess.get(self.mainurl + '?action=getlist&key=' + self.key + '&type=json').json()
		if 'error' in resp:
			return 'ERROR|' + resp['error']
		self.messinfo = []
		if len(resp) == 0:
			return [self.messinfo, len(self.messinfo)]
		for info in resp:
			self.messinfo.append([info['id'], re.findall('<(.*?)>', info['from'])[0], info['subject']])
		return [self.messinfo, len(self.messinfo)]

	def getMessage(self, email_id):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		if email_id == None or email_id == '':
			return 'ERROR|ID_NOT_SET'
		resp = self.sess.get(self.mainurl + '?action=getmail&key=' + self.key + '&id=' + str(email_id) + '&type=json').json()
		return resp['message']

	def getAll(self):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		return [self.messinfo, len(self.messinfo)]

	def resetTime(self):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		self.sess.get(self.mainurl + '?action=update&key=' + self.key)

	def deleteEmail(self):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		self.sess.get(self.mainurl + '?action=clear&key=' + self.key)

	def getData(self):
		if self.key == None or self.key == '':
			return 'ERROR|KEY_NOT_SET'
		if self.email == None or self.email == '':
			return 'ERROR|EMAIL_NOT_SET'
		return [self.email, self.key]
