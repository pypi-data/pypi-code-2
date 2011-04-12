# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: validators.py 236779 2011-04-01 05:51:02Z nilo $

from Products.validation.interfaces.IValidator import IValidator
from config import COUNTRIES
import re
import zope.interface

class CountryValidator(object):
    """country validator, checks if given value is in list
    of valid iso country codes.
    """
    zope.interface.implements(IValidator)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        
        if value == '' or value in COUNTRIES.keys():
            return 1
        else:
            return """This is not a valid country ISO-Code."""


