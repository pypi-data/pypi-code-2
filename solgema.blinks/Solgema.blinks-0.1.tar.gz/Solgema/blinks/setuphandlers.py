from plone.portlets.utils import unregisterPortletType
from zope.component import getUtility, getAdapters
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Solgema.blinks.portlets.solgemablinks import ISolgemaBlinksPortlet

# Check for Plone versions
try:
   from plone.app.upgrade import v40
   HAS_PLONE30 = True
   HAS_PLONE40 = True
except ImportError:
   HAS_PLONE40 = False
   try:
       from Products.CMFPlone.migrations import v3_0
   except ImportError:
       HAS_PLONE30 = False
   else:
       HAS_PLONE30 = True

def removeSolgemaBlinksPortlet(portal):
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
    right = getMultiAdapter((portal, rightColumn,), IPortletAssignmentMapping, context=portal)
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping, context=portal)
    for portlet_id in right:
        if HAS_PLONE40:
            if ISolgemaBlinksPortlet.providedBy(right[portlet_id]):
                del right[portlet_id]
        else:
            if ISolgemaBlinksPortlet.isImplementedBy(right[portlet_id]):
                del right[portlet_id]
    for portlet_id in left:
        if HAS_PLONE40:
            if ISolgemaBlinksPortlet.providedBy(left[portlet_id]):
                del left[portlet_id]
        else:
            if ISolgemaBlinksPortlet.isImplementedBy(left[portlet_id]):
                del left[portlet_id]

def uninstallSolgemaBlinks(context):
    if context.readDataFile('blinks_uninstall.txt') is None:
        return
    site = context.getSite()
    removeSolgemaBlinksPortlet(site)
    unregisterPortletType(site, 'portlet.SolgemaBlinks')
