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

import Globals, os, logging
from config import *

from Acquisition import aq_base
from Products.CMFCore import utils
from Products.ZenModel.ZenPack import ZenPackBase
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent

logger = logging.getLogger(PROJECTNAME)
logger.info('Installing ZopeMonitor')

for directory in (SKINS_DIR, os.path.join(os.path.dirname(__file__), SKINS_DIR)):
    try:
        registerDirectory(directory, GLOBALS)
    except:
        pass

from lbn.zenoss import packutils
import setuphandlers


class ZenPack(ZenPackBase):
    """ Zenoss eggy thing """
    packZProperties = [
        ('zZopeURI', 'http://admin:password@localhost:8080', 'string'),
        ]

    def install(self, zport):
        """
        Set the collector plugin
        """
        ZenPackBase.install(self, zport)

	setuphandlers.install(zport)

def initialize(context):
    """ Zope Product """
    
    zport = packutils.zentinel(context)
    if zport and not hasZenPack(zport, __name__):
	zpack = ZenPack(__name__)
        packutils.addZenPack(zport, zpack, SKINS_DIR, SKINNAME, GLOBALS)
        setuphandlers.install(zport, zpack)


