#!/usr/bin/python
#coding:utf-8

import ftplib
import os

__name__ = "FTPTerm"

class BasicFTPError(Exception): pass
class FTPConnectionError(BasicFTPError): pass
class FTPLoginError(BasicFTPError): pass

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
		
	elif cmd == "exit":
		conn.close()
		break;
		
		
		