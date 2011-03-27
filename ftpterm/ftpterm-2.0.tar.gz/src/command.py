#!/usr/bin/env python
#coding: utf-8

import os
import sys
import readline
from socket import gethostbyname

class RunTerm:
	def __init__(self, conn, data):
		self.conn = conn
		self.data = data # <= (host, user, pass)
		self.EndofLoop = False
		
		user = self.data[1]
		while self.EndofLoop == False:
			self.conn.sendcmd("NOOP")
			cwd = self.conn.pwd().split("/")[-1]
			self.prompt = "%s:[%s] > " % (user,cwd)
			
			cmd = raw_input(self.prompt)
			
			arg, opts = self.parse_cmd(cmd)
			self.cp = CommandParser(self.conn, arg, opts, self.EndofLoop, self.data)
			self.EndofLoop = self.cp.endloop
		
	# 
	# Sub Methods
	# --------------------------	
	def parse_cmd(self, cmd):
		base = cmd.split(" ")
		arg = base[0]
		opts = base[1:]
		return arg, opts
			
	def check_access(self, file):
		acs = True if os.access(file, os.F_OK) else False
		if acs == False:
			print "%s is not exist." % file
			return False
		else: return file
		
class Upload:
	def __init__(self, conn, file, filepath=None):
		if filepath:
			self.path = filepath
		else: self.path = "./"
		
		file = self.check_access(file)
		if file == False:
			sys.exit(1)
		
		fp = open(file, "r")
		conn.storbinary("STOR %s" % file, fp)
		print "Uploaded : [%s]" % file
		
	#
	# Sub Methods
	# --------------------------
	def check_access(self, file):
		acs = True if os.access(file, os.F_OK) else False
		if acs == False:
			print "%s is not exist." % file
			return False
		else: return file
		
		
		
