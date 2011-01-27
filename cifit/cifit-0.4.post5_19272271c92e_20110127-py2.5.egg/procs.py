#!/usr/bin/env python
# encoding: utf-8
"""
procs.py

This code handles processes.

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""

import re
from files import run
from classes import Storage, classes
import logging

log = logging.getLogger('%s:procs' % classes['hostname'])


def getServiceCommand(name,cmd):
	if classes.platform != 'darwin':
		return '/etc/init.d/%s %s' % (name,cmd)
	else:
		#use launchctl and files from /System/Library/LaunchDaemons 
		log.error('NOT IMPLEMENTED')
def stopService(svcname):
	return run(getServiceCommand(svcname,'stop'))
def startService(svcname):
	return run(getServiceCommand(svcname,'start'))
def restartService(svcname):
	stopService(svcname)
	startService(svcname)
def checkService(svcname):
	ret,out = run(getServiceCommand(svcname,'status'))
	rec = re.compile('runnning',re.IGNORECASE)
	for line in out:
		if re.search(rec,line):
			return True
	else:
		#if we can't find it by system service, just try by isRunning.
		return isRunning(svcname)

def stopProcess(pattern,mode=15):
	"""given a name, stop a process."""
	pid = isRunning(pattern)
	if pid:
		run('kill -%s %s' % (mode,pid))
	else:
		log.warn('no process found to kill:%s' % pattern)

def startProcess(cmd):
	"""Startup a process."""
	if classes.platform == 'darwin':
		cmd = 'open %s' % cmd
		run(cmd)
	else:
		run(cmd)

class processes(Storage):
	def addproc(self,procinfo):
		"""Add process to self's Storage Object"""
		self[procinfo.PID] = procinfo
	def getByCommand(self,cmd):
		"""get processes that are contain cmd (as a regex) in their COMMAND key."""
		cmdre = re.compile(cmd,re.IGNORECASE)
		ret = {}
		for k,v in self.items():
			if re.search(cmdre,v.COMMAND):
				ret[k] = v
		return ret

procs = processes()

def getProcesses(refresh=False):
	"""return {} of processes running.
	key = PID, value = {} of procinfo below.
	"""
	if refresh == False and (len(procs.keys()) > 0):
		return procs
	ret , vals = run('ps auxww')
	if ret == 0:
		for i in vals:
			p = i.split()
			if p[0].strip() == 'USER':
				continue
			procinfo = Storage({
				'USER':p[0].strip(),
				'PID':int(p[1].strip()),
				'CPU':float(p[2].strip()),
				'MEM':float(p[3].strip()),
				'VSZ':p[4].strip(),
				'RSS':p[5].strip(),
				'TT':p[6].strip(),
				'STAT':p[7].strip(),
				'STARTED':p[8].strip(),
				'TIME':p[9].strip(),
				'COMMAND':' '.join(p[10:len(p)])
			})
			#send to procs dictionary.
			procs.addproc(procinfo)
		return procs
	else:
		log.error('getProcesses:fail',procs)
		return []

def isRunning(pattern):
	"""match and return the pid of said process
	We also match against PID numbers, since it's also used to make sure
	a process is currently running.
	"""
	rx = re.compile(str(pattern),re.IGNORECASE)
	for proc in getProcesses().values():
		if re.search(rx,proc.COMMAND):
			return proc.PID
		elif re.search(rx,str(proc.PID)):
			return proc.PID
	return False

getPID = isRunning

if __name__ == '__main__':
	print getProcesses()
	print 'this is a module, use import.'
	pass

