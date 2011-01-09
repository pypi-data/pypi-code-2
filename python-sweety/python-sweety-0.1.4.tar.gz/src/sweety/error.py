#!/usr/bin/env python
'''
sweety.error

Defines the error classes.

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import exceptions

class SweetyError(exceptions.RuntimeError):
    pass

class SweetyOptionRequiredError(SweetyError):
    pass
