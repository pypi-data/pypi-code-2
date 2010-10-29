# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""Common imports and declarations
common includes a set of basic things that every test needs.

$Id: common.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__ = ''
__docformat__ = 'restructuredtext'

# enable nice names for True and False from newer python versions
try:
    dummy = True
except NameError: # python 2.1
    True  = 1
    False = 0

import time

def Xprint(s):
    """print helper

    print data via print is not possible, you have to use
    ZopeTestCase._print or this function
    """
    ZopeTestCase._print(str(s)+'\n')

def dcEdit(obj):
    """dublin core edit (inplace)
    """
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    # XXX more

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

###
# general test suits including products
###
from Testing import ZopeTestCase
ZopeTestCase.installProduct('CMFCore', 1)
ZopeTestCase.installProduct('CMFDefault', 1)
ZopeTestCase.installProduct('CMFCalendar', 1)
ZopeTestCase.installProduct('CMFTopic', 1)
ZopeTestCase.installProduct('DCWorkflow', 1)
ZopeTestCase.installProduct('CMFActionIcons', 1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', 1)
ZopeTestCase.installProduct('CMFFormController', 1)
ZopeTestCase.installProduct('GroupUserFolder', 1)
ZopeTestCase.installProduct('ZCTextIndex', 1)
ZopeTestCase.installProduct('CMFPlone', 1)
ZopeTestCase.installProduct('MailHost', 1)
ZopeTestCase.installProduct('PageTemplates', 1)
ZopeTestCase.installProduct('PythonScripts', 1)
ZopeTestCase.installProduct('ExternalMethod', 1)
ZopeTestCase.installProduct('ZCatalog', 1)
ZopeTestCase.installProduct('Archetypes', 1)
ZopeTestCase.installProduct('PortalTransforms', 1)
ZopeTestCase.installProduct('ATContentTypes', 1)
ZopeTestCase.installProduct('AttachmentField', 1)
ZopeTestCase.installProduct('PloneExFile', 1)
ZopeTestCase.installProduct('PloneArticle', 1)
ZopeTestCase.installProduct('PloneFilesZip', 1)

###
# from archetypes
###

from Products.Archetypes.public import *
from Products.Archetypes.config import PKG_NAME
from Products.Archetypes.tests import ArchetypesTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.Storage import AttributeStorage, MetadataStorage
from Products.Archetypes import listTypes
from Products.Archetypes.Widget import IdWidget, StringWidget, BooleanWidget, \
     KeywordWidget, TextAreaWidget, CalendarWidget, SelectionWidget
from Products.Archetypes.utils import DisplayList
from Products.CMFCore  import CMFCorePermissions
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE,CEILING_DATE

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_inner, aq_parent


###
# AT Content Types
###

try:
    from Products.ATContentTypes.types import ATDocument
except:
    from Products.ATContentTypes.content import document

# import Interface for interface testing
try:
    import Interface
except ImportError:
    # set dummy functions and exceptions for older zope versions
    def verifyClass(iface, candidate, tentative=0):
        return True
    def verifyObject(iface, candidate, tentative=0):
        return True
    def getImplementsOfInstances(object):
        return ()
    def getImplements(object):
        return ()
    def flattenInterfaces(interfaces, remove_duplicates=1):
        return ()
    class BrokenImplementation(Exception): pass
    class DoesNotImplement(Exception): pass
    class BrokenMethodImplementation(Exception): pass
else:
    from Interface.Implements import getImplementsOfInstances, \
         getImplements, flattenInterfaces
    from Interface.Verify import verifyClass, verifyObject
    from Interface.Exceptions import BrokenImplementation, DoesNotImplement
    from Interface.Exceptions import BrokenMethodImplementation

###
# PloneExFile tests
###

from PloneFilesZipTestCase import PloneFilesZipTestCase
from PloneFilesZipTestCase import DATA_PATH

