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
from Acquisition import aq_inner
from config import SKINS_DIR, GLOBALS
from lbn.zenoss.packutils import _addSkin

def install(context):                                       
    portal = context.getSite()

    # windowZ doesn't have a profile handler ...
    portal.portal_quickinstaller.installProduct('windowZ')

    # we need passthru for reports ...
    portal.portal_windowZ.update(dynamic_window=True)

    zport = aq_inner(portal.aq_parent).zport

    # go register our zport skin ...
    _addSkin(zport.portal_skins, SKINS_DIR, 'bastionzport', GLOBALS)

def uninstall(context):
    portal = context.getSite()

