"""
    Expose viewlets to renderable in the templates by their name.

"""


__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>'
__docformat__ = 'epytext'
__copyright__ = "2009-2010 mFabrik Research Oy"
__license__ = "GPL 2"


import logging

from Acquisition import aq_inner
import zope.interface

from plone.app.customerize import registration

from Products.Five.browser import BrowserView

from zope.traversing.interfaces import ITraverser, ITraversable
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewlet

from collective.fastview.interfaces import ViewletNotFoundException

logger = logging.getLogger("collective.fastview")

class Viewlets(BrowserView):
    """ Expose arbitary viewlets to traversing by name.

    Exposes viewlets to templates by names.

    Example how to render plone.logo viewlet in arbitary template code point::

        <div tal:content="context/@@viewlets/plone.logo" />

    """

    def getViewletByName(self, name):
        """ Viewlets allow through-the-web customizations.

        Through-the-web customization magic is managed by five.customerize.
        We need to think of this when looking up viewlets.

        @return: Viewlet registration object
        """
        views = registration.getViews(IBrowserRequest)

        found = None

        # Get active layers on the currest request object
        wanted_layers = list(self.request.__provides__.__iro__)
                
        # List of all viewlet registration with the name
        # Note: several registrations possible due to layers
        possible = []

        for v in views:

            if v.provided == IViewlet:
                # Note that we might have conflicting BrowserView with the same name,
                # thus we need to check for provided
                if v.name == name:
                    possible.append(v)

        wanted_layers = wanted_layers[:]
        
        for layer in wanted_layers:

            for viewlet_registration in possible:

                # (<InterfaceClass zope.interface.Interface>, <InterfaceClass gomobiletheme.basic.interfaces.IThemeLayer>, <InterfaceClass zope.publisher.interfaces.browser.IBrowserView>, <implementedBy gomobiletheme.basic.viewlets.MainViewletManager>)
                theme_layer = viewlet_registration.required[1]
                if theme_layer == layer:
                    return viewlet_registration

        return None

    def setupViewletByName(self, name):
        """ Constructs a viewlet instance by its name.

        Viewlet update() and render() method are not called.

        @return: Viewlet instance of None if viewlet with name does not exist
        """
        context = aq_inner(self.context)
        request = self.request

        # Perform viewlet regisration look-up
        # from adapters registry
        reg = self.getViewletByName(name)
        if reg == None:
            return None

        # factory method is responsible for creating the viewlet instance
        factory = reg.factory

        # Create viewlet and put it to the acquisition chain
        # Viewlet need initialization parameters: context, request, view
        
        from Shared.DC.Scripts.Bindings import UnauthorizedBinding

        if isinstance(context, UnauthorizedBinding):
            # Viewlets cannot be constructed on Unauthorized error pages, so we try to reconstruct them using the site root
            context = context.portal_url.getPortalObject()
        
        try:
            viewlet = factory(context, request, self, None)
            
        except TypeError, e:
            logger.exception(e)
            raise RuntimeError("Unable to initialize viewlet %s. Factory method %s call failed." % (name, str(factory)))

        if hasattr(viewlet, "__of__"):
            # Plone 3 viewlets with implicit acquisiton
            viewlet = viewlet.__of__(context)

        return viewlet

    def __getitem__(self, name):
        """
        Allow travering intoviewlets by viewlet name.

        @return: Viewlet HTML output

        @raise: ViewletNotFoundException if viewlet is not found
        """
        viewlet = self.setupViewletByName(name)
        if viewlet is None:
            active_layers = [ str(x) for x in self.request.__provides__.__iro__ ]
            active_layers = tuple(active_layers)
            raise ViewletNotFoundException("Viewlet does not exist by name %s for the active theme layer set %s. Probably theme interface not registered in plone.browserlayers. Try reinstalling the theme."  % (name, str(active_layers)))

        viewlet.update()
        return viewlet.render()

