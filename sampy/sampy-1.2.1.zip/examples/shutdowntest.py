#!/usr/bin/env python

import time

from sampy import *
# Create a Hub Proxy
myhub=SAMPHubProxy()
myhub.connect()
# Create a client that uses
# the passed Hub Proxy
cli1=SAMPClient(hub=myhub)
metadata1={"samp.name":"Client 1",
           "samp.description.txt":"Test Client 1",
           "cli1.version":"0.01"}
# Start and register clients
cli1.start()
cli1.register()
cli1.declareMetadata(metadata1)

# Create a client that uses
# the passed Hub Proxy
cli2=SAMPClient(hub=myhub)
metadata2={"samp.name":"Client 2",
           "samp.description.txt":"Test Client 2",
           "cli2.version":"0.01"}
# Start and register clients
cli2.start()
cli2.register()
cli2.declareMetadata(metadata2)

cli3=SAMPClient(hub=myhub)
metadata3={"samp.name":"Client 3",
           "samp.description.txt":"Test Client 3",
           "cli3.version":"0.01"}
# Start and register clients
cli3.start()
cli3.register()
cli3.declareMetadata(metadata3)

cli4=SAMPClient(hub=myhub)
metadata4={"samp.name":"Client 4",
           "samp.description.txt":"Test Client 4",
           "cli4.version":"0.01"}
# Start and register clients
cli4.start()
cli4.register()
cli4.declareMetadata(metadata4)

cli5=SAMPClient(hub=myhub)
metadata5={"samp.name":"Client 5",
           "samp.description.txt":"Test Client 5",
           "cli5.version":"0.01"}
# Start and register clients
cli5.start()
cli5.register()
cli5.declareMetadata(metadata5)



# Function called when a notification is received
def test_receive_notification(private_key, sender_id, mtype, params, extra):
  print "Notification:", sender_id, params, "\n"

cli1.bindReceiveNotification("samp.hub.event.shutdown", test_receive_notification)
cli2.bindReceiveNotification("samp.hub.event.shutdown", test_receive_notification)
cli3.bindReceiveNotification("samp.hub.event.shutdown", test_receive_notification)
cli4.bindReceiveNotification("samp.hub.event.shutdown", test_receive_notification)
cli5.bindReceiveNotification("samp.hub.event.shutdown", test_receive_notification)

try:
  while True:
    time.sleep(0.01)
except KeyboardInterrupt:
  cli1.stop()
  cli2.stop()
  cli3.stop()
  cli4.stop()
  cli5.stop()