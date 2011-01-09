#!/usr/bin/env python
'''
sweety.logstatus

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import cStringIO

_content = cStringIO.StringIO()

def get_log_content():
	_content.seek(0, 0)
	return _content.read()

