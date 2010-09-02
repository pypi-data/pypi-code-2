from zope import schema
from zope.interface import Interface
from getpaid.discount import discountMessageFactory as _
class IDiscountable(Interface):
    """
    Marker interface for the Discountable items
    """
    discount_title = schema.TextLine(title=_(u'Discount Title'),
                           required=True)
    
    discount_type = schema.Choice(title=_(u'Type of Discount'),
                                  values=[_(u'Dollars Off'), _(u'Percentage Off')],
                                  required=True)
    
    discount_value = schema.Float(title=_(u'Value of the discount'),
                                  required=True,)

class IDiscountableMarker(Interface):
    """
    Discount Interface
    """

class IBuyXGetXFreeable(Interface):
    """
    Marker interface for the BuyXGetXFreeable items
    """
    discount_title = schema.TextLine(title=_(u'Discount Title'),
                           required=True)
    
    number_to_buy = schema.Int(title=_(u'Number of items to buy'),
                                  required=True)
    
    number_free = schema.Int(title=_(u'Number of free items'),
                                  required=True)

class IBuyXGetXFreeableMarker(Interface):
    """
    Discount Interface
    """

class ICodeDiscountable(Interface):
    """
    Marker interface for the CodeDiscountable items
    """
    discount_title_1 = schema.TextLine(title=_(u'Discount Title'),
                           required=True)

    discount_code_1 = schema.TextLine(title=_(u'Discount Code'),
                           required=True)
    
    discounted_price_1 = schema.Float(title=_(u'Price after Discount'),
                                  required=True,)


    discount_title_2 = schema.TextLine(title=_(u'Second Discount Title'),
                           required=False)

    discount_code_2 = schema.TextLine(title=_(u'Second Discount Code'),
                           required=False)
    
    discounted_price_2 = schema.Float(title=_(u'Price after Second Discount'),
                                  required=False,)


    discount_title_3 = schema.TextLine(title=_(u'Third Discount Title'),
                           required=False)

    discount_code_3 = schema.TextLine(title=_(u'Third Discount Code'),
                           required=False)
    
    discounted_price_3 = schema.Float(title=_(u'Price after Third Discount'),
                                  required=False,)


class ICodeDiscountableMarker(Interface):
    """
    Discount Interface
    """
