from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.discount')
from zope.i18n import translate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from getpaid.discount.browser.interfaces import IDiscountableMarker
from getpaid.discount.browser.interfaces import IBuyXGetXFreeableMarker
from getpaid.discount.browser.portlets25 import BaseDiscountPortlet

from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.PloneGetPaid.interfaces import PayableMarkerMap
from Products.PloneGetPaid.interfaces import IPayableMarker
from Products.PloneGetPaid.browser.portlets import buy
from Products.PloneGetPaid.browser.portlets import donate
from Products.PloneGetPaid.browser.portlets import premium
from Products.PloneGetPaid.browser.portlets import ship

class DiscountRenderer(base.Renderer, BaseDiscountPortlet):
    """Plone 3.0 Base rendered useful for discount portlets.
    """

    # Marker interface that this renderer is meant for.
    marker = IPayableMarker
    # Supply a template id in the inheriting class.

    @property
    def available(self):
        """Portlet is available when a marker interface is provided.

        Overwrite this by picking a different interface.
        """
        return self.marker.providedBy(self.context)
        
    @property
    def payable(self):
        """Return the payable (shippable) version of the context.
        """
        iface = PayableMarkerMap.get(self.marker, None)
        if iface is None:
            # Something is badly wrong here.
            return None
        return iface( self.context )


class IDiscountablePortlet(IPortletDataProvider):
    pass


class DiscountableAssignment(base.Assignment):
    implements(IDiscountablePortlet)

    @property
    def title(self):
        """Title shown in @@manage-portlets.
        """
        msgid = _(u"Discountable_portlet", default= u"Discountable Portlet")
        result = translate(msgid, domain='getpaid.discount')

        return result


class DiscountableAddForm(base.NullAddForm):

    def create(self):
        return DiscountableAssignment()


class DiscountableRenderer(DiscountRenderer):
    marker = IDiscountableMarker
    render = ViewPageTemplateFile('../templates/portlet_content_discountable.pt')


class IBuyXGetXfreeablePortlet(IPortletDataProvider):
    pass


class BuyXGetXfreeableAssignment(base.Assignment):
    implements(IBuyXGetXfreeablePortlet)

    @property
    def title(self):
        """Title shown in @@manage-portlets.
        """
        return _(u"BuyXGetXFreeable")


class BuyXGetXfreeableAddForm(base.NullAddForm):

    def create(self):
        return BuyXGetXfreeableAssignment()


class BuyXGetXfreeableRenderer(DiscountRenderer):
    marker = IBuyXGetXFreeableMarker
    render = ViewPageTemplateFile('../templates/portlet_content_buyxgetxfreeable.pt')


#Plone 3 renderers for the portlets
class BuyRenderer(buy.Renderer):
    """"""
    
    @property
    def available(self):
        """"""
        return self.marker.providedBy(self.context) and \
            not IDiscountableMarker.providedBy(self.context) and \
            not IBuyXGetXFreeableMarker.providedBy(self.context)

class DonateRenderer(donate.Renderer):
    """"""
    
    @property
    def available(self):
        """"""
        return self.marker.providedBy(self.context) and \
            not IDiscountableMarker.providedBy(self.context) and \
            not IBuyXGetXFreeableMarker.providedBy(self.context)

class PremiumRenderer(premium.Renderer):
    """"""
    
    @property
    def available(self):
        """"""
        return self.marker.providedBy(self.context) and \
            not IDiscountableMarker.providedBy(self.context) and \
            not IBuyXGetXFreeableMarker.providedBy(self.context)

class ShipRenderer(ship.Renderer):
    """"""
    
    @property
    def available(self):
        """"""
        return self.marker.providedBy(self.context) and \
            not IDiscountableMarker.providedBy(self.context) and \
            not IBuyXGetXFreeableMarker.providedBy(self.context)


