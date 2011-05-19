from zope.event import notify
from zope.component import adapts, getUtility
from zope.interface import implements, alsoProvides
from getpaid.core.interfaces import ILineItemFactory, IShoppingCart
from getpaid.core.item import PayableLineItem, RecurringLineItem
from pfg.donationform.interfaces import IDonationFieldSet, DonationCreatedEvent, IDonationCart
from zope.app.intid.interfaces import IIntIds
from Products.PloneGetPaid import sessions
from Products.CMFPlone.utils import safe_unicode

class DonationFieldLineItemFactory(object):
    implements(ILineItemFactory)
    adapts(IShoppingCart, IDonationFieldSet)
    
    def __init__(self, cart, field):
        self.cart = cart
        self.field = field

    def create(self):

        pfg = self.field.aq_parent
        form = self.field.REQUEST.form
        fname = self.field.getId()
        amount = form.get(fname + '_level')
        if not amount:
            amount = form.get(fname + '_amount', '0')
        amount = amount.lstrip('$')
        is_recurring = form.get(fname + '_recurring', False)
        occurrences = form.get(fname + '_occurrences', 9999)
        
        if is_recurring:
            item = RecurringLineItem()
            item.interval = 1
            item.unit = 'months'
            item.total_occurrences = occurrences
        else:
            item = PayableLineItem()
        item.item_id = self.field.UID()
        item.uid = getUtility(IIntIds).register(self.field)
        item.name = safe_unicode(pfg.Title())
        item.cost = float(amount)
        item.quantity = 1
        
        if item.item_id in self.cart:
            # replace existing donation from same form
            del self.cart[item.item_id]
        self.cart[item.item_id] = item
        
        alsoProvides(self.cart, IDonationCart)
        notify(DonationCreatedEvent(self.cart))
        
        try:
            sessions.set_came_from_url(pfg)
        except:
            pass
        return item
