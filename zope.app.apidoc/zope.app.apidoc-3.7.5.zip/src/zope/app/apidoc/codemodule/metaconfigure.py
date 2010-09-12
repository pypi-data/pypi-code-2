##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""This module handles the 'apidoc' namespace directives.

$Id: metaconfigure.py 113308 2010-06-10 01:09:36Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.interface import implements
from zope.component.zcml import utility

from zope.app.apidoc import classregistry
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule


class RootModule(str):
    implements(IAPIDocRootModule)

def rootModule(_context, module):
    """Register a new module as a root module for the class browser."""
    utility(_context, IAPIDocRootModule, RootModule(module), name=module)


def setModuleImport(flag):
    classregistry.__import_unknown_modules__ = flag

def moduleImport(_context, allow):
    """Set the __import_unknown_modules__ flag"""
    return _context.action(
        ('apidoc', '__import_unknown_modules__'),
        setModuleImport,
        (allow, ))
