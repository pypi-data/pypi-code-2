#!/usr/bin/env python

import warnings
import logging
import time
import copy
import xmpp

# Base classes for defining common elements to conversations:

class BaseConvo(object):
    """
    Base class for all conversation types.
    
    Implement .process on subclasses to actually do things.
    """
    def __init__(self, bot):
        self.bot = bot
        self.other_side = None
        self.kill_me = False
    def send(self, msg):
        msg.setTo(self.other_side)
        self.bot.send(msg)
    def process(self, msg):
        self.kill_me = True
        warnings.warn("'process' not implemented")

class MessageConvo(BaseConvo):
    pass

# Composited classes for actual subclassing into functional conversational
# models:

class MessageConvoMultiUserChat(MessageConvo):
    def send(self, msg):
        room = self.other_side
        room.setResource('')
        msg.setTo(room)
        self.bot.send(msg)

class MessageConvoSimple(MessageConvo):
    pass

class PresenceConvo(BaseConvo):
    pass

class IqConvo(BaseConvo):
    pass

# Test convos:

class EchoConvoMuc(MessageConvoMultiUserChat):
    def __init__(self, *args, **kwargs):
        MessageConvoMultiUserChat.__init__(self, *args, **kwargs)
        self.message_count = 0
    def process(self, msg):
        if msg.getBody() == "end":
            self.kill_me = True
        self.message_count += 1
        from_name = msg.getFrom().getResource()
        room_name = copy.copy(msg.getFrom())
        room_name.setResource('')
        room_name = unicode(room_name)
        if from_name == '' or (room_name in self.bot.rooms and \
                               from_name == self.bot.rooms[room_name].me):
            return
        if msg.getBody() is not None:
            new_msg = xmpp.protocol.Message()
            new_msg.setBody(msg.getBody() + (" %d" % self.message_count))
            self.send(new_msg)

class EchoConvo(MessageConvoSimple):
    def __init__(self, *args, **kwargs):
        MessageConvoSimple.__init__(self, *args, **kwargs)
        self.message_count = 0
    def process(self, msg):
        if msg.getBody() == "end":
            self.kill_me = True
        self.message_count += 1
        if msg.getBody() is not None:
            new_msg = xmpp.protocol.Message()
            new_msg.setBody(msg.getBody() + (" %d" % self.message_count))
            self.send(new_msg)

# Stubs of factories for producing the subclasses of the above classes that you
# make:

def message_convo_multi_user_chat_factory(bot, msg):
    return MessageConvoMultiUserChat(bot)

def message_convo_simple_factory(bot, msg):
    return MessageConvoSimple(bot)

def presence_convo_factory(bot, msg):
    return PresenceConvo(bot)

def iq_convo_factory(bot, msg):
    return IqConvo(bot)

# Server state classes:

class MultiUserChat(object):
    """
    """
    def __init__(self, node, server, me):
        self.name = node
        self.server = server
        self.me = me
        self.members = set()
    def __unicode__(self):
        return "%s@%s" % (self.name, self.server)
    __str__ = __unicode__
    def add_user(self, jid):
        self.members.add(jid)
    def remove_user(self, jid):
        try:
            self.members.remove(jid)
        except KeyError:
            pass

# Bot framework is basically a system for authenticating against the server,
# and then routing messages to and from conversation objects.  It also manages
# their lifecycle, from creation to destruction.  It also handles miscellaneous
# other information about users and the server, such as who is in a MUC.

class Bot(object):
    """
    This class holds an instance of xmpp.client.Client and manages lifecycle of
    Convos, then routes new stanzas to the appropriate Convo.
    """
    def __init__(self, node, server, resource):
        self.jid = xmpp.protocol.JID("%s@%s" % (node, server))
        self.jid.setResource(resource)
        self.conn = None
        self.__last = int(time.strftime('%s', time.localtime()))
        self.conversations = {}
        self.rooms = {}
    def __get_or_make_convo(self, msg):
        msg_from = copy.copy(msg.getFrom())
        if msg_from is not None:
            msg_from.setResource('')
        msg_name = msg.getName()
        try:
            convo = self.conversations[(msg_name, msg_from)]
        except KeyError:
            if msg_name == 'message':
                msg_type = msg.getType()
                if msg_type == 'groupchat':
                    convo = message_convo_multi_user_chat_factory(self, msg)
                else:
                    convo = message_convo_simple_factory(self, msg)
            elif msg_name == 'presence':
                convo = presence_convo_factory(self, msg)
            elif msg_name == 'iq':
                convo = iq_convo_factory(self, msg)
            try:
                convo
            except NameError:
                return
            msg_from = msg.getFrom()
            convo.other_side = msg_from
            self.conversations[(msg_name, msg_from)] = convo
        return convo
    def __stanza_handler(self, conn, stanza):
        convo = self.__get_or_make_convo(stanza)
        if convo is None:
            return
        try:
            convo.process(stanza)
        except Exception, e:
            exc_string = "%s: %s" % (e.__class__.__name__, e)
            logging.error(exc_string)
        if convo.kill_me:
            key = (stanza.getName(), stanza.getFrom())
            try:
                del self.conversations[key]
            except KeyError:
                pass
    def __idle_process(self):
        time.sleep(1)
        now = int(time.strftime('%s', time.localtime()))
        delta = now - self.__last
        if delta > 60:
            self.__last = now
            self.conn.send(xmpp.protocol.Presence())
        if delta % 10 == 0:
            self.periodic_action()
    def periodic_action(self):
        pass
    def on_connect(self):
        self.join('test', 'rooms.transneptune.net', 'Testbot Mcgee')
    def send(self, msg):
        self.conn.send(msg)
    def join(self, room, domain, desired_name):
        """
        This attempts to join room@domain as desired_name, appending _ to the
        name until it works.

        TODO Not yet completely functional.
        """
        r2j = xmpp.protocol.JID(node=room,
                                domain=domain,
                                resource=desired_name)
        self.conn.send(xmpp.protocol.Presence(to=r2j))
        new_room = MultiUserChat(room, domain, desired_name)
        self.rooms[unicode(new_room)] = new_room
    def connect(self, password):
        if self.conn is None:
            conn = xmpp.client.Client(self.jid.getDomain(), )#debug=[])
            if not conn.connect():
                logging.critical('Unable to connect.')
                return
            if not conn.auth(self.jid.getNode(), password,
                             self.jid.getResource()):
                logging.critical('Unable to authorize.')
                return
            conn.RegisterHandler('message', self.__stanza_handler)
            conn.RegisterHandler('presence', self.__stanza_handler)
            conn.RegisterHandler('iq', self.__stanza_handler)
            conn.sendInitPresence()
            self.conn = conn
            self.on_connect()
        return self.conn
    def serve(self):
        if self.conn is None:
            logging.error('Please connect before serving!')
        while True:
            try:
                self.conn.Process(1)
                self.__idle_process()
            except KeyboardInterrupt:
                break
        return

if __name__ == "__main__":
    import sys
    import os
    LOG_FILENAME = "%s.log" % (os.path.splitext(sys.argv[0])[0])
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    b = Bot('test', 'transneptune.net', 'Testbot')
    b.connect('^^password^^')
    b.serve()
