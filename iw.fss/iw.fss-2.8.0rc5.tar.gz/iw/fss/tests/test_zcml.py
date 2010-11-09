## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: test_zcml.py 65108 2008-05-19 20:23:31Z cbosse $
"""
Testing the ZCML meta and associated modules
"""
__author__  = ''
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing.doctest import ELLIPSIS

def test_typewithfss():
    """
    Test fss:typeWithFSS directive::

        >>> from Products.Five import zcml
        >>> import iw.fss
        >>> template = '''
        ... <configure
        ...   xmlns="http://namespaces.zope.org/zope"
        ...   xmlns:fss="http://namespaces.ingeniweb.com/filesystemstorage">
        ...   %s
        ... </configure>'''
        >>> zcml.load_config('meta.zcml', iw.fss)

    Existing product configuration::

        >>> atfile_directive = '''
        ... <fss:typeWithFSS
        ...   class="Products.ATContentTypes.atct.ATFile"
        ...   fields="file" />'''
        >>> config_zcml = template % atfile_directive
        >>> zcml.load_string(config_zcml)

    Make sure we configured it::

        >>> from Products.ATContentTypes.atct import ATFile
        >>> ATFile.schema['file'].storage
        <Storage FileSystemStorage>

    The patched type has been registered::

        >>> from iw.fss.zcml import patchedTypesRegistry
        >>> len(patchedTypesRegistry)
        1
        >>> patchedTypesRegistry[ATFile]
        {u'file': <Storage AnnotationStorage>}

    Not existing content type or class::

        >>> stupid_directive = '''
        ... <fss:typeWithFSS
        ...   class="no.such.class"
        ...   fields="woof" />'''
        >>> config_zcml = template % stupid_directive
        >>> zcml.load_string(config_zcml)
        Traceback (most recent call last):
        ...
        ZopeXMLConfigurationError: ...

    Class is not Archetypes content type::

        >>> stupid_directive = '''
        ... <fss:typeWithFSS
        ...   class="smtplib.SMTP"
        ...   fields="woof" />'''
        >>> config_zcml = template % stupid_directive
        >>> zcml.load_string(config_zcml)
        Traceback (most recent call last):
        ...
        ConfigurationExecutionError: exceptions.AttributeError: class SMTP has no attribute 'schema'
        ...

    No such field in valid content type::

        >>> stupid_directive = '''
        ... <fss:typeWithFSS
        ...   class="Products.ATContentTypes.atct.ATFile"
        ...   fields="file nosuchfield" />'''
        >>> config_zcml = template % stupid_directive
        >>> zcml.load_string(config_zcml)
        Traceback (most recent call last):
        ...
        ConfigurationExecutionError: exceptions.KeyError: u'nosuchfield'
        ...
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(optionflags=ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
