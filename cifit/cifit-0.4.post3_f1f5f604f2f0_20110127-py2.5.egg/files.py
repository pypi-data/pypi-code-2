#!/usr/bin/env python
# encoding: utf-8
"""
Mess about with files.

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.

class readonlypipe, executor and run happily stolen from BCFG2
http://trac.mcs.anl.gov/projects/bcfg2/
Copyright 2004 University of Chicago
see their copyright here: http://trac.mcs.anl.gov/projects/bcfg2/browser/trunk/bcfg2/COPYRIGHT
See LICENSE for details.

"""

import re
import os
import sys
import stat
import pwd,grp
import tempfile
import popen2
import time
import logging
import filecmp
import shutil

log = logging.getLogger('files')

def getFilename(filename):
	"""return absolute path and expanded ~ vars for you."""
	return os.path.abspath(os.path.expanduser(filename))

class readonlypipe(popen2.Popen4):
	"""This pipe sets up stdin --> /dev/null"""
	def __init__(self, cmd, bufsize=-1):
		popen2._cleanup()
		c2pread, c2pwrite = os.pipe()
		null = open('/dev/null', 'w+')
		self.pid = os.fork()
		if self.pid == 0:
			# Child
			os.dup2(null.fileno(), sys.__stdin__.fileno())
			#os.dup2(p2cread, 0)
			os.dup2(c2pwrite, 1)
			os.dup2(c2pwrite, 2)
			self._run_child(cmd)
		os.close(c2pwrite)
		self.fromchild = os.fdopen(c2pread, 'r', bufsize)
		popen2._active.append(self)

class executor(object):
	"""this class runs stuff for us"""
	def __init__(self, logger):
		"""initialization, needs a logger object"""
		self.log = logger

	def run(self, command):
		"""Run a command in a pipe dealing with stdout buffer overloads"""
		self.log.debug('> %s' % command)
		runpipe = readonlypipe(command, bufsize=16384)
		output = []
		try:#macosx doesn't like this
			runpipe.fromchild.flush()
		except IOError:
			pass
		line = runpipe.fromchild.readline()
		cmdstat = -1
		while cmdstat == -1:
			while line:
				if len(line) > 0:
					self.log.debug('< %s' % line[:-1])
					output.append(line[:-1])
				line = runpipe.fromchild.readline()
			time.sleep(0.1)
			cmdstat = runpipe.poll()
		output += [line[:-1] for line in runpipe.fromchild.readlines() \
				  if line]
		return (cmdstat, output)


def run(cmd):
	runner = executor(log)
	return runner.run(cmd)

def copy(src,dst,mode=None):
	"""copy only if files are changed
	returns True only if actually copied something.
	"""
	copied = False
	src = getFilename(src)
	dst = getFilename(dst)
	if not os.path.exists(dst):
		#destination doesn't exist, just copy
		shutil.copy(src,dst)
		copied = True
	if not filecmp.cmp(src,dst):
		log.debug('file %s has changed, copying replacement' % (dst))
		shutil.copy(src,dst)
		copied = True
	if mode:
		setPermissions(dst,mode=mode)
	return copied

def append(filename,lines,out='REPLACE',linesep=True):
	"""append is way to append lines in files if the line is not already in the
	file (exact match only) filename is a ''
	lines is a [] of strings to append to the end of the file.
	out is a fileobject.

	if linsep, then we add the lineseperator to the end of the line for
	comparison and writing.
	we DO NOT handle whitespace differences.
	(some config files might care about whitespace.)
	return True only if we actually updated something.
	"""
	updated = False
	if linesep:
		for line in lines:
			lines[lines.index(line)] = line+os.linesep
	filename = getFilename(filename)
	replace=False
	if out == 'REPLACE':
		if not os.path.exists(filename):
			run('touch %s' % filename)
		origperms={'owner':getOwner(filename),'group':getGroup(filename),'mode':getOctPerms(filename)}
		out,outfile = tempfile.mkstemp()
		out=os.fdopen(out,'w+')
		replace=True
	else:
		outfile = getFilename(out)
	log.debug('input:%s,output:%s' % (filename,outfile))
	if not os.path.lexists(filename):
		f = open(filename,'w+')
	else:
		f = open(filename,'r')
	for line in f:
		#if it is in our lines output already take it out of our list.
		if line in lines:
			lines.pop(lines.index(line))
		out.write(line)
	#we've done the compare, now do the append if there is anything...
	for line in lines:
		out.write(line)
		updated = True
	#file done
	if replace:
		infile = f.name
		f.close()
		out.close()
		os.rename(infile,infile+'.bak')
		os.rename(outfile,infile)
		setPermissions(infile,owner=origperms['owner'],group=origperms['group'],mode=origperms['mode'])
	return updated


