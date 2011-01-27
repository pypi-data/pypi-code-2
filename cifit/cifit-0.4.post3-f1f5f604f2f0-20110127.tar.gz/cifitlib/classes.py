#!/usr/bin/env python
# encoding: utf-8
"""
classes.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2010 Craig Sawyer. All rights reserved.

Storage stolen from web.py see LICENSE for details.
http://www.web.py
"""
import re
import os
import time
import socket
import sys
from files import run

class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    instead of `obj['foo']`. Create one by doing `storage({'a':1})`.
    """
    def __getattr__(self, key):
        if self.has_key(key):
            return self[key]
        raise AttributeError, repr(key)
    def __setattr__(self, key, value):
        self[key] = value
    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'

classes = Storage()


dow = {
    0:'Monday',
    1:'Tuesday',
    2:'Wednesday',
    3:'Thursday',
    4:'Friday',
    5:'Saturday',
    6:'Sunday'
}



def roundDown(num,rounder=5):
	"""this does the rounding for the min_ classes
	rounder should be set to whatever your crontab is set to probably.
	"""
	return (num // rounder) * rounder

#Default to 'Unknown'
classes.DISTRIB_ID = 'Unknown'

#do lsb stuff if possible.
if os.path.exists('/etc/lsb-release'):
    for line in open('/etc/lsb-release','r'):
        key, value = line.split('=')
        classes[key] = value.strip()
if os.path.exists('/etc/debian_version'):
	for line in open('/etc/debian_version','r'):
		classes['DISTRIB_ID'] = 'Debian'
		classes['DISTRIB_RELEASE'] = line.strip()

if os.path.exists('/etc/redhat-release'):
	line = open('/etc/redhat-release').readline()
	match = re.match(r'(\S*) release (\S*) \((\S*)\)', line)
	classes['DISTRIB_ID'] = match.group(1)
	classes['DISTRIB_RELEASE'] = match.group(2).split('.')

abspath = os.path.abspath(sys.argv[0])

classes.cifitlocation = os.path.dirname(abspath)
classes.hostname = socket.gethostname()
classes.hour = time.localtime()[3]
classes.dow = dow[time.localtime()[6]]
classes.minutes = roundDown(time.localtime()[4])
hour = time.localtime()[3]
classes.platform = sys.platform
#this is platform agnostic, but it might return 127.0.0.1 on unix hosts
#TODO: data is(based on /etc/hosts) -- possibly add code from netifaces package?
classes.mainip = socket.gethostbyname(socket.gethostname())
if classes.platform in ('Linux','Darwin'):
	classes.kernelver = run('uname -r')[1][0]


	#newyear and newmonth, 

if __name__ == '__main__':
	for k,v in classes.items():
		print "%s: %s" % (k,v)
