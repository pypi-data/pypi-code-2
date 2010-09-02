from Products.statusmessages.interfaces import IStatusMessage

from zope.component import getMultiAdapter
from Products.CMFPlone import PloneMessageFactory as _
from zope import component
from zope import interface
from zope.formlib import form
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations

from zope.component import getUtility

from Products.Five.formlib.formbase import EditForm
from Products.Five.utilities import marker
from Products.Five.browser import BrowserView

from getpaid.discount.browser.interfaces import IDiscountable
from getpaid.discount.browser.interfaces import IBuyXGetXFreeable
from getpaid.discount.browser.interfaces import ICodeDiscountable
from getpaid.discount.browser.interfaces import IDiscountableMarker
from getpaid.discount.browser.interfaces import IBuyXGetXFreeableMarker
from getpaid.discount.browser.interfaces import ICodeDiscountableMarker

from Products.PloneGetPaid.interfaces import IPayableMarker

from getpaid.core import interfaces
from getpaid.core.interfaces import IShoppingCartUtility

class DiscountForm(EditForm):
    """
    """
    form_fields = form.FormFields(IDiscountable)
    marker = IDiscountableMarker
    actions = form.Actions()
    interface = IDiscountable
    
    def allowed( self ):
        adapter = component.queryAdapter( self.context, IPayableMarker)
        return not (adapter is None)

class DiscountEdit(DiscountForm):
    """
    """
    @form.action(_(u'Update', default=u'Update'),name=u'update', condition=form.haveInputWidgets)
    def update_discountable( self, action, data):
        self.handle_edit_action.success_handler( self, action, data )
        message = 'Changes saved.'
#        result = translate(msgid, domain='plone',context=self.request)
        self.request.response.redirect( '%s/view?portal_status_message=%s' % (self.context.absolute_url(), message) )

class DiscountCreation(DiscountForm):
    """
    """

    @form.action(_(u'Activate', default=u'Activate'),name=u'activate',condition=form.haveInputWidgets)
    def activate_discountable( self, action, data):
        #we set up the type as IDiscountable
        interface.alsoProvides(self.context, self.marker)

        self.handle_edit_action.success_handler( self, action, data )
