from zope.interface import Interface#, Attribute
from zope import schema
from Products.PFGVerkkomaksut import PFGVerkkomaksutMessageFactory as _

class IPFGVerkkomaksut(Interface):
    """Interface for Verkkomaksut adapter.
    """

    attachments_before_verkkomaksut = schema.Choice(
        title=_(u"E-mail attachments before Verkkomaksut"),
        required=False,
        description=_(u"Please select the attachments to be sent with email when one has successfully finished inputs of the form."),
        vocabulary="attachments",
    )

    merchant_id = schema.IntegerLine(
        title=_(u"Merchant ID"),
        description=_(u'Please input MERCHANT_ID provided by Verkkomaksut here. The default ID is for demo use which is 13466.'),
        required=True,
        default=13466,
    )

    merchant_authentication_code = schema.TextLine(
        title=_(u"Merchant Authentication Code"),
        description=_(u'Please input Merchant Authentication Code provided by Verkkomaksut here. The default ID is for demo use which is 6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ.'),
        required=True,
        default='6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ',
    )

    next_order_number = schema.IntegeterLine(
        title=_(u"Next Order Number"),
        required=True,
        description=_(u'Please input the next order number here. This number will be automatically increased by one for each transaction and will be sent to Verkkomksut.'),
        default=1,
        )

    price_field = schema.Choice(
        title=_(u"Price Field"),
        required=True,
        description=_(u"Please select the price field which will be used for Verkkomakusut. Remember to add fixed-point field or selection field with required option checked to the form folder first."),
        vocabulary="price_fields",
    )

    thanks_text = schema.Text(
        title=_(u"Thanks Text"),
        description=_(u"This thanks text will be displayed when payment is successful."),
        required=False,
    )

    cancel_message = schema.TextLine(
        title=_(u"Cancel Message"),
        description=_(u'This message will be shown when one cancels Verkkomaksut payment.'),
        required=False,
    )

    def attachments():
        """
            Attachments from the contents of the form folder.
            They are either images or files.
        """

    def price_fields():
        """
            Price fields driven from contents in the form.
            Fixed point field and selection field with required option checked could be selected.
        """

    def selected_price_field():
        """
            Field selected as the price field.
        """

#    shop_currency = schema.Choice(
#        title=_(u"Shop Currency"),
#        required=True,
#        description=_(u"Choose one currency your shop use to maintain it."),
#        vocabulary=_(u"Currencies")
#    )

#    content_languages = schema.Choice(
#        title=_(u"Content Languages"),
#        required=True,
#        description=_(u"Only selected languages here can be used to create contents inside the shop."),
#        vocabulary=_(u"Content Languages")
#    )

#    company_name = schema.TextLine(
#        title=_(u"Company Name"),
#        description=_(u"Fill legaly registered name here."),
#        required=True
#    )

#    vat_number = schema.TextLine(
#        title=_(u"VAT No."),
#        description=_(u"Fill VAT number here."),
#        required=True
#    )

#    contact_phone_number = schema.TextLine(
#        title=_(u"Contact Phone Number"),
#        required=True
#    )

#    contact_address = schema.TextLine(
#        title=_(u"Contact Address"),
#        required=True
#    )

#    postal_code = schema.TextLine(
#        title=_(u"Postal Code"),
#        required=True
#    )

#    country = schema.Choice(
#        title=_(u"Country"),
#        required=True,
#        description=_(u"Choose one country where your shop(company) is located."),
#        vocabulary=_(u"Countries")
#    )

#    updated_items_amount = schema.Choice(
#        title=_(u'Updated Items Amount'),
#        required=True,
#        description=_(u'Amount of New Items and Restocked Items to be displayed on top page of shop.'),
#        vocabulary=_(u'Updated Items Amount'),
#        )

#    gross_profit_margin_rate = schema.Float(
#        title=_(u"Gross Profit Margin Rate"),
#        description=_(u"Do not input anything here if you are not going to use this gross profit margin rate as prices for products."),
#        required=False
#   )

#class IAbitaMallAbout(Interface):
#    title = schema.TextLine(
#        title=_(u"Title"),
#        required=False,
#    )

#    description = schema.TextLine(
#        title=_(u"Description"),
#        required=False,
#    )

#    text = schema.SourceText(
#        title=_(u"text"),
#        required=False,
#    )

#class IAbitaMallProduct(Interface):
#    """A folder which is ShopItem.
#    """
#    contains(
#        'abita.mall.interfaces.IAbitaMallProduct',
#        'Products.ATContentTypes.interfaces.IATImage',
#        'abita.mall.interfaces.IAbitaMallAbout'
#        )

#    sku = schema.TextLine(
#        title=_(u"SKU"),
#        required=True
#    )

#    selling = schema.Bool(
#        title = _(u"Selling Item"),
#        description = _(u"If this item is not selling item, like you use this item as items container, check out this option.")
#    )

#    manufacture = schema.TextLine(
#        title=_(u"Manufacture"),
#    )

#    vat = schema.Choice(
#        title=_(u"VAT"),
#        description = _(u"Please select vat for this product."),
#        required = True,
#        vocabulary ="abita.mall.VAT",
#        default = u'0.00',
#    )

