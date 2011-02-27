#!/usr/bin/env python

"""
A test of XMPP support, providing a simple chat interface.
"""

import libxml2dom.xmpp
import os
import sys

try:
    username, domain, password, mode = sys.argv[1:5]
except ValueError:
    print sys.argv[0], "<username> <domain> <password> <mode> [ <endpoint> ]"
    print
    print "For example:"
    print
    print sys.argv[0], "libxml2dom localhost jabber listen       # to listen"
    print sys.argv[0], "libxml2dom localhost jabber contact 1234 # to contact a listener"
    sys.exit(1)

receiving = mode == "listen"
register = mode == "register"
unregister = mode == "unregister"

# Get a peer to send messages to.

if not receiving and not register and not unregister:
    if len(sys.argv) > 5:
        peer = "%s@%s/%s" % (username, domain, sys.argv[5])
    else:
        print "Need to specify a peer to send messages to."
        sys.exit(1)

# Connect to the XMPP server.

s = libxml2dom.xmpp.Session(("localhost", 5222))
d = s.connect("localhost")

print "---- Connection ----"
print d.toString(prettyprint=1)

# Register if requested.

if register:
    print "---- Register ----"
    iq = s.createIq()
    iq.makeQuery()
    print iq.toString(prettyprint=1)
    s.send(iq)

    print "---- Response ----"
    d = s.receive()
    print d.toString(prettyprint=1)

    if not d.query.xpath("register:registered"):
        instructions = d.query.xpath("register:instructions")
        if instructions:
            print instructions[0].textContent

        print "---- Completing form ----"
        iq = s.createIq()
        iq.makeRegistration()
        iq.registration["username"] = username
        iq.registration["password"] = password
        print iq.toString(prettyprint=1)
        s.send(iq)

        print "---- Response ----"
        d = s.receive()
        print d.toString(prettyprint=1)

    s.disconnect()
    sys.exit(1)

print "---- Authentication ----"
auth = s.createAuth()
auth.mechanism = "PLAIN"
auth.setCredentials(username, username, password)
print auth.toString(prettyprint=1)
s.send(auth)

print "---- Response ----"
d = s.receive()
print d.toString(prettyprint=1)

if d.localName == "failure":
    if d.reason == "not-authorized":
        print "Not authorized: perhaps register first!"
        s.disconnect()
        sys.exit(1)

# Reconnect.

d = s.connect("localhost")

print "---- Authenticated connection ----"
print d.toString(prettyprint=1)

print "---- Binding ----"
iq = s.createIq()
iq.makeBind()
iq.bind.resource = str(os.getpid())
print iq.toString(prettyprint=1)
s.send(iq)

print "---- Response ----"
d = s.receive()
print d.toString(prettyprint=1)

print "---- Session ----"
iq = s.createIq()
iq.makeSession("localhost")
print iq.toString(prettyprint=1)
s.send(iq)

print "---- Response ----"
d = s.receive()
print d.toString(prettyprint=1)

# Unregister if requested.

if unregister:
    print "---- Unregister ----"
    iq = s.createIq()
    iq.makeUnregistration()
    print iq.toString(prettyprint=1)
    s.send(iq)

    print "---- Response ----"
    d = s.receive()
    print d.toString(prettyprint=1)

    s.disconnect()
    sys.exit(1)

# Otherwise, enter chat mode.

print "---- Chatting ----"
try:
    while 1:
        if not receiving:
            message = s.createMessage()
            message.from_ = "%s@%s/sender" % (username, domain)
            message.to = peer
            message.type = "chat"
            message.body = message.createBody()
            print "Enter message..."
            message_text = raw_input()
            text = message.ownerDocument.createTextNode(message_text)
            message.body.appendChild(text)
            print "Sending..."
            print message.toString(prettyprint=1)
            s.send(message)
            receiving = 1

        if receiving:
            print "Listening as %s..." % os.getpid()
            d = s.receive()
            print d.toString(prettyprint=1)
            print
            print "From:", d.from_
            print "To:", d.to
            print "Type:", d.type
            print
            if d.localName == "message":
                print "Message..."
                if d.type == "chat" and d.body:
                    print d.body.textContent
                elif d.event:
                    print "Composing?", d.event.composing
                    print "Delivered?", d.event.delivered
                    print "Displayed?", d.event.displayed
                    print "Offline?", d.event.offline
                    print "Id:", d.event.id
            elif d.localName == "presence":
                print "Presence..."
                if d.type == "subscribe":
                    presence = s.createPresence()
                    presence.type = "subscribed"
                    presence.from_ = d.to
                    presence.to = d.from_
                    print "Sending..."
                    print presence.toString(prettyprint=1)
                    s.send(presence)
                    d = s.receive()
                    print d.toString(prettyprint=1)
            print
            receiving = 0
            peer = d.from_

finally:
    s.disconnect()

# vim: tabstop=4 expandtab shiftwidth=4
