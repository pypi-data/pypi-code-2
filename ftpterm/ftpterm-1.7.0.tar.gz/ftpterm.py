#!/usr/bin/python
#coding:utf-8

import ftplib
import os
import sys
from socket import gethostbyname

__name__ = "FTPTerm"
commands = {1:{"cd <file>": "move current directory."},
2:{"pwd": "print now directory."},
3:{"ls" : "list directory."},
4:{"local <cmd>": "operate local files."},
5:{"upload <file>": "upload file."},
6:{"download <file>": "download file"},
7:{"rm<file>": "delete file."},
8:{"mkdir <dir>": "make directory."},
9:{"rmdir <dir>": "delete directory. (empty dir only.)"},
10:{"rm -r <dir>": "delete directory.(not only empty dir.)"},
11:{"rename <fromname> <toname>": "rename file name."},
12:{"find <filename>": "find filename."},
13:{"read <file>": "read file. like cat command."},
14:{"status": "show connect status."},
15:{"showip": "show ip address of user."},
16:{"showuser": "show user name."},
17:{"access <file>": "show access authority of file."}}

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
		unver = conn.sendcmd("NOOP")
		cmd = raw_input("%s:%s > " % (user,conn.pwd().split("/")[-1]))
		
		if cmd == "ls":
			conn.dir()
			continue
		
		elif cmd == "status":
			status = conn.voidcmd("STAT")
			for i in status.split(" "):
				print i.strip()
			
		elif cmd == "showuser":
			print "Your User is : %s "% user
			
		elif cmd == "showip":
			print "Server IP Address is : %s" % gethostbyname(host)
			
		elif cmd.split(" ")[0] == "local":
			arg = cmd.split(" ")[1:]
			if len(arg) == 0: 
				print "local command operate local file. commands::"
				print "  ls -- show local dir"
				print "  pwd -- show now directory"
				print "  cd <dir> -- move dir"
				print "  vim <file> -- edit file with vim."
				print "  emacs <file> -- edit file with emacs."
				continue
			
			if arg[0] == "pwd":
				print os.getcwd()
			
			elif arg[0] == "cd":
				try: dir = arg[1]
				except: print "argument is not found";continue;
				
				try: os.chdir(dir)
				except: print "'%s' dir may not exist or not directory." % dir
				
			elif arg[0] == "ls":
				os.system("ls")
				
			elif arg[0] == "vim":
				try: file = arg[1]
				except: print "argument is not found";continue;
				
				os.system("vim %s" % file)
				
			elif arg[0] == "emacs":
				try: file = arg[1]
				except: print "argument is not found";continue;
				
				os.system("emacs %s" % file)
			
			else: 
				print "local command operate local file. commands::"
				print "  ls -- show local dir"
				print "  pwd -- show now directory"
				print "  cd <dir> -- move dir"
				print "  vim <file> -- edit file with vim."
				print "  emacs <file> -- edit file with emacs."
				continue
			
		elif cmd.split(" ")[0] == "find":
			try: file = cmd.split(" ")[1]
			except: print "arguments is not found.";continue;
			
			files = conn.nlst()
			findout = []
			for i in files:
				try: 
					indexes = i.index(file)
					findout.append(i)
				except: pass
			
			if len(findout) == 0:
				print "'%s' is Not Found."%file
			else:
				print ', '.join(findout)
		
		elif cmd.split(" ")[0] == "access":
			try: file = cmd.split(" ")[1]
			except: print "arguments is not found.";continue;
			
			sys.stdout = open("temp","w")
			conn.dir()
			sys.stdout = sys.__stdout__
			body = open("temp","r").read()
			lines = body.split("\n")[:-1]
			files = sorted(conn.nlst())
			try: indexs = files.index(file)
			except: print "Error! '%s' may not exist."%file;os.system("rm temp");continue;
			print lines[indexs]
			os.system("rm temp")

		elif cmd.split(" ")[0] == "upload":
			try: file = cmd.split(" ")[1]
			except: print "arguments is not found.";continue;
			
			if os.access(file, os.F_OK): f = open(file,"r")
			else: print "'%s' is not found." % file;continue;
		
			try: conn.storbinary("STOR %s" % file,f)
			except: print "Error! '%s' file may not exist." % file
		
		elif cmd.split(" ")[0] == "download":
			try: file = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			f = open(file,"w")
			try: conn.retrbinary("RETR %s"%file,f.write)
			except: print "Error! '%s' file may not exist." % file;continue;
			print "Completed."
			
		elif cmd.split(" ")[0] == "read":
			try: file = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			try: conn.retrlines("RETR %s" % file)
			except: print "Error! '%s' file may not exist." % file;continue;
		
		elif cmd.split(" ")[0] == "cd":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			try: conn.cwd(dir)
			except: print "'%s' is not directory." % dir
			
		elif cmd.split(" ")[0] == "rm":
			try: mode = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			if mode != "-r":
				files = mode
				try: conn.delete(files)
				except: print "Error! '%s' file may not exist or directory." % files;continue;
				
			else:
				try: dir = cmd.split(" ")[2]
				except: print "argument is not found.";continue;
				
				try: conn.cwd(dir)
				except: print "'%s' is not directory." % dir;continue;
				
				files = conn.nlst()
				if len(files) == 0:
					conn.cwd("../")
					conn.rmd(dir)
				else:
					for i in range(len(files)):
						try: conn.delete(files[i])
						except:
							conn.cwd(files[i])
							if len(conn.nlst()) == 0:
								conn.cwd("../")
								conn.rmd(files[i])
							else:
								for j in range(len(conn.nlst())):
									try: conn.delete(files[j])
									except:
										conn.cwd(files[j])
										if len(conn.nlst()) == 0:
											conn.cwd("../")
											conn.rmd(files[j])
										else:
											for k in range(len(conn.nlst())):
												try: conn.delete(files[j])
												except: print "Can't Delete."
								conn.cwd("../")
								conn.rmd(dir)
					conn.cwd("../")
					conn.rmd(dir)
					
		elif cmd.split(" ")[0] == "mkdir":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
			
			try: conn.mkd(dir)
			except: print "'%s' file exists." % dir
			
		elif cmd.split(" ")[0] == "rmdir":
			try: dir = cmd.split(" ")[1]
			except: print "argument is not found.";continue;
		
			try: conn.rmd(dir)
			except: print "Error! '%s' dir is not empty." % dir
			
		elif cmd == "pwd":
			print conn.pwd()
		
		elif cmd.split(" ")[0] == "rename":
			try: fromname = cmd.split(" ")[1];toname = cmd.split(" ")[2]
			except: print "argument is not found.";continue;
		
			try: conn.rename(fromname,toname)
			except: print "Error! '%s' file may not exist." % fromname
		
		elif cmd == "help":
			for i in sorted(commands.keys()):
				key = commands[i].keys()[0]
				value = commands[i].values()[0]
				print "*",key.ljust(27),":",value.rjust(9)
			
		elif cmd == "exit":
			conn.close()
			break;
			
		elif cmd == "clear":
			print '\x1b[H\x1b[2J'
		
		else: unver=conn.sendcmd("NOOP")
	
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
	
