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
from Acquisition import aq_base, aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.ZenUtils.Utils import zenPath
from Products.ZenUtils.CmdBase import CmdBase
from Products.ZenModel.zenbuild import zenbuild

from Products.BastionZenoss.config import *

from lbn.zenoss.packutils import _addSkin

# we need to make sure CMFPlone's zcml is loaded so portal_setup will find it's profile
import Products.CMFPlone
import Products.GenericSetup
from Products.CMFPlone.factory import _DEFAULT_PROFILE, addPloneSite
from Products.GenericSetup.registry import _profile_registry


logger = logging.getLogger('BastionZenoss.sitesetup')

def createPlone(context):
    """
    funtion to create a Plone site
    """
    try:
        if not _profile_registry._profile_info.has_key(_DEFAULT_PROFILE):
            from Products.Five import zcml
            zcml.load_config('configure.zcml', Products.GenericSetup)  # need gs tags
            zcml.load_config('configure.zcml', Products.CMFPlone)
        addPloneSite(context, 'plone', title='ZenPlone Portal')
        context.plone.portal_quickinstaller.installProduct('Products.BastionZenoss')
    except:
        logger.error('Create Plone instance failed', exc_info=True)

def createZentinel(context, skipusers=True):
    """
    function to create a zport
    """
    try:
        zb = bzenbuild(context)

        # hmmm - lets just accept defaults
        #zb.options.evthost,
        #zb.options.evtuser,
        #zb.options.evtpass,
        #zb.options.evtdb,
        #zb.options.evtport,
        #zb.options.smtphost,
        #zb.options.smtpport,
        #zb.options.pagecommand        

        zb.build()

        zport = context.zport

        # go register our skin ...
        skinstool = zport.portal_skins
        _addSkin(skinstool, 'skins', 'lbn.zenoss', GLOBALS)
        
        # this is the qs-nousersetup functionality ...
        if skipusers:
            zport.dmd._rq = True

    except:
        logger.error('Create Zentinel instance failed', exc_info=True)


class bzenbuild(zenbuild):
    """
    no command-line opts zenbuild
    """
    revertables = ('index_html', 'standard_error_message')

    def __init__(self, context):
        CmdBase.__init__(self, noopts=True)
        self.app = context.getPhysicalRoot()
        

    def build(self):
        """
        don't let zenbuild trash default Zope
        """
        app = self.app
        for id in self.revertables:
            if app.hasObject(id):
                app.manage_renameObject(id, '%s.save' % id)

        zenbuild.build(self)

        # move the Zenoss standard_error_message
        std_err = aq_base(app._getOb('standard_error_message'))
        app.zport._setObject('standard_error_message', std_err)

        for id in self.revertables:
            if app.hasObject(id):
                app._delObject(id)

            app.manage_renameObject('%s.save' % id, id)

class SiteSetup(BrowserView):
    """
    Creates a Zenoss installation
    """

    def createZentinel(self, skipusers=True):
        """
        creates zport, DMD in install root
        """
        context = aq_inner(self.context)

        createZentinel(context,skipusers)

        self.request.set('manage_tabs_message', 'created zenoss dmd')
        self.request.RESPONSE.redirect('zport/dmd')


    def createMySql(self):
        """
        setup (local) MySQL for Events processing
        """
        self.request.set('manage_tabs_message', 'created MySQL')
        self.request.redirect('manage_main')
