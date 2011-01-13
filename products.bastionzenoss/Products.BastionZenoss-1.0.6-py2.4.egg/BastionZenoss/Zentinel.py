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
import Globals
from Products.CMFCore.utils import UniqueObject, registerToolInterface
from zope.interface import implements

from Products.windowZ.content.Window import Window

from config import ZENTINEL_TOOL
from interfaces import IZentinelTool

class ZentinelTool(UniqueObject, Window):
    """
    The zport wrapped thingy

    This is essentially a place-holder until we fully skin Zenoss
    """
    meta_type = 'Zentinel Tool'
    portal_type = Window.portal_type

    implements(IZentinelTool)

    def __init__(self, id=ZENTINEL_TOOL):
        Window.__init__(self, id)

    def manage_afterAdd(self, item, container):
        self.update(title='Zenoss Zentinel',
                    catalog_page_content=False,
                    show_reference=False,
                    remoteUrl='/zport/dmd')

Globals.InitializeClass(ZentinelTool)
registerToolInterface(ZENTINEL_TOOL, IZentinelTool)
