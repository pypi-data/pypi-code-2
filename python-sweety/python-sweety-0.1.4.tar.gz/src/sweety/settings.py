#!/usr/bin/env python
'''
sweety.settings

Defines the setting module.

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''


#META_DIRNAME = '.meta'
#META_LOCKFILE = 'lock'
#META_FILENAME = 'meta'

import os
import sys

from sweety import loader

_vars = locals()

if os.environ.has_key('SWEETY_SETTING_MODULE'):
	_setting = loader.load_file(os.environ['SWEETY_SETTING_MODULE'])

	for _key in dir(_setting):
		_vars[_key] = getattr(_setting, _key)

for _key in _vars.keys():
    _val = _vars[_key]
    if isinstance(_val, (str, unicode)):
        _val = os.path.expanduser(_val)
        _val = os.path.expandvars(_val)
        _vars[_key] = _val

del _vars