elif mode == "upload":
	try: file = sys.argv[2] 
	except: raise NonArgumentError("file argument is not here.")
	
	try:
		conffile = sys.argv[3]
		# read conf file
		body = open(conffile,"r").read()
		configs = body.split("\n")[:-1]
		if len(configs) != 3: raise ConfigFileError("'%s' config file is error." % conffile)
		host = configs[0]
		user = configs[1]
		passwd = configs[2]
	except:
		print "Please input host, user and passwd."
		host = raw_input("host > ")
		user = raw_input("user > ")
		passwd = raw_input("pass > ")
		
	print "Connectting..."
	
	try: conn = ftplib.FTP(host)
	except: raise FTPConnectionError("'%s' host nor servname provided, or not known" % host)
		
	print "Connected."
	
	try: conn.login(user=user,passwd=passwd)
	except: raise FTPLoginError("this program can't login. Please again!")
	
	try: path = sys.argv[4]
	except: path = ""
	
	try: conn.cwd(path)
	except: print "'%s' is not directory." % path; sys.exit(1)
				
	print "Uploading..."
	
	if os.access(file, os.F_OK): f = open(file,"r")
	else: print "'%s' is not found." % file;sys.exit(1)
	
	conn.storbinary("STOR %s" % file,f)
	print "Completed."
		
elif mode == "help":
	print "Usage: % python ftpterm.py <mode>\n"
	print "mode:"
	print "01 : nomal -- nomal mode. please input host, user and passwd."
	print "02 : useconf <config file>-- use config file."
	print "03 : upload <upload file> <*config file> <*path>-- upload file."
	print "** if you not input mode, this module call nomal mode.\n"
	print "config file:"
	print "<hostname>"
	print "<username>"
	print "<password>"
	print "Please input host, user and pass to file."

else:
	print "Usage: % python ftpterm.py <mode>\n"
	print "mode:"
	print "01 : nomal -- nomal mode. please input host, user and passwd."
	print "02 : useconf <config file>-- use config file."
	print "03 : upload <upload file> <*config file> <*path>-- upload file."
	print "** if you not input mode, this module call nomal mode.\n"
	print "config file:"
	print "<hostname>"
	print "<username>"
	print "<password>"
	print "Please input host, user and pass to file."
		