#!/usr/bin/env python
'''
sweety.log

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 

Environment variables:
SWEETY_VERBOSE - turn on verbose mode.
SWEETY_LOG_FILENAME - specify the log file.
'''

from datetime import datetime
import logging
import os
import sys

from sweety import logstatus, util

_start_time = datetime.now()

_logfile_formatter = logging.Formatter(
									'%(asctime)s - %(name)s | %(levelname)s: [%(filename)s:%(lineno)d] - %(message)s'
									)
_console_formatter = logging.Formatter(
									'%(asctime)s - %(message)s | %(levelname)s: [%(filename)s:%(lineno)d]'
									)

def get_logger(name_or_self):
	'''
	get_logger(name_or_self) -> Logger
	
	Gets logger with specified name.
	
	@param name: the logger name or self.
	@return: the logger object.
	'''

	lockname = 'sweety.log.%s.lock' % _start_time.strftime('%Y-%m-%d')
	lock = util.FileLock(lockname)
	lock.lock()

	if not isinstance(name_or_self, (str, unicode)):
		name_or_self = name_or_self.__class__.__name__

	log = logging.getLogger(name_or_self)
	log.setLevel(logging.DEBUG)

	if not log.handlers:
		buf = logging.StreamHandler(logstatus._content)
		buf.setFormatter(_logfile_formatter)
		log.addHandler(buf)
		buf.setLevel(logging.INFO)

		console = logging.StreamHandler(sys.stderr)
		console.setFormatter(_console_formatter)
		log.addHandler(console)

		if os.environ.has_key('SWEETY_VERBOSE') and os.environ['SWEETY_VERBOSE']:
			console.setLevel(logging.INFO)
		else:
			console.setLevel(logging.WARNING)


		if os.environ.has_key('SWEETY_LOG_FILENAME'):
			fn = os.environ['SWEETY_LOG_FILENAME']
			fdir = os.path.dirname(fn)
			fdir = os.path.join(fdir, _start_time.strftime('%Y-%m-%d'))
			if not os.path.exists(fdir):
				os.makedirs(fdir)
			fn = '%s/%s.%s.%d' % (
					fdir,
					os.path.basename(fn),
					_start_time.strftime('%Y-%m-%d_%H:%M:%S'),
					os.getpid()
					)
			logfile = logging.FileHandler(fn)
			logfile.setFormatter(_logfile_formatter)
			log.addHandler(logfile)
			logfile.setLevel(logging.DEBUG)

	return log

logging.root = get_logger('root')
