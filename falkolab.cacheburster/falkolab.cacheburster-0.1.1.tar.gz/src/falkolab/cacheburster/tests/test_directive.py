#############################################################################
#
# Copyright (c) 2010 Falko Lab and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
import os
import unittest
import zope.component
from cStringIO import StringIO

from zope.configuration.xmlconfig import XMLConfig, xmlconfig
from zope.publisher.browser import TestRequest
from zope.testing import cleanup
import zope.browserresource

import falkolab.cacheburster
from zope.browserresource.file import FileResource
from falkolab.cacheburster.interfaces import IVersionRule,\
    IVersionedResourceLayer, IVersionManager
from falkolab.cacheburster.rule import CacheBursterRule
from falkolab.cacheburster.version import MD5VersionManager, CRC32VersionManager,\
    FileVersionManager
from falkolab.cacheburster import version
from zope.interface.declarations import  directlyProvides
from falkolab.cacheburster.testing import ITestSkin


"""
'browser' namespace directive tests
"""


tests_path = os.path.join(
    os.path.dirname(falkolab.cacheburster.__file__),
    'tests')


template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


   
request = TestRequest()
directlyProvides(request, ITestSkin)

   
class Test(cleanup.CleanUp, unittest.TestCase):
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.browserresource)()
        XMLConfig('meta.zcml', falkolab.cacheburster)()       
        
        zope.component.provideAdapter(MD5VersionManager, name='md5')
        zope.component.provideAdapter(CRC32VersionManager, name='crc32')
        
        file = os.path.join(tests_path, 'testfiles', 'version.txt')
        zope.component.provideAdapter(FileVersionManager(file), 
                                (version.IResource, IVersionedResourceLayer),
                                IVersionManager, name='versionfile')
                       
    def tearDown(self):
        super(Test, self).tearDown()
        
    def testVersionAdapters(self):            
        path = os.path.join(tests_path, 'testfiles', 'script.js')

        xmlconfig(StringIO(template %
            '''
            <browser:resource
                name="script.js"
                file="%s"
                />
             ''' % path
            ))
        
        resource = zope.component.getAdapter(request, name='script.js')
        self.assertTrue(isinstance(resource, FileResource))
                
        self.assertNotEqual(zope.component.queryMultiAdapter((resource, request), 
                            name='crc32'), None)
        self.assertNotEqual(zope.component.queryMultiAdapter((resource, request), 
                            name='md5'), None)
        
    def testRules(self):        
       
        path = os.path.join(tests_path, 'testfiles', 'script.js')
        xmlconfig(StringIO(template %
            r'''
            <browser:resource
                name="script.js"
                file="%s"
                />
                
            <browser:cacheburster 
                from="(.*)\.js" 
                to="\1.{version}.js"
                fileset="testfiles/*.js"
                />
                
            <browser:cacheburster 
                from="(.*)-module\.js" 
                to="\1-module.js?{version}"
                manager="md5"
                />           
            ''' % path
            ))
        
        resource = zope.component.getAdapter(request, name='script.js')
        self.assertTrue(isinstance(resource, FileResource))
        n=0
        for name, rule in zope.component.getAdapters((resource,), IVersionRule):
            n+=1            
            self.assertTrue(isinstance(rule, CacheBursterRule))
            
        self.assertEqual(n, 2)
        
    
        



def test_suite():
    return unittest.makeSuite(Test)