#    primecost = schema.Float(
#        title = _(u"Prime Cost"),
#        description = _(u"VAT free prime cost."),
#        required = True,
#        default = 0.0
#    )

#    manual_pricing = schema.Bool(
#        title = _(u"Manual Pricing"),
#        description = _(u"Check this if you input selling price manually."),
#    )

#    price = schema.Float(
#        title = _(u"Price"),
#        description = _(u"Input the selling price including VAT."),
#        required=True,
#    )

#    stock = schema.Int(
#        title = _(u'Stock'),
#        required=False,
#    )

#    weight_unit = schema.Choice(
#        title=_(u"Weight Unit"),
#        values=[u'g', u'kg'],
#        description = _(u"Please select the weight unit for this product."),
#        required = True,
#        default = u'g',
#    )

#    package_weight = schema.Float(
#        title = _(u"Package Weight"),
#        description = _(u"Please input total weight of product package."),
#        required=True,
#    )

#    package_height = schema.Float(
#        title = _(u'Package Height'),
#        description = _(u"Please input height of product package in cm unit."),
#        required=False,
#    )

#    package_width = schema.Float(
#        title = _(u'Package Width'),
#        description = _(u"Please input width of product package in cm unit."),
#        required=False,
#    )

#    package_depth = schema.Float(
#        title = _(u'Package Depth'),
#        description = _(u"Please input depth of product package in cm unit."),
#        required=False,
#    )

#    content_weight = schema.Float(
#        title = _(u"Content Weight"),
#        description = _(u"Please input weight of product content withought package."),
#        required=False,
#    )

#    content_height = schema.Float(
#        title = _(u'Content Height'),
#        description = _(u"Please input height of product content withought package in cm unit."),
#        required=False,
#    )

#    content_width = schema.Float(
#        title = _(u'Content Width'),
#        description = _(u"Please input width of product content withought package in cm unit."),
#        required=False,
#    )

#    content_depth = schema.Float(
#        title = _(u'Content Depth'),
#        description = _(u"Please input depth of product content withought package in cm unit."),
#        required=False,
#    )

#    content_diameter = schema.Float(
#        title = _(u'Content Diameter'),
#        description = _(u"Please input diameter of product content withought package in cm unit."),
#        required=False,
#    )

##    buyable = schema.Bool(
##        required=False,
##    )

#class IAbitaMallShippingMethod(Interface):

#    title = schema.TextLine(
#        title=_(u"Title"),
#        required=True
#    )

#    description = schema.TextLine(
#        title=_(u"Description"),
#    )

#    from_country = schema.Choice(
#        title=_(u"Country From"),
#        required=True,
#        description=_(u"Choose countries from which this shipping method is applied."),
#        vocabulary=_(u"Countries")
#    )

#    to_country = schema.Choice(
#        title=_(u"Country To"),
#        required=True,
#        description=_(u"Choose countries to which this shipping method is applied."),
#        vocabulary=_(u"Countries")
#    )


#    base_charge = schema.Float(
#        title=_(u"Base Shipping Charge"),
#        description=_(u"This is starting charge for shipping."),
#        required=True,
#   )

#    weight_charge = schema.Float(
#        title=_(u"Weight Charge"),
#        description=_(u"This charge will be added every kg of weight."),
#        required=True,
#   )

#    fuel_charge = schema.Float(
#        title=_(u"Fuel Charge"),
#        description=_(u"Fuel Charge usually changes every month."),
#        required=True,
#   )

#    risk_margin = schema.Float(
#        title=_(u"Risk Margin"),
#        description=_(u"Give risk margin in %. 0% means no risk margin, so you apparently want to give some positive % here."),
#        required=True,
#   )

#    minimum_delivery_days = schema.Int(
#        title=_(u"Minimum Delivery Days"),
#        required=True,
#   )

#    max_delivery_days = schema.Int(
#        title=_(u"Maximum Delivery Days"),
#        required=True,
#   )

#    volume_weight_ratio = schema.Float(
#        title=_(u"Volume Weight Ratio"),
#        description=_(u"1 m3 = ??? kg"),
#        required=True,
#   )

#    insurance_base = schema.Float(
#        title=_(u"Base Price of Insurance"),
#        description=_(u""),
#        required=True,
#   )
#    insurance_rate = schema.Float(
#        title=_(u"Base Rate of Insurance"),
#        description=_(u"This amount of % will be added to the total product price."),
#        required=True,
#   )

#class IAbitaMallCarts(Interface):
#    """IOBTree which contains carts."""

#class IAbitaMallCart(Interface):
#    shipping_info = Attribute('shipping_info')
#    shops = Attribute('shops')
##    payer_info = Attribute('payer_info')
##    shipping_method = Attribute('shipping_method')
##    number = Attribute('number')
##    state = Attribute('state')
##    language = Attribute('language')
##    member = Attribute('member')
##    payment_method = Attribute('payment_method')
##    order_number = Attribute('order_number')


#    def is_vat_free():
#        """Returns True if vat free if else False."""

