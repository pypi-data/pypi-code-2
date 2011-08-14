# -*- coding: utf-8 -*-
# $Id: validators.py 1542 2011-04-01 07:13:53Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import re

from zope.interface import implements

from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator

TIME_PERIOD_VALIDATOR_NAME = 'isTimePeriod'

class TimePeriodValidator:
    """
    Ensure that we don't get a value for start and/or end time of a time period
    which are not valid.
    """

    #__implements__ = IValidator
    implements(IValidator)
    
    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
    
    def __call__(self, value, *args, **kwargs):
        """
        """
        if value[0] or value[1]:

            for item in value:
                m = re.match('^\s*(\d\d)[.:]?(\d\d)\s*$', item)
    
                if not m:
                    return ("Validation failed: '%(value)s' is not a time specification." %
                            { 'value': item, })
        
        return True

# register time period validator 
isTimePeriod = TimePeriodValidator(TIME_PERIOD_VALIDATOR_NAME)
validation.register(isTimePeriod)
