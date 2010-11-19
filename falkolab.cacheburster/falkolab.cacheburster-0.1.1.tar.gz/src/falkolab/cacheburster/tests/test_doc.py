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
import re
import os
import unittest

from zope.app.testing import functional
from zope.testing import renormalizing
from falkolab.cacheburster.testing import CacheBursterLayer, testsPath

def getTemplateContent(name):   
    pageTemplate = os.path.join(os.path.dirname(__file__),
       'testfiles', name)
    f = open(pageTemplate, 'r')
    data = f.read()
    f.close()
    return data

def test_suite():    
    suite = unittest.TestSuite()
    s = functional.FunctionalDocFileSuite(
        '../README.txt',     
        globs={'getTemplateContent': getTemplateContent,
               'testsPath':testsPath},   
        checker = renormalizing.RENormalizing([
            (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
            ])
        )
    s.layer = CacheBursterLayer
    suite.addTest(s)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')