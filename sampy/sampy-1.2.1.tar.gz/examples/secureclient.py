#!/usr/bin/python
import sampy
import time

def receive_notify(private_key, sender_id, mtype, params, extra):
	
	print "Extra:", extra
	

cli1 = sampy.SAMPIntegratedClient(metadata={"samp.name": "Example 1"})
cli2 = sampy.SAMPIntegratedClient(metadata={"samp.name": "Example 2"})

#cli1.connect(user = "admin", password = "c0sm0s")
#cli2.connect(user = "admin", password = "c0sm0s")
cli1.connect()
cli2.connect()


cli2.bindReceiveNotification("test.notify", receive_notify)

cli1.enotify(cli2.getPublicId(), "test.notify")


try:
	
	while True:
		time.sleep(0.01)
		
except KeyboardInterrupt:
	
	try:
		cli1.disconnect()
		cli2.disconnect()
	except:
		pass
	