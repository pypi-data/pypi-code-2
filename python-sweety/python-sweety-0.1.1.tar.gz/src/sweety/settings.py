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

def get_conf_dir():
    confdir = os.path.realpath(
                            os.path.join(
                                        os.path.dirname(get_conf_dir.func_code.co_filename),
                                        '../../../conf'
                                        )
                            )

    return confdir

confdir = get_conf_dir()

sys.path.insert(0, os.path.dirname(confdir))

from conf.settings import *

del sys.path[0]

_vars = locals()
for _key in _vars.keys():
    _val = _vars[_key]
    if isinstance(_val, (str, unicode)):
        _val = os.path.expanduser(_val)
        _val = os.path.expandvars(_val)
        _vars[_key] = _val


