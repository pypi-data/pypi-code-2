# -*- coding: utf-8 -*-

from Products.validation import validation

from collective.itvalidators.validators.base_validators import baseValidators
from collective.itvalidators.validators.MinCharsValidator import MinCharsValidator


for v in baseValidators:
    validation.register(v)

#validation.register(MinCharsValidator)