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
from Globals import ImageFile

import logging, string
from Products.CMFCore.DirectoryView import registerDirectory, addDirectoryViews
from Products.CMFCore import utils as coreutils
from Products.CMFCore.permissions import AddPortalContent
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot

from config import *
from browser.sitesetup import createZentinel, createPlone

# classes requiring registration
import Reporting

registerDirectory(SKINS_DIR, GLOBALS)

logger = logging.getLogger('BastionZenoss')
logger.info('Installing...')

# fix up stuff ...
import monkeypatches

def initialize(context):
    """
    """
    try:
        profile_registry.registerProfile('default',
                                         PROJECTNAME,
                                         'bastionzenoss',
                                         'profiles/default',
                                         PROJECTNAME,
                                         EXTENSION,
                                         IPloneSiteRoot)
    except KeyError:
        # duplicate entry ...
        pass

    #
    # create the Plone instance and auto-install us
    # 
    app = context._ProductContext__app

    if not getattr(app, 'plone', None):
        createPlone(app)

    #
    # create the zport/dmd stuff - this could take a while ...
    #
    if not getattr(app, 'zport', None):
        createZentinel(app)
