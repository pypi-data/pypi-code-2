#!/usr/bin/env python

import time
from sampy import *


# CREATE A SAMP CLIENT

cli1 = SAMPIntegratedClient({"samp.name":"Client 1",
                             "samp.description.text":"Test Client 1"})

# GENERIC FUNCTION TO GET ANY MTYPE

def get_message(private_key, sender_id, msg_id, mtype, params, extra):

    print private_key, sender_id, msg_id, mtype, params, extra
    cli1.reply(msg_id, {"samp.status": SAMP_STATUS_OK,
                        "samp.result": {"result": "ok guys"}})


# GENERIC FUNCTION TO GET ANY MTYPE WRAPPED TO 
# SIMPLIFY THE RESPONSE RETURNED
@SAMPMsgReplierWrapper(cli1)
def get_message_wrapped(private_key, sender_id, msg_id, mtype, params, extra):

    print private_key, sender_id, msg_id, mtype, params, extra
    return {"result": "ok guys"}


# CONNECT CLIENT 1
cli1.connect()
# BIND NON WRAPPED FUNCTION AND WRAPPED FUNCTION
cli1.bindReceiveMessage("my.test.mtype1", get_message)
cli1.bindReceiveMessage("my.test.mtype2", get_message_wrapped)

# CREATE AND CONNECT CLIENT 2
cli2 = SAMPIntegratedClient({"samp.name":"Client 2",
                             "samp.description.text":"Test Client 2"})
cli2.connect()


# CALL NON WRAPPED FUNCTION
print cli2.ecallAndWait(cli1.getPublicId(), "my.test.mtype1", \
                        "5", txt = "sample text", \
                        extra_kws = {"my.extra.info": "just an example"})

try:
    # CALL WRAPPED FUNCTION
    print cli2.ecallAndWait(cli1.getPublicId(), "my.test.mtype2", \
                            "5", txt = "sample text", \
                            extra_kws = {"my.extra.info": "just an example"})
except SAMPProxyError, err:
    print err.faultCode, err.faultString

# NOTIFY NON WRAPPED FUNCTION
cli2.enotifyAll("my.test.mtype1", txt = "sample text")
# NOTIFY WRAPPED FUNCTION
cli2.enotifyAll("my.test.mtype2", txt = "sample text")

# WAIT A LITTLE
time.sleep(0.5)

# BYE
cli1.disconnect()
cli2.disconnect()