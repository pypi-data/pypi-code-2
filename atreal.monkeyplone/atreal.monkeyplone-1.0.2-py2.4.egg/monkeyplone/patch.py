from zope.component import getMultiAdapter
from zope.component import queryUtility

from plone.memoize.instance import memoize
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.portlets.portlets.review import Renderer

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
#
# plone.app.portlets-1.2-py2.4/plone/app/portlets/portlets/review.py
# => Show fullname in place of login
def _data(self):
    if self.anonymous:
        return []
    context = aq_inner(self.context)
    workflow = getToolByName(context, 'portal_workflow')
    
    plone_view = getMultiAdapter((context, self.request), name=u'plone')
    getIcon = plone_view.getIcon
    toLocalizedTime = plone_view.toLocalizedTime

    idnormalizer = queryUtility(IIDNormalizer)
    norm = idnormalizer.normalize
    membership = getToolByName(context, 'portal_membership')
    objects = workflow.getWorklistsResults()
    items = []
    for obj in objects:
        review_state = workflow.getInfoFor(obj, 'review_state')
        author = membership.getMemberInfo(obj.Creator())
        items.append(dict(
            path = obj.absolute_url(),
            title = obj.pretty_title_or_id(),
            description = obj.Description(),
            icon = getIcon(obj).html_tag(),
            creator = (author and author['fullname'] or obj.Creator()),
            review_state = review_state,
            review_state_class = 'state-%s ' % norm(review_state),
            mod_date = toLocalizedTime(obj.ModificationDate()),
        ))
    return items




from AccessControl import getSecurityManager
from Acquisition import aq_parent, aq_inner, aq_base
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.PortalFolder import PortalFolderBase
#
# Products.CMFCore-2.1.2-py2.4.egg/Products/CMFCore/PortalFolder.py
# => Don't check a DeleteObject permission on parent on a paste action
def _verifyObjectPasteCMFCore(self, object, validate_src=1):
    # This assists the version in OFS.CopySupport.
    # It enables the clipboard to function correctly
    # with objects created by a multi-factory.
    mt = getattr(object, '__factory_meta_type__', None)
    meta_types = getattr(self, 'all_meta_types', None)

    if mt is not None and meta_types is not None:
        method_name = None
        mt_permission = None

        if callable(meta_types):
            meta_types = meta_types()

        for d in meta_types:
            if d['name'] == mt:
                method_name = d['action']
                mt_permission = d.get('permission')
                break

        if mt_permission is not None:
            sm = getSecurityManager()

            if sm.checkPermission(mt_permission, self):
                if validate_src:
                    # Ensure the user is allowed to access the object on
                    # the clipboard.
                    parent = aq_parent(aq_inner(object))

                    if not sm.validate(None, parent, None, object):
                        raise AccessControl_Unauthorized(object.getId())

                    if validate_src == 2: # moving
                        if not sm.checkPermission("View", parent):
                            raise AccessControl_Unauthorized('Delete not '
                                                             'allowed.')
            else:
                raise AccessControl_Unauthorized('You do not possess the '
                        '%r permission in the context of the container '
                        'into which you are pasting, thus you are not '
                        'able to perform this operation.' % mt_permission)
        else:
            raise AccessControl_Unauthorized('The object %r does not '
                    'support this operation.' % object.getId())
    else:
        # Call OFS' _verifyObjectPaste if necessary
        PortalFolderBase.inheritedAttribute(
            '_verifyObjectPaste')(self, object, validate_src)

    # Finally, check allowed content types
    if hasattr(aq_base(object), 'getPortalTypeName'):

        type_name = object.getPortalTypeName()

        if type_name is not None:

            pt = getToolByName(self, 'portal_types')
            myType = pt.getTypeInfo(self)

            if myType is not None and not myType.allowType(type_name):
                raise ValueError('Disallowed subobject type: %s'
                                    % type_name)

