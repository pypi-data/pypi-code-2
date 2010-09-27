from Acquisition import aq_base

from zope.interface import implements, noLongerProvides, alsoProvides
from zope.component import adapts, queryUtility, queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserSkinType
import zope.traversing.namespace
from zope.annotation.interfaces import IAnnotations
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Products.CMFPlone import utils

from themetweaker.themeswitcher.interfaces import IThemeSwitcher

THEMESWITCHER_ANNO = u'themetweaker.themeswitcher'

def _removeThemeSpecificLayers(request, context, current_skin):
    """remove the theme specific layers from above so that they
    don't bleed down into other themes
    """
    # get current skin layers
    portal_state = queryMultiAdapter((context, request),
                                name=u'plone_portal_state')
    portal = portal_state.portal()
    themespecific_layers = []
    # add the currently selected skin interface if it exists
    cur_skin_iface = queryUtility(IBrowserSkinType, name=current_skin)
    if cur_skin_iface is not None:
        themespecific_layers.append(cur_skin_iface)
    # traverse up the tree looking for other applied themes
    # start with the this item's parent
    obj = utils.parent(context)
    while aq_base(obj) is not aq_base(portal):
        if IThemeSwitcher.providedBy(obj):
            parent_anno = IAnnotations(obj)
            skin_name = parent_anno.get(THEMESWITCHER_ANNO, 
                                        None)['themeswitcher_skin']
            skin_iface = queryUtility(IBrowserSkinType, skin_name)
            if skin_iface is not None:
                themespecific_layers.append(skin_iface)
        obj = utils.parent(obj)
    # remove theme specific layers above
    for iface in themespecific_layers:
        noLongerProvides(request, iface)
    return request, context

def _switch(request, context):
    """Switching....
    """
    current_skin = context.getCurrentSkinName()

    annotation = IAnnotations(context)
    skin_anno = annotation.get(THEMESWITCHER_ANNO, None)
    skin_name = None
    if skin_anno is not None:
        skin_name = skin_anno.get('themeswitcher_skin', None)
    # if we have a skin and it's not the currently active skin,
    # switch the skin
    if skin_name is not None and skin_name != current_skin:
        # remove layers
        request, context = _removeThemeSpecificLayers(
            request,
            context,
            current_skin
            )
        
        # switch skins
        context.changeSkin(skin_name, request)
        skin_iface = queryUtility(IBrowserSkinType, skin_name)
        # check to see the skin has a BroswerSkinType
        if skin_iface is not None and \
          not skin_iface.providedBy(request):
            alsoProvides(request, skin_iface)
    return request, context


class ViewTraverser(zope.traversing.namespace.view):
    """overriding to push in the new skin...
    """
    
    def traverse(self, name, ignored):
        """XXX Must be a better place to tap into this...
        
        Right now we are overriding the base 'view' view in order
        to apply the skin to the @@views
        """
        # XXX bare exception, this is because we can't check for
        #     IAnnotation.providedBy(self.context) reliably.
        try:
            self.request, self.context = _switch(self.request, self.context)
        except:
            pass
        return super(ViewTraverser, self).traverse(name, ignored)


class Traverser(DefaultPublishTraverse):
    """Provide traverse features
    """
    adapts(IThemeSwitcher, IBrowserRequest)
    implements(IBrowserPublisher)
    
    def publishTraverse(self, request, name):
        request, self.context = _switch(request, self.context)
        # Then restore normal traversing
        return super(Traverser, self).publishTraverse(request, name)

