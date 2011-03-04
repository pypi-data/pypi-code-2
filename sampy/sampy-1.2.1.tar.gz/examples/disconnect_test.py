#!/usr/bin/python

import sampy
import time

def get_notification(private_key, sender_id, mtype, params, extra):
	
	print "Notification %s received" % mtype

cli = sampy.SAMPIntegratedClient(metadata = {"samp.name": "Disconnect test"})
cli.connect()
cli.bindReceiveNotification("samp.hub.disconnect", get_notification)


try:
	
	while True:
		time.sleep(0.01)
			
except KeyboardInterrupt:
	
	try:
		cli.disconnect()
	except:
		pass