#    def selected_currency_code():
#        """Returns selected currency code."""

#    def overall_total():
#        """Returns decimal overall total."""

#    def overall_vat_free_total():
#        """Returns decimal overall vat free total."""

#    def overall_total_with_currency():
#        """Returns overall total with currency."""

#    def overall_total_in_selected_currency_code():
#        """Returns overall total in selected currency code."""

#    def overall_vat_free_total_in_selected_currency_code():
#        """Returns overall vat free total in selected currency code."""

#    def overall_total_with_selected_currency_code():
#        """Returns overall total with selected currency code."""


#class IAbitaMallCartShippingMethod(Interface):
#    uid = Attribute('uid')
#    title = Attribute('title')
#    titel_en = Attribute('title_en')
#    description = Attribute('description')
#    base_charge = Attribute('base_charge')
#    weight_charge = Attribute('weight_charge')
#    fuel_charge = Attribute('fuel_charge')
#    risk_margin = Attribute('risk_margin')
#    minimum_delivery_days = Attribute('minimum_delivery_days')
#    max_delivery_days = Attribute('max_delivery_days')
#    volume_weight_ratio = Attribute('volume_weight_ratio')

#class IAbitaMallCartShop(Interface):
#    uid = Attribute('uid')
#    title = Attribute('title')
#    url = Attribute('url')
#    products = Attribute('products')

#    def total_products_price():
#        """Returns decimal total products price."""

#    def total_products_vat_free_price():
#        """Returns decimal total products vat free price."""

#    def current_total_products_price():
#        """Returns decimal total products price or total products vat free price depending on vat."""

#    def total_products_price_with_currency():
#        """Returns total products price with currency."""

#    def total_products_price_in_selected_currency_code():
#        """Returns decimal total products price in selected currency code."""

#    def total_products_vat_free_price_in_selected_currency_code():
#        """Returns decimal total products vat free price in selected currency code."""

#    def current_total_products_price_in_selected_currency_code():
#        """Returns decimal total products price or total products vat free price in selected currency code depending on vat."""

#    def total_products_price_with_selected_currency_code():
#        """Returns total products price with selected currency code."""

#    def shipping_cost():
#        """Returns decimal shipping cost."""

#    def shipping_cost_with_currency():
#        """Retruns shipping cost with currency."""

#    def shipping_cost_in_selected_currency_code():
#        """Returns decimal shipping cost in selected currency code."""

#    def shipping_cost_with_selected_currency_code():
#        """Returns shipping cost with selected currency code."""

#    def total_cost():
#        """Returns decimal total cost."""

#    def total_vat_free_cost():
#        """Returns decimal total vat free cost."""

#    def total_cost_with_currency():
#        """Returns total cost with currency."""

#    def total_cost_in_selected_currency_code():
#        """Returns total cost in selected currency code."""

#    def total_vat_free_cost_in_selected_currency_code():
#        """Returns total vat free cost in selected currency code."""

#    def total_cost_with_selected_currency_code():
#        """Returns total cost with selected currency code."""

#class IAbitaMallCartProduct(Interface):
#    uid = Attribute('uid')
#    url = Attribute('url')
#    sku = Attribute('sku')
#    title = Attribute('title')
#    title_en = Attribute('title_en')
#    vat = Attribute('vat')
#    primecost = Attribute('primecost')
#    price = Attribute('price')
#    vat_free_price = Attribute('vat_free_price')
#    vat_price = Attribute('vat_price')
#    profit = Attribute('profit')
#    price_with_currency = Attribute('price_with_currency')
#    price_in_selected_currency_code = Attribute('price_in_selected_currency_code')
#    vat_free_price_in_selected_currency_code = Attribute('product.vat_free_price_in_selected_currency_code')
#    price_with_selected_currency_code = Attribute('product.price_with_selected_currency_code')
#    stock = Attribute('stock')
#    stock_list = Attribute('stock_list')
#    weight_in_kg = Attribute('weight_in_kg')
#    dimensions = Attribute('dimensions')
#    quantity = Attribute('quantity')

#    def subtotal_price():
#        """Returns decimal subtotal price of the product."""

#    def subtotal_vat_free_price():
#        """Returns decimal subtotal vat free price of the product."""

#    def subtotal_vat_price():
#        """Returns decimal subtotal vat price of the product."""

#    def subtotal_profit():
#        """Returns decimal profit of the product."""

#    def subtotal_price_with_currency():
#        """Returns subtotal price with currency."""

#    def subtotal_price_in_selected_currency_code():
#        """Returns decimal subtotal price of the product in selected currency code."""

#    def subtotal_vat_free_price_in_selected_currency_code():
#        """Returns decimal subtotal vat free price of the product in selected currency code."""

#    def subtotal_price_with_selected_currency_code():
#        """Returns subtotal price with selected currency code."""

#    def cart():
#        """Returns cart."""

#    def shop():
#        """Returns shop inside cart."""

#    def weight():
#        """Returns weight in kg for shipping cost calculation."""

#class ICustomerInfo(Interface):
#    country_code = Attribute('country_code')
