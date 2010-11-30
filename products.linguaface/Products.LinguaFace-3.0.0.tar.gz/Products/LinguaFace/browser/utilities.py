# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.
""" View used for content importation in XMLRPC
"""


from zope.interface import implements

from Products.Five import BrowserView
from interfaces import ILinguaFaceUtilities

class LinguaFaceUtilities(BrowserView) :
    """LinguaFace Utilities view"""
    implements(ILinguaFaceUtilities)

