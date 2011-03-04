from sampy import *
import time

# Create a client
cli1 = SAMPIntegratedClient(metadata = {"samp.name":"Client 1",
                                        "samp.description.text":"Test Client 1",
                                        "cli1.version":"0.01"})
# Create another client
cli2 = SAMPIntegratedClient(metadata = {"samp.name":"Client 2",
                                        "samp.description.text":"Test Client 2",
                                        "cli2.version":"0.25"})

# Connect them
cli1.connect()
cli2.connect()


print "CLI1", cli1.getPrivateKey(), cli1.getPublicId()
print "CLI2", cli2.getPrivateKey(), cli2.getPublicId()


# Function called when a notification is received
def test_receive_notification(private_key, sender_id, mtype, params, extra):
  print "Notification:", private_key, sender_id, mtype, params, extra

# Function called when a call is received
def test_receive_call(private_key, sender_id, msg_id, mtype, params, extra):
  print "Call:", private_key, sender_id, msg_id, mtype, params, extra
  cli1.ereply(msg_id, SAMP_STATUS_OK, result = {"txt": "printed"})

# Function called when a response is received
def test_receive_response(private_key, sender_id, msg_id, response):
  print "Response:", private_key, sender_id, msg_id, response

# Subscribe Client 1 to "samp.*" and "samp.app.*" MType and bind it to
# the related functions
cli1.bindReceiveNotification("samp.app.*", test_receive_notification)
cli1.bindReceiveCall("samp.app.*", test_receive_call)

# Bind Client 2 message-tags received to suitable functions
cli2.bindReceiveResponse("my-dummy-print", test_receive_response)
cli2.bindReceiveResponse("my-dummy-print-specific", test_receive_response)

# Client 2 notifies to All "samp.app.echo" MType using myhub
cli2.enotifyAll("samp.app.echo", txt = "Hello world!")

print cli2.getSubscribedClients("samp.app.echo")


time.sleep(2)

# Client 2 calls to All "samp.app.echo" MType using "my-dummy-print"
# as message-tag
print cli2.callAll("my-dummy-print",
                   {"samp.mtype": "samp.app.echo",
                    "samp.params": {"txt": "Hello world!"}})

time.sleep(2)

# Client 2 calls "samp.app.echo" MType on Client 1 tagging it as 
# "my-dummy-print-specific"
try:
  print cli2.call(cli1.getPublicId(),
                  "my-dummy-print-specific",
                  {"samp.mtype": "samp.app.echo",
                   "samp.params": {"txt": "Hello Cli 1!"}})
except SAMPProxyError, e:
  print "Error (%s): %s" % (e.faultCode, e.faultString)


time.sleep(2)

# Function called to test synchronous calls
def test_receive_sync_call(private_key, sender_id, msg_id, mtype, params, extra):
  print "SYNC Call:", sender_id, msg_id, mtype, params, extra
  time.sleep(2)
  cli1.reply(msg_id, {"samp.status": SAMP_STATUS_OK,
                      "samp.result": {"txt": "printed sync"}})

# Bind test MType for sync calls
cli1.bindReceiveCall("samp.test", test_receive_sync_call)  

now = time.time()

print "SYNCRO --->\n\n"
try:
  # Sync call
  print cli2.callAndWait(cli1.getPublicId(), 
                         {"samp.mtype": "samp.test", 
                          "samp.params": {"txt": "Hello SYNCRO Cli 1!"}},
                         "10")
except SAMPProxyError, e:
  # If timeout expires than a SAMPProxyError is returned
  print "Error (%s): %s" % (e.faultCode, e.faultString)

print "<------SYNCRO (%d) \n\n" % (time.time() - now)

time.sleep(6)

cli1.disconnect()
cli2.disconnect()
