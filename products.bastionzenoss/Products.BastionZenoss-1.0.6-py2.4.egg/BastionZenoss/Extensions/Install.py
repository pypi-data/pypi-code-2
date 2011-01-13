#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Last Bastion Network Pty Ltd BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.BastionZenoss.config import *


def install(portal):                                       
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')

    setup_tool.runAllImportStepsFromProfile(
                "profile-BastionZenoss:default",
                purge_old=False)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(portal, reinstall=False):
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setImportContext('profile-BastionZenoss:default')
    setup_tool.runAllImportSteps()
    try:
        setup_tool.setImportContext('profile-CMFPlone:plone')
    except:
	pass
    return "Ran all uninstall steps."


#
# it's a pain when this module won't load - this immediately lets us know !!!

# but you might need /usr/lib/zope/lib/python in $PYTHONPATH
#
if __name__ == '__main__':
    print 'brilliant - it compiles ...'