def sub(filename,subs,out='REPLACE'):
	"""sub is a sed-like subsitution for lines in files.
	filename is a path (relative is fine).
	subs is a list of regex subs to perform.
	each sub is a sed substitution i.e.:
	 /PATTERN/REPLACEMENT/OPTS
	 where / can be any single character.
	 PATTERN is a python regular expression
	 replacement is the string to replace pattern with.
	 OPTS is currentlly undefined. (but should grow to accept g (global replace))
	out is a file object to write to.
	"""
	replace=False
	if out == 'REPLACE':
		origperms={'owner':getOwner(filename),'group':getGroup(filename),'mode':getOctPerms(filename)}
		out,outfile = tempfile.mkstemp()
		out=os.fdopen(out,'w+')
		#print 'outfile:',outfile
		replace=True
	#this stores the regexes to be used..
	res=[]
	for sub in subs:
		#print "sub:",sub
		char,regex,rpl,opts = sub.split(sub[0],3)
		regex = re.compile(regex)
		res.append([regex,rpl,opts])
	filename = getFilename(filename)
	f = open(filename,'r')
	for line in f:
		for r in res:
			line = re.sub(r[0],r[1],line)
		out.write(line)
	#file done
	if replace:
		infile = f.name
		f.close()
		out.close()
		os.rename(infile,infile+'.bak')
		os.rename(outfile,infile)
		setPermissions(infile,owner=origperms['owner'],group=origperms['group'],mode=origperms['mode'])

def normUID(owner):
	"""
	   This takes a user name or uid and
	   returns the corresponding uid or False
	"""
	try:
		try:
			return int(owner)
		except:
			return int(pwd.getpwnam(owner)[2])
	except (OSError, KeyError):
		log.error('UID normalization failed for %s' % (owner))
		return False

def normGID(group):
	"""
	   This takes a group name or gid and
	   returns the corresponding gid or False
	"""
	try:
		try:
			return int(group)
		except:
			return int(grp.getgrnam(group)[2])
	except (OSError, KeyError):
		log.error('GID normalization failed for %s' % (group))
		return False


def calcPerms(perms):
	"""This compares ondisk permissions with specified ones
	initial is stat.S_IFDIR
	perms is string of octal mode i.e. 644 for -rw-r--r--
	"""
	pdisp = [{1:stat.S_ISVTX, 2:stat.S_ISGID, 4:stat.S_ISUID},
			 {1:stat.S_IXUSR, 2:stat.S_IWUSR, 4:stat.S_IRUSR},
			 {1:stat.S_IXGRP, 2:stat.S_IWGRP, 4:stat.S_IRGRP},
			 {1:stat.S_IXOTH, 2:stat.S_IWOTH, 4:stat.S_IROTH}]
	tempperms = stat.S_IFDIR
	if len(perms) == 3:
		perms = '0%s' % (perms)
	pdigits = [int(perms[digit]) for digit in range(4)]
	for index in range(4):
		for (num, perm) in list(pdisp[index].items()):
			if pdigits[index] & num:
				tempperms |= perm
	return tempperms

def getOctPerms(filename):
	"""return octal string of current perms.
	"""
	filename = getFilename(filename)
	perms = os.stat(filename).st_mode
	pmap = [
		{stat.S_IRUSR:04,stat.S_IWUSR:02,stat.S_IXUSR:01},
		{stat.S_IRGRP:04,stat.S_IWGRP:02,stat.S_IXGRP:01},
		{stat.S_IROTH:04,stat.S_IWOTH:02,stat.S_IXOTH:01},
	]
	pdigits = [0,0,0]
	for index in range(3):
		for k,v in pmap[index].items():
			if perms & k:
				pdigits[index] += v
	return ''.join([str(i) for i in pdigits])

def getStringPerms(filename):
	filename = getFilename(filename)
	mode = os.stat(filename).st_mode
	perms="-"
	for who in "USR", "GRP", "OTH":
		for what in "R", "W", "X":
			if mode & getattr(stat,"S_I"+what+who):
				perms=perms+what.lower()
			else:
				perms=perms+"-"
	return perms

def getOwner(filename):
	filename = getFilename(filename)
	return os.stat(filename).st_uid

def getGroup(filename):
	filename = getFilename(filename)
	return os.stat(filename).st_gid

def setPermissions(filename,owner=None,group=None,mode=None):
	"""Verify and correct permissions."""
	filename = getFilename(filename)
	if not os.path.lexists(filename):
		log.error("file does not exist:%s" % (filename))
	if not group:
		group = getGroup(filename)
	if not owner:
		owner = getOwner(filename)
	if not mode:
		mode = getOctPerms(filename)
	try:
		os.chown(filename,normUID(owner),normGID(group))
		os.chmod(filename,calcPerms(mode))
		return True
	except (OSError,KeyError):
		log.error('permission fixup failed for %s' % (filename))
		return False

if __name__ == '__main__':
	args = sys.argv[1:]
	subs = []
	files = []
	for i in range(len(args)):
		arg = args[i]
		if arg == '-s':
			subs.append(args[i+1])
			continue
		else:
			if arg not in subs:
				files.append(arg)
	#print "subs:",subs
	#print "files:",files
	sub(files,subs,out='REPLACE')

