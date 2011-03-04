#!/usr/bin/env python
############################################################################
##
##   sampasswd.py - This script allows to manage SAMPy authentication
##                  files
##                  
##
##
##   Copyright (C) 2008  INAF-IASF Milano
##
##   This program is free software; you can redistribute it and/or
##   modify it under the terms of the GNU General Public License
##   as published by the Free Software Foundation; either version 2
##   of the License, or (at your option) any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.
##
##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##   MA 02110-1301, USA.
##
##   Authors:
##
##   Luigi Paioro
##   INAF - Istituto Nazionale di Astrofisica
##
##   IASF Milano
##   Via Bassini 15, I-20133 Milano, Italy
##   E-mail: luigi at iasf-milano.inaf.it
##   Site  : http://www.iasf-milano.inaf.it/
##
################################################################################
##
##   Automatic keywords:
##   $Date: 2011-03-04 10:09:03 +0100 (Fri, 04 Mar 2011) $
##   $Revision: 665 $
##   $Author: luigi $
##   $HeadURL: http://cosmos.iasf-milano.inaf.it/svn/fase/trunk/framework/samp/python/utils/sampasswd.py $
##   $Id: sampasswd.py 665 2011-03-04 09:09:03Z luigi $
##
################################################################################


__author__   = "Luigi Paioro <luigi at iasf-milano.inaf.it>"
__status__   = "development"
__release__  = "1.0"
__revision__ = "$Revision: 665 $"
__date__     = "$Date: 2011-03-04 10:09:03 +0100 (Fri, 04 Mar 2011) $"

import hashlib
import bsddb
import sys
import os
import getpass

def add(filename, user, group):
	db = bsddb.hashopen(filename, "w")
	if user in db.keys():
		print "WARNING: User %s is already present in file %s!" % (user, filename)
	else:
		password = getpass.getpass("Input password:")
		password2 = getpass.getpass("Verify password:")
		if password2 == password:
			db[user] = "%s%s" % (hashlib.md5(password).digest(),group)
		else:
			print "WARNING: Password verification failed, user %s not added." % user
	db.close()

def delete(filename, user):
	db = bsddb.hashopen(filename, "w")
	if db.has_key(user):
		del(db[user])
	db.close()

def list_users(filename):
	db = bsddb.hashopen(filename, "r")
	users = db.keys()
	users.sort()
	max_len = 0
	for user in users:
		max_len = max([max_len, len(user)])
	print "%s %s" % ("NAME".ljust(max_len), "GROUPS")
	for user in users:
		print "%s %s" % (user.ljust(max_len), db[user][16:])
	db.close()


import optparse

parser = optparse.OptionParser(version="%prog " + __release__)
parser.disable_interspersed_args()

parser.add_option("-f", "--file-name", dest = "filename", metavar = "FILE",
									help = "password file name (mandatory).")

parser.add_option("-u", "--user-name", dest = "username", metavar = "USER",
									help = "user's name.")

parser.add_option("-g", "--group-name", dest = "groupname", metavar = "GROUP",
									help = "user's group name or comma separated list of groups.")

actions = optparse.OptionGroup(parser, "Actions", "Actions to be executed " \
															 "with the selected user and/or password file.")

actions.add_option("-l", "--list", dest = "list_usr", action = "store_true",
									 help = "list the users.")

actions.add_option("-a", "--add", dest = "add_usr", action = "store_true",
									 help = "add a new user.")

actions.add_option("-d", "--delete", dest = "delete_usr", action = "store_true",
									 help = "delete the user.")

actions.add_option("-c", "--create", dest = "create_file", action = "store_true",
									 help = "create password file if missing.")


parser.add_option_group(actions)

parser.set_defaults(filename = None)
parser.set_defaults(username = None)
parser.set_defaults(groupname = "default")
parser.set_defaults(list_usr = False)
parser.set_defaults(add_usr = False)
parser.set_defaults(delete_usr = False)
parser.set_defaults(create_file = False)

(options, args) = parser.parse_args()

if options.filename == None:
	print "WARNING: Password file name is mandatory!"
	sys.exit(1)

if options.create_file == False:
	if not os.path.isfile(options.filename):
		print "WARNING: Unable to open file %s!" % options.filename
		sys.exit(1)

if options.list_usr == False and options.add_usr == False and options.delete_usr == False:
	print "WARNING: Specify the action to be performed!"
	sys.exit(1)

if options.list_usr == True:
	list_users(options.filename)
	sys.exit(1)

if options.add_usr == True:
	if options.username == None:
		print "WARNING: User's name is mandatory in order to add a new user!"
	else:
		add(options.filename, options.username, options.groupname)
	sys.exit(1)

if options.delete_usr == True:
	if options.username == None:
		print "WARNING: User's name is mandatory in order to delete user!"
	else:
		delete(options.filename, options.username)
	sys.exit(1)