#        message = 'Changes saved.'
#        self.request.response.redirect( '%s/view?portal_status_message=%s' % (self.context.absolute_url(), message) )
        IStatusMessage(self.request).addStatusMessage(_("Changes saved."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(self.context.absolute_url())

class DiscountDestruction(BrowserView):
    marker = IDiscountableMarker
    
    def __call__(self):
        marker.erase( self.context, self.marker )
        self.request.response.redirect( '%s/view' % self.context.absolute_url() )

class BuyXGetXFreeEdit(DiscountEdit):
    """
    """
    interface = IBuyXGetXFreeable
    form_fields = form.FormFields(IBuyXGetXFreeable)
    marker = IBuyXGetXFreeableMarker

class BuyXGetXFreeCreation(DiscountCreation):
    """
    """
    interface = IBuyXGetXFreeable
    form_fields = form.FormFields(IBuyXGetXFreeable)
    marker = IBuyXGetXFreeableMarker

class BuyXGetXFreeDestruction(DiscountDestruction):
    marker = IBuyXGetXFreeableMarker

class CodeDiscountableEdit(DiscountEdit):
    """
    """
    interface = ICodeDiscountable
    form_fields = form.FormFields(ICodeDiscountable)
    marker = ICodeDiscountableMarker

class CodeDiscountableCreation(DiscountCreation):
    """
    """
    interface = ICodeDiscountable
    form_fields = form.FormFields(ICodeDiscountable)
    marker = ICodeDiscountableMarker

class CodeDiscountableDestruction(DiscountDestruction):
    marker = ICodeDiscountableMarker

class DiscountAdapter(object):
    """
    """
    implements(IDiscountable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        discount_title = self.annotations.get('discount_title', None)
        if discount_title is None:
            self.annotations['discount_title'] = ''
        discount_type = self.annotations.get('discount_type', None)
        if discount_type is None:
            self.annotations['discount_type'] = 'Dollars Off'
        discount_value = self.annotations.get('discount_value', None)
        if discount_value is None:
            self.annotations['discount_value'] = 0.0
    
    def getDiscountTitle(self):
        return self.annotations['discount_title']

    def setDiscountTitle(self, data):
        self.annotations['discount_title'] = data

    def getDiscountType(self):
        return self.annotations['discount_type']

    def setDiscountType(self, data):
        self.annotations['discount_type'] = data
    
    def getDiscountValue(self):
        return self.annotations['discount_value']

    def setDiscountValue(self, data):
        self.annotations['discount_value'] = data
    
    discount_title = property(fget=getDiscountTitle, fset=setDiscountTitle)
    discount_type = property(fget=getDiscountType, fset=setDiscountType)
    discount_value = property(fget=getDiscountValue, fset=setDiscountValue)

class BuyXGetXFreeAdapter(object):
    """
    """
    implements(IBuyXGetXFreeable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        discount_title = self.annotations.get('discount_title', None)
        if discount_title is None:
            self.annotations['discount_title'] = ''
        number_to_buy = self.annotations.get('number_to_buy', None)
        if number_to_buy is None:
            self.annotations['number_to_buy'] = 0
        number_free = self.annotations.get('number_free', None)
        if number_free is None:
            self.annotations['number_free'] = 0
    
    def getDiscountTitle(self):
        return self.annotations['discount_title']

    def setDiscountTitle(self, data):
        self.annotations['discount_title'] = data

    def getNumberToBuy(self):
        return self.annotations['number_to_buy']

    def setNumberToBuy(self, data):
        self.annotations['number_to_buy'] = data
    
    def getNumberFree(self):
        return self.annotations['number_free']

    def setNumberFree(self, data):
        self.annotations['number_free'] = data
    
    discount_title = property(fget=getDiscountTitle, fset=setDiscountTitle)
    number_to_buy = property(fget=getNumberToBuy, fset=setNumberToBuy)
    number_free = property(fget=getNumberFree, fset=setNumberFree)

class CodeDiscountableAdapter(object):
    """
    """
    implements(ICodeDiscountable)
    
    def _getDiscountTitle(x):
        def func(self):
            return self.annotations['discount_title_%s' % x]
    
        return func

    def _setDiscountTitle(x):
        def func(self, data):
            self.annotations['discount_title_%s' % x] = data
            
        return func

    def _getDiscountCode(x):
        def func(self):
            return self.annotations['discount_code_%s' % x]

        return func

    def _setDiscountCode(x):
        def func(self, data):
            if data:
                data = data.strip()
            self.annotations['discount_code_%s' % x] = data

        return func
    
    def _getDiscountedPrice(x):
        def func(self):
            return self.annotations['discounted_price_%s' % x]

        return func

    def _setDiscountedPrice(x):
        def func(self, data):
            self.annotations['discounted_price_%s' % x] = data

        return func

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)

        for f in [1,2,3]:
            title = 'discount_title_%s' % f
            code = 'discount_code_%s' % f
            price = 'discounted_price_%s' % f

            setattr(self, title, self.annotations.get(title, None))
            if getattr(self, title, None) is None:
                self.annotations[title] = ''

            setattr(self, code, self.annotations.get(code, None))
            if getattr(self, code, None) is None:
                self.annotations[code] = ''

            setattr(self, price, self.annotations.get(price, None))
            if getattr(self, price, None) is None:
                self.annotations[price] = 0.0

    discount_title_1 = property(fget=_getDiscountTitle(1), fset=_setDiscountTitle((1)))
    discount_code_1 = property(fget=_getDiscountCode(1), fset=_setDiscountCode(1))
    discounted_price_1 = property(fget=_getDiscountedPrice(1), fset=_setDiscountedPrice(1))

    discount_title_2 = property(fget=_getDiscountTitle(2), fset=_setDiscountTitle(2))
    discount_code_2 = property(fget=_getDiscountCode(2), fset=_setDiscountCode(2))
    discounted_price_2 = property(fget=_getDiscountedPrice(2), fset=_setDiscountedPrice(2))

    discount_title_3 = property(fget=_getDiscountTitle(3), fset=_setDiscountTitle(3))
    discount_code_3 = property(fget=_getDiscountCode(3), fset=_setDiscountCode(3))
    discounted_price_3 = property(fget=_getDiscountedPrice(3), fset=_setDiscountedPrice(3))

class ApplyDiscountCode(BrowserView):
    """
    """
    # create form that:
    #   - accepts a code
    #   - iterates over cart and checks that an item provides ICodeDiscountable
    #   - it also does not provide IDiscountable
    #   - Creates new IDiscountable set appropiatly and drops item price
    def __call__(self):
        code = self.request.form.get('discount.code', None)
        code = code.strip()

        self.cart = getUtility(IShoppingCartUtility).get(self.context) or {}

        if not self.cart:
            order_id = self.request.get("order_id", None)
            if order_id:
                order_manager = component.getUtility(interfaces.IOrderManager)
                self.cart = order_manager.get(order_id).shopping_cart

        if code is not None and len(code) is not 0 and self.cart:
            
            for item in self.cart.values():

                ref_obj = item.resolve()
                payable_quantity = item.quantity

                annotation = IAnnotations(item)

                if ref_obj \
                   and ICodeDiscountableMarker.providedBy(ref_obj) \
                   and not "getpaid.discount.code" in annotation:

                    adapter_obj = ICodeDiscountable(ref_obj)

                    for f in [1,2,3]:
                        discount_title = 'discount_title_%s' % f
                        discount_code = 'discount_code_%s' % f
                        discounted_price = 'discounted_price_%s' % f

                        if code.lower() == getattr(adapter_obj, discount_code, '').lower():

                            discounted_price = getattr(adapter_obj, discounted_price)
                        
                            annotation["getpaid.discount.code"] = getattr(adapter_obj, discount_code)

                            # Here I want to create a new IDiscountableMarker
                            # I also want to drop the price on this payable_line    
                            annotation["getpaid.discount.code.title"] = getattr(adapter_obj, discount_title)
                            discount = item.cost - discounted_price
                            item.cost = discounted_price
                            total_discount = discount * item.quantity
                            annotation["getpaid.discount.code.discount"] = "%.2f" % (total_discount)

        self.request.response.redirect('@@getpaid-cart')

    
