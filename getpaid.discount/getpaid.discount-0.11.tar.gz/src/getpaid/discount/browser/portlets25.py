from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.discount')
from Products.Five.browser import BrowserView

from getpaid.discount.browser.interfaces import IDiscountableMarker
from getpaid.discount.browser.interfaces import IBuyXGetXFreeableMarker
from getpaid.discount.browser.interfaces import IDiscountable
from getpaid.discount.browser.interfaces import IBuyXGetXFreeable

from Products.PloneGetPaid.interfaces import PayableMarkerMap

class BaseDiscountPortlet(object):
    """
    """
    def isDiscountable(self):
        return IDiscountableMarker.providedBy(self.context)
    
    def isBuyXGetXFreeable(self):
        return IBuyXGetXFreeableMarker.providedBy(self.context)
    
    def getPrice(self, item):
        """
        returns the price of the payable item
        """
        for marker, iface in PayableMarkerMap.items():
            if marker.providedBy(item):
                payable = iface(item)
                return payable.price
        return None
     
    def hasNormalDiscount(self, item):
        """
        returns a nice display of the discount on the item
        """
        result = None
        price = self.getPrice(item)
        if IDiscountableMarker.providedBy(item) and price:
            adapter_obj = IDiscountable(item)
            discount_value = adapter_obj.getDiscountValue()
            if discount_value != 0.0:
                discount_type = adapter_obj.getDiscountType()
                if discount_type == 'Dollars Off':
                    
                    msgid = _(u"details_discount_off", default= u"${discounted_value}( ${discount_value} off )", mapping={ u"discounted_value" : price - discount_value, u"discount_value": discount_value})
                    result = translate(msgid, domain='getpaid.discount',context=self.request)
                    #result = "$%0.2f ($%0.2f off)" % (price - discount_value, discount_value)
                else:
                    msgid = _(u"details_discount_percentage", default= u"${discounted_value_percentage}(${discount_value} \%off)", mapping={ u"discounted_value_percentage" : price - price*discount_value/100, u"discount_value": discount_value})
                    result = translate(msgid, domain='getpaid.discount',context=self.request)
                    
                    #result = "$%0.2f (%0.0f%s off)" % (price - price*discount_value/100, discount_value, '%')
        return result

    def hasBuyXGetXFreeDiscount(self, item):
        """
        returns a nice display of the discount on the item
        """
        result = None
        if IBuyXGetXFreeableMarker.providedBy(item):
            adapter_obj = IBuyXGetXFreeable(item)
            number_to_buy = adapter_obj.getNumberToBuy()
            number_free = adapter_obj.getNumberFree()
            if number_to_buy != 0 and number_free != 0:
                #result = "Order %d get %d additional free" % (number_to_buy, number_free)
                msgid = _(u"orderx_getyfree", default= u"Order ${number_to_buy} get ${number_free} additional free (${number_total})", mapping={ u"number_to_buy" : number_to_buy, u"number_free": number_free, u"number_total": number_free + number_to_buy})
                result = translate(msgid, domain='getpaid.discount',context=self.request)
                
        return result
    

class DiscountContentPortlet(BrowserView, BaseDiscountPortlet):
    """ Plone 2.5 View methods for the ContentPortlet """
    
    def __init__(self, *args, **kw):
        super(BrowserView, self).__init__(*args, **kw)
        
        
class PGPContentPortlet(BrowserView):
    """ Plone 2.5 override of the View methods for the ContentPortlet """
    payable = None
    def __init__( self, *args, **kw):
        super( BrowserView, self).__init__( *args, **kw)

        found = False
        for marker, iface in PayableMarkerMap.items():
            if marker.providedBy( self.context ):
                found = True
                break

        if found:
            self.payable = iface( self.context )
        
    def isPayable(self):
        return self.payable is not None and \
            not IDiscountableMarker.providedBy(self.context) and \
            not IBuyXGetXFreeableMarker.providedBy(self.context)

