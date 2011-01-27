#!/usr/bin/env python
# encoding: utf-8
"""
network.py

Manage network connections.

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""

import logging

from cifitlib.files import run
from cifitlib.classes import classes,Storage

log = logging.getLogger('%s:network' % classes['hostname'])

class NetObject(Storage):
	"""
	defined here for definition purposes.
	keys we expect & support:
		interface:
		address
		netmask
		broadcast
		gateway
	"""
	pass

class NetBase(object):
	"""base class"""
	def __init__(self):
		pass

	def listInterfaces(self):
		"""return a list of interfaces
		{interface:[address]}
		"""
		ints = {}
		ret,out = run('ifconfig')
		if not ret:
			for line in out:
				if line[:1] != '\t':
					blah = line.split(':')
					i = blah[0]
					ints[i] = []
				if line.startswith('\tinet'):
					ip = line.split(' ')
					#print ip
					ip = ip[1]
					ints[i].append(ip)
		return ints

	def isAddress(address):
		"""returns Interface or False if address exists on any interface"""
		for k,v in self.listInterfaces():
			if address in v:
				return k
		return False

#end NetBase
class NetDebian(NetBase):
	def addInterface(self,netobj):
		"""add Interface to a Debian system.
		netobj should be a {}.
		"""
		pass

	def addVirtualInterface(self,netobj):
		"""add virtual interface to a debian system.
		this is essentially the same thing as above, except interface can be left blank,
		if there is a network already setup on an interface that makes sense for this link.

		"""
		pass

class NetDarwin(NetBase):
	def addVirtualAddress(self,NetObject):
		"""Add a virtual address to NetObject.interface"""
		if self.isAddress(NetObject.address):
			log.debug('already added')
			return None
		cmd = "ifconfig %s alias %s" % (NetObject.interface,NetObject.address)
		ret,out = run(cmd)
		if ret:
			log.error('error adding address:%s' % out)
		return ret
	def delVirtualAddress(self,NetObject):
		"""remove a virtaual address from NetObject.interface if it exists."""
		interfaces = self.listInterfaces()
		if NetObject.interface in interfaces:
			interface = interfaces[NetObject.interface]
			if NetObject.address in interface:
				cmd = "ifconfig %s -alias %s" % \
		(NetObject.interface,NetObject.address)
				ret,out = run(cmd)
				if ret:
					log.error('error removing address:%s' % (out))
			else:
				log.debug('no valid existing interface')
		else:
			log.debug('no valid interface')
		return



if __name__ == '__main__':
	x = NetDebian()
	print x.listInterfaces()


