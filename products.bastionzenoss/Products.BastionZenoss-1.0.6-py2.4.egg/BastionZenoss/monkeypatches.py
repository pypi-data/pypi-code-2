#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import logging
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


logger = logging.getLogger('BastionZenoss')

def noop(*args, **kw): pass

#
# seems that this pesky function is removing inituser without successfully
# installing it ...
#
logger.info('monkeypatching ZenUtils.Security')
from Products.ZenUtils import Security
Security._createInitialUser = noop


#
# Zenoss hard-code underlying skin templates which is most unsporting!
#
from Products.ZenUI3.browser.macros import PageTemplateMacros, BBBMacros

PTMacros_get_orig = PageTemplateMacros.__getitem__
 
def PTMacros_get(self, key):
        if key in ('page1', 'page2'):
	    return getattr(aq_inner(self.context), 'templates').macros[key]
        return PTMacros_get_orig(self, key)


def BBBMacros_get(self, key):
    if key=='macros':
        return self
    return getattr(aq_inner(self.context), 'templates').macros[key]


logger.info('Monkeypatching main templates overrides')

PageTemplateMacros.__getitem__ = PTMacros_get
BBBMacros.__getitem__ = BBBMacros_get

#
# add password type into Properties on ZMI (but since these aren't writable, it's moot
# and of course, we'd need to plug the properties.dtml for impact in ZMI)
#
from ZPublisher.Converters import type_converters, field2string
type_converters['password'] = field2string

logger.info('added type converter: password')
