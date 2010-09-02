from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.discount')
from zope.component import getUtility

from zope import component
from getpaid.core import interfaces

from plone.app.layout.viewlets.common import ViewletBase

from getpaid.core.interfaces import IShoppingCartUtility

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from getpaid.discount.browser.interfaces import IDiscountableMarker
from getpaid.discount.browser.interfaces import IDiscountable
from getpaid.discount.browser.interfaces import IBuyXGetXFreeable
from getpaid.discount.browser.interfaces import IBuyXGetXFreeableMarker
from getpaid.discount.browser.interfaces import ICodeDiscountable
from getpaid.discount.browser.interfaces import ICodeDiscountableMarker

from zope.annotation.interfaces import IAnnotations

class DiscountListingViewlet(ViewletBase):
    render = ViewPageTemplateFile('discount_listing.pt')
    
    def update(self):
        #self.portal_state = getMultiAdapter((self.context, self.request),
        #                                    name=u'plone_portal_state')
        #self.portal_url = self.portal_state.portal_url()
        self.cart = getUtility(IShoppingCartUtility).get(self.context) or {}
        # if cart is destroyed, we'll use the order_id to retrieve the cart detail and discount
        if not self.cart:
            order_id = self.request.get("order_id", None)
            if order_id:
                order_manager = component.getUtility(interfaces.IOrderManager)
                #self.order = order_manager.get(order_id)
                self.cart = order_manager.get(order_id).shopping_cart
        
    def getDiscounts(self):
        """
        for all the items in the cart
        we look if they have a discount
        and if so, we bring back a list of dictionaries
        """
        results = []
        if self.cart:
            for payable_line in self.cart.values():
                annotation = IAnnotations(payable_line)
                ref_obj = payable_line.resolve()
                payable_quantity = payable_line.quantity
                if ref_obj and IDiscountableMarker.providedBy(ref_obj):
                    adapter_obj = IDiscountable(ref_obj)
                    discount_value = adapter_obj.getDiscountValue()
                    if discount_value != 0.0:
                        discount_title = adapter_obj.getDiscountTitle()
                        discount_type = adapter_obj.getDiscountType()
                        if discount_type != 'Dollars Off':

                            msgid = _(u"total_discount_off", default= u"${discount_value_X}", mapping={ u"discount_value_X" : discount_value* payable_quantity})
                            description = translate(msgid, domain='getpaid.discount',context=self.request)
                            # total value of the discount would be a better word
                                                                                
                        else:
                            msgid = _(u"total_discount_percentage", default= u"Total of ${discount_value_percentage}", mapping={ u"discount_value_percentage" : discount_value* payable_quantity})
                            description = translate(msgid, domain='getpaid.discount',context=self.request)
                        msgid = _(u"discount_title_ref_obj_title", default= u"${discount_title} on ${ref_obj_title}", mapping={ u"discount_title" : discount_title,u"ref_obj_title":ref_obj.Title()})
                        title = translate(msgid, domain='getpaid.discount',context=self.request)  
                        res = {'title': title, 'description': description}
                        results.append(res)
                elif IBuyXGetXFreeableMarker.providedBy(ref_obj):
                    adapter_obj = IBuyXGetXFreeable(ref_obj)
                    number_to_buy = adapter_obj.getNumberToBuy()
                    number_free = adapter_obj.getNumberFree()
                    if number_to_buy != 0 and number_free != 0:
                        discount_title = adapter_obj.getDiscountTitle()
                        number_res = int(payable_quantity / number_to_buy * number_free)
                        msgid = _(u"free_additional_items_number", default=u"${number_res} free additional item(s)", mapping={ u"number_res":str(number_res)})
                        description = translate(msgid, domain='getpaid.discount',context=self.request)
                        msgid = _(u"free_additional_items_title", default= u"${discount_title} on ${ref_obj_title}", mapping={u"discount_title":discount_title,u"ref_obj_title":ref_obj.Title()})
  
                        res = {'title': translate(msgid, domain='getpaid.discount',context=self.request), 
                           'description': description
                          }
                    results.append(res)
                elif ICodeDiscountableMarker.providedBy(ref_obj) \
                     and "getpaid.discount.code" in annotation:

                    discount_title = annotation["getpaid.discount.code.title"]
                    discount_value = annotation["getpaid.discount.code.discount"]
                    if discount_value != 0.0:
                        msgid = _(u"total_percentage_off", default= u"Total of ${discount_value} off", mapping={ u"discount_value" : discount_value})
                        description = translate(msgid, domain='getpaid.discount', context=self.request)
                        msgid = _(u"total_percentage_off_title", default= u"${discount_title} on ${ref_obj_title} off", mapping={ u"discount_title" : discount_title,u"ref_obj_title":ref_obj.Title()})
                        title = translate(msgid, domain='getpaid.discount',context=self.request)
                        res = {'title': title, 
                               'description': description
                              }
                        results.append(res)

        return results

class DiscountCodeViewlet(ViewletBase):
    render = ViewPageTemplateFile('discount_code.pt')
    
    def update(self):
        #self.portal_state = getMultiAdapter((self.context, self.request),
        #                                    name=u'plone_portal_state')
        #self.portal_url = self.portal_state.portal_url()
        self.cart = getUtility(IShoppingCartUtility).get(self.context) or {}
        # if cart is destroyed, we'll use the order_id to retrieve the cart detail and discount
        if not self.cart:
            order_id = self.request.get("order_id", None)
            if order_id:
                order_manager = component.getUtility(interfaces.IOrderManager)
                #self.order = order_manager.get(order_id)
                self.cart = order_manager.get(order_id).shopping_cart
        

