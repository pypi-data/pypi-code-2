#!/usr/bin/python
#coding:utf-8

import ftplib
import os
import sys

__name__ = "FTPTerm"
commands = {"cd <file>": "move current directory.",
"pwd": "print now directory.",
"ls" : "list directory.",
"upload <file>": "upload file.",
"del <file>": "delete file.",
"mkdir <dir>": "make directory.",
"rmdir <dir>": "delete directory.",
"rename <fromname> <toname>": "rename file name."}

class BasicFTPError(Exception): pass
class FTPConnectionError(BasicFTPError): pass
class FTPLoginError(BasicFTPError): pass
class NonArgumentError(BasicFTPError): pass
class NonConfigError(BasicFTPError): pass
class ConfigFileError(BasicFTPError): pass

try: mode = sys.argv[1]
except: mode = "nomal"
		
def term():
	while True:
		cmd = raw_input("%s:%s > " % (user,conn.pwd().split("/")[-1]))
		
		if cmd == "ls":
			conn.dir()
			continue
			
		elif cmd.split(" ")[0] == "upload":
			try: file = cmd.split(" ")[1]
			except: print "arguments is not found.";continue;
			
			if os.access(file, os.F_OK): f = open(file,"r")
			else: print "'%s' is not found." % file;continue;
		
			conn.storbinary("STOR %s" % file,f)
		
		elif cmd.split(" ")[0] == "download":
			try: file = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			f = open(file,"w")
			conn.retrbinary("RETR %s"%file,f.write)
			print "Completed."
		
		elif cmd.split(" ")[0] == "cd":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			try: conn.cwd(dir)
			except: print "'%s' is not directory." % dir
			
		elif cmd.split(" ")[0] == "del":
			try: file = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			conn.delete(file)
		
		elif cmd.split(" ")[0] == "mkdir":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			conn.mkd(dir)
			
		elif cmd.split(" ")[0] == "rmdir":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
		
			conn.rmd(dir)
	
		elif cmd == "pwd":
			print conn.pwd()
		
		elif cmd.split(" ")[0] == "rename":
			try: fromname = cmd.split(" ")[1];toname = cmd.split(" ")[2]
			except: print "argument is not found.";continue;
		
			conn.rename(fromname,toname)
		
		elif cmd == "help":
			for key,value in commands.iteritems():
				print "*",key.ljust(27),":",value.rjust(9)
			
		elif cmd == "exit":
			conn.close()
			break;
	
if mode == "nomal":
	print " Welcome to ftpterm. ".center(50,"+")
	print " Please input host name. ".center(50,"+")
	host = raw_input("host > ")
	print " Please input user name and password. ".center(50,"+")
	user = raw_input("user > ")
	passwd = raw_input("password > ")
	print "Connectting..."
	
	try: conn = ftplib.FTP(host)
	except: raise FTPConnectionError("'%s' host nor servname provided, or not known" % host)
	
	print "Connected."

	try: conn.login(user=user,passwd=passwd)
	except: raise FTPLoginError("this program can't login. Please again!")
	
	print "Logined : %s " % (user)
	print conn.getwelcome()
	
	term()
		
elif mode == "useconf":
	try: conffile = sys.argv[2]
	except: raise NonArgumentError("file argument is not here.")
	
	if os.access(conffile,os.F_OK) != True:
		raise NonConfigError("'%s' file is not here." % conffile)
	
	# read conf file
	body = open(conffile,"r").read()
	configs = body.split("\n")[:-1]
	if len(configs) != 3: raise ConfigFileError("'%s' config file is error." % conffile)
	host = configs[0]
	user = configs[1]
	passwd = configs[2]
	print "Connectting..."
	
	try: conn = ftplib.FTP(host)
	except: raise FTPConnectionError("'%s' host nor servname provided, or not known" % host)
	
	print "Connected."

	try: conn.login(user=user,passwd=passwd)
	except: raise FTPLoginError("this program can't login. Please again!")
	
	print "Logined : %s " % (user)
	print conn.getwelcome()
	
	term()
	
else:
	print "Usage: % python ftpterm.py <mode>\n"
	print "mode:"
	print "01 : nomal -- nomal mode. please input host, user and passwd."
	print "02 : useconf -- use config file."
	print "** if you not input mode, this module call nomal mode.\n"
	print "config file:"
	print "<hostname>"
	print "<username>"
	print "<password>"
	print "Please input host, user and pass to file."
		