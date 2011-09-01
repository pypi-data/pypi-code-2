import logging
from Acquisition import aq_inner, aq_parent
from Products.CMFCore import utils as cmfutils

logger = logging.getLogger('PloneFlashUpload')

def non_view_context(orig_context):
    context = orig_context
    for x in range(5):
        newcontext = getattr(context, 'context', None)
        if newcontext is None:
            break
        context = newcontext

    return context

def find_user(context, userid):
    """Walk up all of the possible acl_users to find the user with the
    given userid.
    """

    track = set()

    acl_users = aq_inner(cmfutils.getToolByName(context, 'acl_users'))
    path = '/'.join(acl_users.getPhysicalPath())
    logger.debug('Visited acl_users "%s"' % path)
    track.add(path)

    user = acl_users.getUserById(userid)
    while user is None and acl_users is not None:
        context = aq_parent(aq_parent(aq_inner(acl_users)))
        acl_users = aq_inner(cmfutils.getToolByName(context, 'acl_users'))
        if acl_users is not None:
            path = '/'.join(acl_users.getPhysicalPath())
            logger.debug('Visited acl_users "%s"' % path)
            if path in track:
                logger.warn('Tried searching an already visited acl_users, '
                            '"%s".  All visited are: %r' % (path, list(track)))
                break
            track.add(path)
            user = acl_users.getUserById(userid)

    if user is not None:
        user = user.__of__(acl_users)

    return user
