from tempmail import Guerilla, Fakemail, NADA, TenMMail, TempTop, PostShift

# mailclient = Guerilla()
mailclient = Fakemail()
# mailclient = TenMMail()
# mailclient = TempTop()
# mailclient = PostShift()
# mailclient = NADA()		#Init NADA client and get new mail address
print(mailclient.getData())		#Display mail address

while True:
	answer = input('[1] - New email address\r\n[2] - Refresh messages\r\n[3] - Get already fetched messages\r\nSelect action: ')
	if answer == '1':
		resp = mailclient.newEmail()	#Get new mail address
		if resp != None:	#Check email creation errors
			print(resp)
			continue
		print(mailclient.getData())
	elif answer == '2':
		messages = mailclient.getMessages()	#Get messages
		if type(messages) == 'str':
			print(messages)
			continue
		print('Message count: ' + str(messages[1]))	#Print message count
		if messages[1] > 0:
			for message in messages[0]:	#Display each message
				print('Message info:')
				print(message)
				print('Message body:')
				print(mailclient.getMessage(message[0]))
	elif answer == '3':
		messages = mailclient.getAll()	#Get fetched messages
		if type(messages) == 'str':
			print(messages)
			continue
		print('Message count: ' + str(messages[1]))	#Print message count
		if messages[1] > 0:
			for message in messages[0]:	#Display each message
				print('Message info:')
				print(message)
				print('Message body:')
				print(mailclient.getMessage(message[0]))
