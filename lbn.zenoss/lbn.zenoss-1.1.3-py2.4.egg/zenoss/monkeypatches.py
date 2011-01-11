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
import Globals, logging
from config import GLOBALS

logger = logging.getLogger('lbn.zenoss')


#
# add password type into Properties on ZMI (but since these aren't writable, it's moot)
#
from ZPublisher.Converters import type_converters, field2string
type_converters['password'] = field2string

from Products.ZenModel.ZenModelRM import ZenModelRM
ZenModelRM.manage_propertiesForm = Globals.DTMLFile('dtml/properties', globals(), property_extensible_schema__=1)

logger.info('added type converter: password')

#
# patch icons and ZMI
#
import OFS
misc_ = OFS.misc_.Misc_('lbn.zenoss', {})
for icon in ('ZenossInfo_icon', 'RelationshipManager_icon', 'portletmanager'):
    misc_[icon] = Globals.ImageFile('www/%s.gif' % icon, GLOBALS)
setattr(OFS.misc_.misc_, 'lbn.zenoss', misc_)

from Products.ZenRelations.ToManyRelationshipBase import ToManyRelationshipBase, RelationshipBase
ToManyRelationshipBase.manage_options = ToManyRelationshipBase.manage_options + OFS.SimpleItem.SimpleItem.manage_options


from Products.ZenWidgets.PortletManager import PortletManager
PortletManager.icon = 'misc_/lbn.zenoss/portletmanager'

from Products.ZenModel.ZenossInfo import ZenossInfo
ZenossInfo.icon = 'misc_/lbn.zenoss/ZenossInfo_icon'

from Products.ZenRelations.RelationshipManager import RelationshipManager
RelationshipManager.icon = 'misc_/lbn.zenoss/RelationshipManager_icon'

# TODO - override RelationshipManager.manage_workspace to be default ...

# note that we're also strapping an implements(IItem) via zcml ...
import AccessControl
from Products.ZenRelations.ZItem import ZItem

ZItem.manage_options = AccessControl.Owned.Owned.manage_options + ( 
    {'label':'Interfaces', 'action':'manage_interfaces'}, 
    ) 


#
# the Skin registration stuff is borked for python modules, but we want to retain
# them for other zenpacks where it might still work ...
#
from Products.ZenModel.ZenPackLoader import ZPLSkins
ZPLSkinsload = ZPLSkins.load
ZPLSkinsunload = ZPLSkins.unload

def skinLoad(self, pack, app):
    try:
	ZPLSkinsload(self, pack, app)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

def skinUnload(self, pack, app, leaveObjects=False):
    try:
	ZPLSkinsunload(self, pack, app, leaveObjects)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

ZPLSkins.load = skinLoad
ZPLSkins.unload = skinUnload

