from Acquisition import aq_parent, aq_inner
from zope.component import getUtility
from Products.Quota.interfaces import IQuotaService


def objectMovedHandler(ob, event):
    """
    handler for IObjectMovedEvent
    """
    if ob.isTemporary():
        return

    qs = getUtility(IQuotaService)
    increment = qs.get_increment(ob)
    size = qs.get_size(ob)
    old_size = size - increment

    # for moves and deletes
    if event.oldParent is not None:
        qs.recurse_quota(event.oldParent, -old_size)

    # for moves and creations
    if event.newParent is not None:
        qs.recurse_quota(event.newParent, size)

def objectModifiedHandler(ob, event):
    """
    handler for IObjectModifiedEvent
    """
    if ob.isTemporary():
        return

    try:
        parent = aq_parent(aq_inner(ob))
    except AttributeError:
        return

    qs = getUtility(IQuotaService)
    increment = qs.get_increment(ob)

    qs.recurse_quota(parent, increment)







