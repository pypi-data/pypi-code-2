#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni


class SomeNetworkedClass(object):
    def __init__(self, connector, resource):
        self.connector = connector
        self.resource = resource

    def doSomething(self):
        self.connector.connect()


class SomeConnector(object):
    def __init__(self, address):
        self.address = address

    def connect(self):
        # just mark it did something. # FIXME: Windows support?
        f = open("/tmp/pydenji_simple_configuration_test_%s" % self.address, "w").write("something")


class SomeResource(object):
    pass

class SomeService(object):
    def __init__(self, NetworkedClassFactory):
        self.NetworkedClassFactory = NetworkedClassFactory

    def performAction(self):
        networkedclass = self.NetworkedClassFactory()
        networkedclass.doSomething()