class CommandParser:
	def __init__(self, conn, arg, opts, eol, data):
		self.conn = conn
		self.arg = arg
		self.opts = opts
		self.endloop = eol
		self.data = data
		self.commands = {
			"cd":self.Cd,         "pwd":self.Pwd,        "ls":self.List, "ll":self.ListAll,
			"local":self.Local,   "upload":self.Upload,  "download":self.Download,
			"rm":self.Rm,         "mkdir":self.Mkdir,    "rmdir":self.Rmdir,
			"rename":self.Rename, "find":self.Find,      "read":self.Read, 
			"status":self.Status, "showip":self.Showip, "showuser":self.Showuser,
			"access":self.Access, "exit":self.Bye, "quit":self.Bye, "help":self.Help,
			"history":self.History
		}
		if self.arg in self.commands.keys():
			self.endloop = self.commands[self.arg](self.opts)
		
	def Cd(self, opts):
		""" [directory] Move current directory. """
		directory = self.check_opts(opts, 0)
		try:
			self.conn.cwd(directory)
			
		except: print "%s is not directory." % directory
		
		return False
	
	def Pwd(self, opts):
		""" Show now current directory."""
		print self.conn.pwd()
		return False
		
	def List(self, opts):
		""" [*directory] show files in now directory. """
		try:
			directory = opts[0]
		except: 
			print ',  '.join(self.conn.nlst()[2:])
			return False
		
		try:
			self.conn.cwd(directory)
			print ',  '.join(self.conn.nlst())
		
		except: print "%s is not directory." % directory
		
		return False
	
	def ListAll(self, opts):
		""" [*directory] show files in now directory with status."""
		try:
			directory = opts[0]
		except: 
			self.conn.dir()
			return False
		
		try:
			conn.dir(directory)
		
		except: print "%s is not directory." % directory
		
		return False
		
	def Local(self, opts):
		""" [command] Run Local terminal command. """
		localcmd = self.check_opts(opts, 0)
		try:
			os.system(localcmd)
		except: 
			return False
			
		return False
		
	def Upload(self, opts):
		""" [file] Upload local file."""
		file = self.check_opts(opts, 0)
		if file == False: return False
		
		file = self.check_access(file)
		fp = open(file, "r")
		self.conn.storbinary("STOR %s" % file, fp)
		print "Uploaded : [%s]" % file
		return False
	
	def Download(self, opts):
		""" [file] Download remote file. """
		file = self.check_opts(opts, 0)
		if file == False: return False
		
		fp = open(file, "w").write
		try:
			self.conn.retrbinary("RETR %s" % file, fp)
			
		except:
			print "%s is not exist." % file
			return False
		
		print "Downloaded : [%s]" % file
		return False
	
	def Rm(self, opts):
		""" [file] Remove remote file."""
		file = self.check_opts(opts, 0)
		if file == False: return False
		
		try:
			self.conn.delete(file)
		
		except:
			print "%s is not exists." % file
			return False
			
		return False
		
	def Mkdir(self, opts):
		""" [directory] Make Directory."""
		dname = self.check_opts(opts, 0)
		if dname == False: return False
		
		try: self.conn.mkd(dname)
		except:
			print "%s is already exist." % dname
			return False
			
		return False
		
	def Rmdir(self, opts):
		""" [directory] Remove empty directory."""
		directory = self.check_opts(opts, 0)
		if directory == False: return False
		
		try: self.conn.rmd(directory)
		except:
			print "this comamnd remove only empty directory."
			return False
			
		return False
		
	def Rename(self, opts):
		""" [from_filename] [to_filename] Renemae filename."""
		fromname = self.check_opts(opts, 0)
		toname = self.check_opts(opts, 1)
		if fromname == False or toname == False: return False
		
		try:
			self.conn.rename(fromname, toname)
		
		except:
			print "%s is not exist." % fromname
			return False
		
		return False
		
	def Find(self, opts):
		""" [file] Find file."""
		file = self.check_opts(opts, 0)
		if file == False: return False
		
		files = self.conn.nlst()
		findout = []
		for item in files:
			try:
				indexs = item.index(file)
				findout.append(item)
			except: pass
		
		if len(findout) == 0:
			print "%s is not found." % file
		else: print ', '.join(findout)
		
		return False
	
	def Read(self, opts):
		""" [file] Read remote file."""
		file = self.check_opts(opts, 0)
		if file == False: return False
		
		try:
			self.conn.retrlines("RETR %s" % file)
		
		except:
			print "%s is not exist." % file
			return False
			
		return False
	
	def Status(self, opts):
		""" Show status."""
		print "Connect Status:"
		print "host = %s \nuser = %s \npasswd = %s \n" % (
			self.data[0], self.data[1], "*"*len(self.data[2])
		)
		print "Server Status:"
		status = self.conn.voidcmd("STAT")
		if "\n" in status:
			for line in status.split("\n"):
				print line
		else:
			for line in status.split(" "):
				print line
		
		return False
	
	def Showip(self, opts):
		""" Show remote ip."""
		print "Server ip address = %s" % gethostbyname(self.data[0])
		return False
		
	def Showuser(self, opts):
		""" Show user name."""
		print "You logined [%s]" % self.data[1]
		return False
				
	def Access(self, opts):
		""" [file] Show status of a file."""
		string = self.check_opts(opts, 0)
		if string == False: return False
		
		findout = []
		from redirect import Redirect
		r = Redirect()
		self.conn.dir()
		lines = r.getitems()
		for line in lines:
			try:
				indexs = line.index(string)
				findout.append(line)
			except: pass
			
		if len(findout) == 0:
			print "%s is not found." % string
		else:
			for line in findout:
				print line
				
		return False
		
	def Bye(self, opts):
		""" Exit."""
		return True
		
	def Help(self, opts):
		""" Show help."""
		command = self.check_opts(opts, 0)
		if command == False:
			for cmd in sorted (self.commands):
				print "* "+cmd.ljust(8) + self.commands[cmd].__doc__
		else:
			if command not in self.commands:
				print "%s is not command." % command
			else:
				print "* "+command.ljust(8) + self.commands[command].__doc__
				
		return False
		
	def History(self, opts):
		""" Show History tail. if you write'-a', show all."""
		history_length = readline.get_current_history_length()
		for n in range(1,history_length):
			print n, readline.get_history_item(n)
		return False
			
	#
	# Sub Methods
	# --------------------------
	def check_opts(self, opts, n):
		try:
			opt = opts[n]
		except IndexError:
			print "too little argument!"
			return False
			
		return opt
	
	def check_access(self, file):
		acs = True if os.access(file, os.F_OK) else False
		if acs == False:
			print "%s is not exist." % file
			return False
		else: return file
		
	def get_files(self, directory):
		files = self.conn.nlst()
		item = ([], []) # <= (files), (dirs)
		for file in files:
			try:
				self.conn.cwd(file)
				item[1].append(file)
			except:
				item[0].append(file)
		
		return item
			
