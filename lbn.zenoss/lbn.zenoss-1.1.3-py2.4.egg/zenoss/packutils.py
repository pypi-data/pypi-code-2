#
#    Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#

__doc__ = """
This is a bunch of helper functions that support creating and deploying
ZenPack-like modules as pure Python
"""

import string, logging, pkg_resources, os, re
from Acquisition import aq_base
from zExceptions import BadRequest
from Products.CMFCore.DirectoryView import registerDirectory, addDirectoryViews
from Products.ZenModel.RRDTemplate import RRDTemplate

logger = logging.getLogger('lbn.zenoss.packutils')
Metatag = re.compile('^([A-Z].+): (.+)$')

def zentinel(context):
    """
    return the zentinel object from an initialize context (or None)
    """
    app = context._ProductContext__app
    return getattr(app, 'zport', None)

def hasZenPack(zport, zenpackname):
     """
     check if the ZenPackManager has this ZenPack
     """
     mgr = zport.dmd.ZenPackManager
     return mgr.packs._getOb(zenpackname, None) is not None

def addZenPack(zport, packname, skins_dir, skinname, GLOBALS):
    """
    uber function to handle all Product --> ZenPack registration
    """
    _registerPack(zport, packname, force=True)
    _addSkin(zport.portal_skins, skins_dir, skinname, GLOBALS)

def addZenPackObjects(zenpack, objs):
    """
    add a bunch of objects to the ZenPack
    """
    expanded = []
    for obj in objs:
        expanded.append(obj)
        if isinstance(obj, RRDTemplate):
            for ds in obj.datasources.objectValues():
                expanded.append(ds)
                expanded.extend(ds.datapoints.objectValues())
            for gd in obj.graphDefs.objectValues():
                expanded.append(gd)
                expanded.extend(gd.graphPoints.objectValues())

    for obj in expanded:
        obj.buildRelations()
        try:
            zenpack.packables.addRelation(obj)
        except:
            logger.error('failed adding %s into %s' % (obj, zenpack.getId()))

def _addSkin(skinstool, skins_dir, skinname, GLOBALS):
    """
    helper to register our skins directory
    """
    if getattr(aq_base(skinstool), skinname, None):
        return

    logger.info('adding skin %s/%s' % (skins_dir, skinname))

    try:
        addDirectoryViews(skinstool, skins_dir, GLOBALS)
    except BadRequest:
        # hmmm - probably just adding a directory name that's already present
	pass

    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        for layer in (skinname,):
            if layer not in path:
                try:
                    path.insert(path.index('custom')+1, layer)
                except ValueError:
                    path.append(layer)
        path = ','.join(path)
        skinstool.addSkinSelection(skin, path)


def _registerPack(zport, zenpack, force=False):
    """
    register with ZenPackManager - necessary to become datasource-aware etc
    """
    mgr = zport.dmd.ZenPackManager
    modulename = zenpack.getId()

    if mgr.packs._getOb(modulename, None):
        logger.info('ZenPack already registered: %s' % modulename)
	if not force:
            return
    else:
        mgr.packs._setObject(modulename, zenpack)

    logger.info('Adding ZenPack %s' % modulename)

    mgr.packs._setObject(modulename, zenpack)
    pack = mgr.packs._getOb(modulename)

    pack.eggPack = True

    egg = pkg_resources.get_distribution(modulename)

    pkginfo = {}
    for line in egg._get_metadata('PKG-INFO'):
        match = Metatag.match(line)
        if match:
            k,v = match.groups()
            pkginfo[k] = v

    pack.manage_changeProperties(title=modulename,
                                 version=egg.version,
                                 author=pkginfo.get('Author', ''),
                                 organization=pkginfo.get('Author', ''),
                                 url=pkginfo.get('Home-page',''),
                                 license=pkginfo.get('License', ''))
                      
    # now create datasources, reports, modules/plugins etc etc
    module_dir = egg.project_name.split('.')
    path = os.path.join(egg.location, *module_dir)

    logger.info('Installing egg path %s' % path)

    pack.install(pack)


