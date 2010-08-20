import logging
import zope.component
from zope.interface import noLongerProvides
from Products.CMFCore.utils import getToolByName
from Products.Five.utilities.marker import mark
from Products.SimpleAlias.config import PROJECTNAME
from interfaces import IAliasLinkedTo

logger = logging.getLogger(PROJECTNAME)

def sync_title_desc(context, event):
    """
    Sync title and description of alias.
    """
    catalog = getToolByName(context, 'portal_catalog')
    aliases = context.getBRefs(relationship='linksTo')
    for obj in aliases:
        if not obj.getAutoTitle():
            continue
        path = '/'.join(obj.getPhysicalPath())
        aliasbrains = catalog(path=path)
        if len(aliasbrains) > 0:
            if aliasbrains[0].Title != context.Title():
                obj.reindexObject()
                logger.info(u"Re-indexed %s" % '/'.join(obj.getPhysicalPath()))
        else:
            logger.info(u"Couldn't find %s in catalog. Re-indexed it" % '/'.join(obj.getPhysicalPath()))
        
def mark_linked_object(context, event):
    """
    Mark linked object with marker interface to keep title and description in sync.
    """
    if context.getAlias() and context.getAutoTitle():
        obj = context.getAlias()
        if not IAliasLinkedTo.providedBy(obj):
            mark(obj, IAliasLinkedTo)
            setattr(context, '_alias_linked_object', obj.UID())

def unmark_linked_object(context, event):
    """
    Unmark linked object when the reference is removed and
    when the alias is deleted.
    N.B. this also works when the alias is deleted as the reference
    is cleared prior to the removed event being called as per this thread:
    http://plone.293351.n2.nabble.com/Event-on-object-deletion-tp3670562p3758817.html
    """
    refcat = getToolByName(context, 'reference_catalog')
    if not context.getAlias() and getattr(context, '_alias_linked_object', False):
        obj = refcat.lookupObject(getattr(context, '_alias_linked_object'))
        if obj:
            if IAliasLinkedTo.providedBy(obj):
                noLongerProvides(obj, IAliasLinkedTo)
                delattr(context, '_alias_linked_object')
                logger.info(u"Removed interface from %s" % '/'.join(obj.getPhysicalPath()))