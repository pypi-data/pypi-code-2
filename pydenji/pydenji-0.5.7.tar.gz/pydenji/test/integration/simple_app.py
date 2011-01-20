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
    destination_filename_prefix = None
    
    def __init__(self, target_address):
        self.address = target_address

    def connect(self):
        # just mark it did something. # FIXME: Windows support?
        f = open(self.destination_filename_prefix + self.address, "w").write("something")
    


class SomeResource(object):
    pass

class SomeService(object):
    def __init__(self, NetworkedClassFactory):
        self.NetworkedClassFactory = NetworkedClassFactory

    def performAction(self):
        networkedclass = self.NetworkedClassFactory()
        networkedclass.doSomething()


