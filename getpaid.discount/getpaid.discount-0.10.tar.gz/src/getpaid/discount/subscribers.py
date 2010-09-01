from getpaid.discount.browser.interfaces import IDiscountable
from getpaid.discount.browser.interfaces import IDiscountableMarker


from Products.CMFCore.utils import getToolByName

def checkDiscount(self, event):
    """
    Check if an item has a discount on it and 
    change the total depending on that
    """
    item = event.object
    ref_obj = item.resolve()
    
    if IDiscountableMarker.providedBy(ref_obj):
        adapter_obj = IDiscountable(ref_obj)
        discount_value = adapter_obj.getDiscountValue()
        if discount_value != 0.0:
            discount_type = adapter_obj.getDiscountType()
            if discount_type == 'Dollars Off':
                item.cost = item.cost - discount_value
            else:
                item.cost = item.cost - item.cost*discount_value/100
