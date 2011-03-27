#!/usr/bin/env python
#coding: utf-8

import ftplib
import os
import command
from ConfigParser import ConfigParser

class BaseError(Exception): pass
class ConnectionError(BaseError): pass
class ArgumentError(BaseError): pass

class Parse_args:
	def __init__(self, args):
		self.modes = Modes()
		if args.nomal:       self.modes.NomalMode()
		if args.config_file: self.modes.UseConfigMode(args.config_file)
		if args.opts:        self.modes.UploadMode(args.opts)
	
class Modes:
	def NomalMode(self):
		print " Welcome to ftpterm. ".center(50,"+")
		print " Please input host name. ".center(50,"+")
		host = raw_input("host > ")
		print " Please input user name and password. ".center(50,"+")
		user = raw_input("user > ")
		passwd = raw_input("password > ")
		
		conn = self.Login(host, user, passwd)
		command.RunTerm(conn, (host,user,passwd))
		
	def UseConfigMode(self, config_file):
		if self.check_acs(config_file) == False:
			raise NameError("%s file is not exists." % config_file)
		
		host, user, passwd = self.get_data(config_file)
		conn = self.Login(host, user, passwd)
		command.RunTerm(conn, (host,user,passwd))
		
	def UploadMode(self, options):
		upload_file, config_file, filepath = self.parse_opt(options)
		
		if config_file == "":
			host, user, passwd = self.inputdata()
			conn = self.Login(host, user, passwd)
		else:
			host, user, passwd = self.get_data(config_file)
			conn = self.Login(host, user, passwd)
		
		command.Upload(conn, upload_file, filepath)
	
	#
	# Sub Methods
	# --------------------------
	def Login(self, host, user, passwd):
		try:
			conn = ftplib.FTP(host, user, passwd)
		except: raise ConnectionError("Can't Connect. invalid data.")
		
		return conn
	
	def parse_opt(self, opts):
		if len(opts) != 3:
			raise ArgumentError("options is not suitable. Please show help use -h option.")
		
		upload_file = opts[0]
		config_file = opts[1]
		filepath = opts[2]
		return upload_file, config_file, filepath
	
	def check_acs(self, file):
		return True if os.access(file, os.F_OK) else False
		
	def get_data(self, file):
		conf = ConfigParser()
		conf.read(file)
		
		try:
			host = conf.get("setting", "host")
			user = conf.get("setting", "user")
			passwd = conf.get("setting", "pass")
		except:
			host = conf.get("Setting", "host")
			user = conf.get("Setting", "user")
			passwd = conf.get("Setting", "pass")
		
		return host, user, passwd
		
	def inputdata(self):
		print " Please input host, user, pass. ".center(50, "+")
		host = raw_input("host > ")
		user = raw_input("user > ")
		passwd = raw_input("pass > ")
		
		return host, user, passwd