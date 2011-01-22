##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Grok test helpers
"""
import sys
import grokcore.component
from zope.configuration.config import ConfigurationMachine
from martian import scan
from grokcore.component import zcml

def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    zcml.do_grok('grokcore.view.meta.views', config)
    zcml.do_grok('grokcore.view.meta.templates', config)
    zcml.do_grok('grokcore.view.meta.skin', config)
    # Use the Five override for the page template factory
    # zcml.do_grok('grokcore.view.templatereg', config)
    zcml.do_grok('five.grok.templatereg', config)
    zcml.do_grok('five.grok.meta', config)
    zcml.do_grok(module_name, config)
    config.execute_actions()

def grok_component(name, component,
                   context=None, module_info=None, templates=None):
    if module_info is None:
        obj_module = getattr(component, '__grok_module__', None)
        if obj_module is None:
            obj_module = getattr(component, '__module__', None)
        module_info = scan.module_info_from_dotted_name(obj_module)

    module = module_info.getModule()
    if context is not None:
        grokcore.component.context.set(module, context)
    if templates is not None:
        module.__grok_templates__ = templates
    config = ConfigurationMachine()
    result = zcml.the_multi_grokker.grok(name, component,
                                         module_info=module_info,
                                         config=config)
    config.execute_actions()
    return result

def warn(message, category=None, stacklevel=1):
    """Intended to replace warnings.warn in tests.

    Modified copy from zope.deprecation.tests to:

      * make the signature identical to warnings.warn
      * to check for *.pyc and *.pyo files.

    When zope.deprecation is fixed, this warn function can be removed again.
    """
    print "From five.grok.testing's warn():"

    frame = sys._getframe(stacklevel)
    path = frame.f_globals['__file__']
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]

    file = open(path)
    lineno = frame.f_lineno
    for i in range(lineno):
        line = file.readline()

    print "%s:%s: %s: %s\n  %s" % (
        path,
        frame.f_lineno,
        category.__name__,
        message,
        line.strip(),
        )


from zope.app.testing.placelesssetup import tearDown as _cleanUp
def cleanUp():
    '''Cleans up the component architecture.'''
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0

def setDebugMode(mode):
    '''Allows manual setting of Five's inspection of debug mode
       to allow for ZCML to fail meaningfully.
    '''
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode

import five.grok
def safe_load_site():
    '''Loads entire component architecture (w/ debug mode on).'''
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    zcml.load_config('ftesting.zcml', five.grok)
    setDebugMode(0)

class Layer:

    def setUp(cls):
        '''Sets up the CA by loading etc/site.zcml.'''
        safe_load_site()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        cleanUp()
    tearDown = classmethod(tearDown)

GrokFunctionalLayer = Layer

