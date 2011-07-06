# Copyright (c) 2007 ifPeople, Kapil Thangavelu, and Contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
$Id: interfaces.py 3572 2010-05-13 05:59:41Z dglick $
"""

from zope.interface import Interface, Attribute, classImplements, implements
from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.app.container.interfaces import IContainer
from zope.schema.interfaces import ITextLine
from zope.schema.vocabulary import SimpleVocabulary
from fields import PhoneNumber, CreditCardNumber, weightValidator, emailValidator
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid')

#################################
# Exceptions
class AddRecurringItemException(Exception):
    pass

class RecurringCartItemAdditionException(Exception):
    pass

#################################
# Where to Buy Stuff

class IStore( Interface ):
    """ represents a getpaid installation, should be a local site w/ getpaid local components installed
    """

class IPersistentOptions( Interface ):
    """
    a base interface that our persistent option annotation settings,
    can adapt to. specific schemas that want to have context stored
    annotation values should subclass from this interface, so they
    use adapation to get access to persistent settings. for example,
    settings = IMySettings(context)
    """

class IStoreSettings( IPersistentOptions ):
    """ minimum configuration schema for a store, pgp product has examples of many more.
    
    TODO: there some duplication here between PGP interfaces for store configuration and the ones here.
    the ones here are for usage without plone... ie z3 unit tests, and z3 stores. ideally the ones
    in pgp would be derived from these.. which needs parallel work to fix up translations.
    """
    
    shipping_method = schema.Choice( title = _(u"Shipping Method"),
                                    description = _(u"Select a method to calculate shipping charges for orders in your store."),
                                     required = True,
                                     source = "getpaid.shipping_methods" )

    store_name = schema.TextLine( title = _(u"Store/Organization Name"),
                                  required = True,
                                  default = u"" )

    contact_name = schema.TextLine( title = _(u"Contact Name"),
                                    required = False,
                                    default = u"" )
                                    

    contact_email = schema.TextLine( title = _(u"Contact Email"),
                                  required = False,
                                  default = u""
                                )
                                
    contact_company = schema.TextLine( title = _(u"Contact Company"),
                              required = False,
                              default = u""
                            )

    contact_address = schema.TextLine( title = _(u"Contact Address"),
                                       required = False,
                                       default = u""
                                     )
                                
    contact_address2 = schema.TextLine( title = _(u"Contact Address2"),
                                        required = False,
                                        default = u""
                                      )

    contact_city = schema.TextLine( title = _(u"Contact City"),
                                    required = False,
                                    default = u""
                                  )

    contact_country = schema.Choice( title = _(u"Contact Country"),
                                     required = False,
                                     vocabulary = "getpaid.countries"
                                   )

    contact_state = schema.Choice( title = _(u"Contact State/Province"),
                                   required = False,
                                   vocabulary = "getpaid.states"
                                 )

    contact_postalcode = schema.TextLine( title = _(u"Contact Zip/Postal Code"),
                                          required = False,
                                          default = u""
                                        )

    contact_phone = PhoneNumber( title = _(u"Contact Phone"),
                                 description = _(u"Only digits allowed"),
                                     required = False,
                                     default = u""
                                   )

    contact_fax = schema.TextLine( title = _(u"Contact Fax"),
                                   required = False,
                                   default = u""
                                 )

    tax_ein = schema.TextLine( title= _(u"Tax Identification Number"),
                               required = False,
                               default=u"")


#################################
# Plugin Management

class IPluginManager( Interface ):
    """
    a lifecycle manager for a single plugin
    """
    
    title = schema.TextLine(title=_(u"Title"))
    description = schema.TextLine(title=_(u"Description"))  
    
    def install( ):
        """install the plugin"""
        
    def uninstall( remove_data=False ):
        """ 
        uninstall the plugin, if remove data is true, the plugin
        should remove its persistent state.
        """
        
    def status():
        """ return true if installed, else false """

class IStoreInstalledEvent( IObjectEvent ):
    """ object event for store installation, and plugin installation """
    
class StoreInstalled( ObjectEvent ):
    implements( IStoreInstalledEvent )
    
class IStoreUninstallEvent( IObjectEvent ):
    """ object event for store uninstallation, and plugin removal """
    
class StoreUninstalled( ObjectEvent ):
    implements( IStoreUninstallEvent )

class IFormSchemas(Interface):
    """
    Utility for getting hold of the form schemas for a particular
    section. Any schema interface with fields that an implementor
    may want to chang should be given a section here rather than
    drectly using a hard-coded interface all over the place.
    """

    def getInterface(section):
        """
        Return the schema interface for the section specified.
        """

    def getPersistentBagClass(section):
        """
        Return the subclass of options.PersistentBag to use
        for storing field information for the specified section.
        """

#################################
# Stuff To Buy

class IPayable( Interface ):
    """
    An object which can be paid for. Payables are typically gotten via adapation between
    a context and the request, to allow for pricing / display customization on a user
    basis.
    """

    made_payable_by = schema.TextLine(
        title = _(u"Made Payable By"),
        readonly = True,
        required = False
        )

    product_code = schema.TextLine( title = _(u"Product Code"),
                        description=_(u"An organization's unique product identifier (not required since shopping cart uses content UID internally)"),
                        required=False
                        )
    price = schema.Float( title = _(u"Price"), required=True)

class IDonationContent( IPayable ):
    """ Donation
    """
    donation_text = schema.TextLine( title = _(u"Donation Description"),
                        description=_(u"Very brief 50 character text (that shows up in portlet)"),
                        required=True,
                        max_length=50)

class IVariableAmountDonationContent( IPayable ):
    """ Variable Amount Donation
    """
    donation_text = schema.TextLine( title = _(u"Donation Description"),
                        description=_(u"Very brief 50 character text (that shows up in portlet)"),
                        required=True,
                        max_length=50)
    price = schema.Float( title = _(u"Price"), required=False)

class ISubscription( IPayable ):
    """ Subscription
    """

class IBuyableContent( IPayable ):
    """ Purchasable Content Delivered Virtually
    """

class IPremiumContent( IPayable ):
    """ Premium Content for Subscriptions
    """

class IPhysicalPayable( IPayable ):
    """
    """


UNIT_POUNDS = _(u"lbs")
UNIT_KILOGRAMS = _(u"kgs")

class IShippableContent( IPayable ):
    """ Shippable Content
    """
    dimensions = schema.TextLine( title = _(u"Dimensions"))
    sku = schema.TextLine( title = _(u"Product SKU"))

    # default unit is country of origin specific... 
    weight = schema.Float( title = _(u"Shipping Weight"),
                           constraint=weightValidator,
                           description = _(u"Enter a weight, only two decimal places are supported. The unit is specified in the field below."))
                           
    weight_unit = schema.Choice( title=_(u"Weight Unit"), values=[ UNIT_POUNDS, UNIT_KILOGRAMS ],description = _(u"Please select the unit in which you specified the shipment weight.") )
    
    def getShipWeight( self ):
        """ Shipping Weight
        """

class IRecurringPaymentContent( IPayable ):
    """ Recurring Payable Content
    """
    interval = schema.TextLine( title = _(u"Interval"),
                                 description = _(u"Number of months between payments.  Use the value 1 for monthly payments, 12 for yearly payments, 3 for quarterly payments, or any other interval.") )
    total_occurrences = schema.TextLine( title = _(u"Total Occurrences"),
                                         description = _(u"The subscription will end after this many payments.") )

#################################
# Events

class IPayableCreationEvent( IObjectEvent ):
    """ sent out when a payable is created
    """

    payable = Attribute("object implementing payable interface")
    payable_interface = Attribute("payable interface the object implements")

class IPayableAuditLog( Interface ):
    """ ordered container of changes, most recent first, hook on events.
    """


#################################
# Stuff to Process Payments

class IPaymentProcessor( Interface ):
    """ A Payment Processor

    a processor can keep processor specific information on an orders
    annotations.
    """

    def authorize( order, payment_information ):
        """
        authorize an order, using payment information.
        """

    def capture( order, amount ):
        """
        capture amount from order.
        """

    def refund( order, amount ):
        """
        reset
        """

class IRecurringPaymentProcessor( IPaymentProcessor ):
    """ a payment processor that can handle recurring line items
    """

class IPaymentProcessorOptions( Interface ):
    """ Options for a Processor

    """

class IWorkflowPaymentProcessorIntegration( Interface ):
    """
    integrates an order's workflow with a payment processor
    """

    def __call__( order_workflow_event ):
        """
        process a workflow event
        """

#################################
# Info needed for payment processing


class ILineItem( Interface ):
    """
    An Item in a Cart
    """
    item_id = schema.TextLine( title = _(u"Unique Item Id"))
    name = schema.TextLine(title = _(u"Name"))
    description = schema.TextLine( title = _(u"Description"))
    cost = schema.Float( title = _(u"Cost"))
    quantity = schema.Int( title = _(u"Quantity"))
    product_code = schema.TextLine( title = _(u"Product Code"))


class ILineItemFactory( Interface ):
    """ encapsulation of creating and adding a line item to a line item container
    from a payable. sort of like an adding view
    """

    def create( payable ):
        """
        create a payable from a line item
        """

class ILineItemContainer( IContainer ):
    """ A container for line items
    """

class ILineContainerTotals( Interface ):
    # interface for getting prices for a collection of items (aka an order),
    # mostly encapsulation, of other components

    def getTotalPrice( ):
        """
        return the total price of all line items in the container
        """

    def getShippingCost( ):
        """
        return total estimated shipping cost for the items in the container.
        """

    def getTaxCost( ):
        """
        return list of dictionaries for each tax cost for the items in the container
        """

    def getSubTotalPrice( ):
        """
        get the price of all the items in the contaners
        """

class IPayableLineItem( ILineItem ):
    """
    A line item linked to a payable
    """

    uid = schema.ASCIILine( title = _(u"Integer Id for a Product") )

    def resolve( ):
        """ return the payable object, or None if can't be found.
        """

class IShippableLineItem( ILineItem ):
    """
    a line item that can be shipped
    """
    #implements( interfaces.IShippableLineItem )
    weight = schema.Float( title = _(u'Weight of Packaged Item'),
                           required = True,
                           )
    #um_weight = 
    #um_distance = ""
    length = schema.Float( title=_(u"Length"))
    height = schema.Float( title=_(u"Height"))
    width = schema.Float( title=_(u"Width"))    
        
class IRecurringLineItem( IPayableLineItem ):

    interval = schema.Int( title = _(u"Period as a timedelta"))
    total_occurrences = schema.Int( title = _(u"Occurrences"))


class IGiftCertificate( ILineItem ):
    """ A Gift Certificate
    """

#################################
# Shopping Cart Stuff

class IShoppingCartUtility( Interface ):

    def get( context, create=False, key=None ):
        """
        Return the user's shopping cart or none if not found. If
        create is passed then create a new one if one isn't found. If
        key is passed then return the cart corresponding to that key
        independent of the current user.
        """

    def destroy( context, key=None ):
        """
        Remove the current user's cart from the session if it exists.
        If key is passed then remove the cart corresponding to that
        key independent of the current user.
        """

    def getKey( context ):
        """
        Return a key for the shopping cart of the current user
        including anonymous users. This key can then be used to
        retrieve or destroy the cart at a later point. This is to
        support handling of notification callbacks with async
        processors.
        """

class IShoppingCart( ILineItemContainer ):
    """ A Shopping Cart
    """
    def size( ):
        """
        Count the number of items in the cart (*not* the number of line
        items)
        """
        
#################################
# Shipping

class IShipmentContainer(  IContainer ):
    """ a container for shipments
    """

class IShipment( ILineItemContainer ):
    """ a (partial|complete) shipment of ishippable line items of an order
    """
    tracking_code = schema.TextLine( description=_(u"Tracking Number") )
    service_code = schema.ASCIILine( description=_(u"Service Code (2 Letter)"))
    service = schema.TextLine( description=_(u"Service Name"))
    shipping_cost = schema.Float( description=_(u"Cost of Delivery") )
    creation_date = schema.Datetime( description=_(u"Creation Date") )

class IShippingMethod( Interface ):

    def getCost( order ):
        """ get the shipping cost for an order...
        """

class IShippingRateService( Interface ):
    """ utility """

    def getRates( order ):
        """ return shipping rate options for an order.  this should return:
        - a list of IShippingMethodRate as 'shipments'
        - an error string as 'error'
        """

    def getMethodName( method_id ):
        """
        given a shipping method service code, returns a shipping method label/name
        """

    def getTrackingUrl( track_number ):
        """
        given a track number this should return, if available for this service
        a url that can be used to track the shipment
        """

class IShippingMethodRate( Interface ):
    """
     Service Code: UPS Next Day Air
     Shipment unit of measurement: LBS
     Shipment weight: 3.0
     Currency Code: USD
     Total Charge: 58.97
     Days to Delivery: 1
     Delivery Time: 10:30 A.M.
    """
    # may need to find a way to make this general
    service_code = schema.ASCIILine( description=_(u"Service Code (2 Letter)"))
    service = schema.TextLine( description=_(u"Service Name"))

    currency = schema.ASCII( description=_(u"Currency Denomination Code"))
    cost = schema.Float( description=_(u"Cost of Delivery"))

    # really shouldn't show these, as they ignore store processing time
    # days_to_delivery = schema.Int( description=_(u"Estimated Days to Deliver") )
    # delivery_time = schema.TextLine( description=_(u"Estimated Delivery Time") )

class IShippingMethodSettings( Interface ):
    """ Options for a Shipping Method
    """

#################################
# Tax Utility

class ITaxUtility( Interface ):

    def getTaxes( order ):
	 	""" return a list dictionaries of each ITax inside that applies to
	 		the order
		"""


#################################
# Payment Information Details
class IAbstractAddress( Interface ):
    """ base/common interface for all addresses"""
    
class IAddress( IAbstractAddress ):
    """ a physical address
    """
    first_line = schema.TextLine( title = _(u"Address 1"), description=_(u"Please Enter Your Address"))
    second_line = schema.TextLine( title = _(u"Address 2"), required=False )
    city = schema.TextLine( title = _(u"City") )
    country = schema.Choice( title = _(u"Country"),
                               vocabulary = "getpaid.countries")
    state = schema.Choice( title = _(u"State"),
                             vocabulary="getpaid.states")
    postal_code = schema.TextLine( title = _(u"Zip/Postal Code"))

class IShippingAddress( IAbstractAddress ):
    """ where to send goods
    """
    ship_same_billing = schema.Bool( title = _(u"Same as billing address"), required=False)
    ship_name = schema.TextLine( title = _(u"Full Name"), required=False)
    ship_organization = schema.TextLine( title = _(u"Organization/Company"), required=False)
    ship_first_line = schema.TextLine( title = _(u"Address 1"), required=False)
    ship_second_line = schema.TextLine( title = _(u"Address 2"), required=False)
    ship_city = schema.TextLine( title = _(u"City"), required=False)
    ship_country = schema.Choice( title = _(u"Country"),
                                    vocabulary = "getpaid.countries", required=False)
    ship_state = schema.Choice( title = _(u"State"),
                                  vocabulary="getpaid.states", required=False)
    ship_postal_code = schema.TextLine( title = _(u"Zip/Postal Code"), required=False)

class IBillingAddress( IAbstractAddress ):
    """ where to bill
    """
    bill_name = schema.TextLine( title = _(u"Full Name"))
    bill_organization = schema.TextLine( title = _(u"Organization/Company"), required=False)
    bill_first_line = schema.TextLine( title = _(u"Address 1"))
    bill_second_line = schema.TextLine( title = _(u"Address 2"), required=False )
    bill_city = schema.TextLine( title = _(u"City") )
    bill_country = schema.Choice( title = _(u"Country"),
                                    vocabulary = "getpaid.countries")
    bill_state = schema.Choice( title = _(u"State"),
                                  vocabulary="getpaid.states" )
    bill_postal_code = schema.TextLine( title = _(u"Zip/Postal Code"))

MarketingPreferenceVocabulary = SimpleVocabulary(
                                   map(SimpleVocabulary.createTerm,
                                       ( (True, "Yes", _(u"Yes")), (False, "No", _(u"No") ) )
                                       )
                                )

EmailFormatPreferenceVocabulary = SimpleVocabulary(
                                   map( lambda x: SimpleVocabulary.createTerm(*x),
                                       ( (True, "Yes", _(u"HTML")), (False, "No", _(u"Plain Text") ) )
                                       )
                                  )


class IUserContactInformation( Interface ):
    """docstring for IUserContactInformation"""

    name = schema.TextLine( title = _(u"Your Name"))

    phone_number = PhoneNumber( title = _(u"Phone Number"),
                                description = _(u"Only digits allowed - e.g. 3334445555 and not 333-444-5555 "))

    email = schema.TextLine(
                        title=_(u"Email"),
                        description = _(u"Contact Information"),
                        constraint = emailValidator
                        )

    marketing_preference = schema.Bool(
                                        title=_(u"Can we contact you with offers?"), 
                                        required=False,
                                        ) 
    
    email_html_format = schema.Choice( 
                                        title=_(u"Email Format"), 
                                        description=_(u"Would you prefer to receive rich html emails or only plain text"),
                                        vocabulary = EmailFormatPreferenceVocabulary,
                                        default = True,
                                        )


class IUserPaymentInformation( Interface ):
    """ A User's payment information to be optionally collected by the
    payment processor view.
    """

    name_on_card = schema.TextLine( title = _(u"Card Holder Name"),
                                description = _(u"Enter the full name, as it appears on the card. "))

    bill_phone_number = PhoneNumber( title = _(u"Phone Number"),
                                description = _(u"Only digits allowed - e.g. 3334445555 and not 333-444-5555 "))

    # DONT STORED PERSISTENTLY
    credit_card_type = schema.Choice( title = _(u"Credit Card Type"),
                                      source = "getpaid.core.accepted_credit_card_types",)

    credit_card = CreditCardNumber( title = _(u"Credit Card Number"),
                                    description = _(u"Only digits allowed - e.g. 4444555566667777 and not 4444-5555-6666-7777 "))

    cc_expiration = schema.Date( title = _(u"Credit Card Expiration Date"),
                                    description = _(u"Select month and year"))

    cc_cvc = schema.TextLine(title = _(u"Credit Card Verfication Number", default=u"Credit Card Verification Number"),
                             description = _(u"For MC, Visa, and DC, this is a 3-digit number on back of the card.  For AmEx, this is a 4-digit code on front of card. "),
                             min_length = 3,
                             max_length = 4)

#################################
#
class IProductCatalog( Interface ):

    def query( **kw ):
        """ query products """
    def __setitem__( product_id, product ):
        """ """
#################################
# Orders

class IOrderManager( Interface ):
    """ persistent utility for storage and query of orders
    """

    def query( **kw ):
        """ query the orders, XXX extract order query interface
        """

    def get( order_id ):
        """ retrieve an order
        """

    def reindex( order ):
        """ reindex a modified order
        """
# future interface
#    def __setitem__( order_id, order ):
#               """ save an order
#        """

    def store( order ):
         """ save an order
         """
class IDefaultFinanceWorkflow( Interface ):
    """ marker interface for workflow / processor integration on the default ootb workflow """

class IOrder( Interface ):
    """ captures information, and is a container to multiple workflows
    """
    user_id = schema.ASCIILine( title = _(u"Customer Id"), readonly=True )
    shipping_address = schema.Object( IShippingAddress, required=False)
    billing_address  = schema.Object( IBillingAddress )
    # only shown on anonymous checkouts?
    contact_information = schema.Object( IUserContactInformation, required=False )
    shopping_cart = schema.Object( IShoppingCart )
    finance_state = schema.TextLine( title = _(u"Finance State"), readonly=True)
    fulfillment_state = schema.TextLine( title = _(u"Fulfillment State"), readonly=True)
    processor_order_id = schema.ASCIILine( title = _(u"Processor Order Id") )
    processor_id = schema.ASCIILine( readonly=True )

# Various Order Classification Markers..

class IShippableOrder( IOrder ):
    """ marker interface for orders which need shipping """
    
    shipping_service = schema.ASCIILine( title = _(u"Shipping Service"))
    shipping_method = schema.ASCIILine( title = _(u"Shipping Method") )
    shipping_price = schema.ASCIILine( title = _(u"Shipping Price") )

    shipments = schema.Object( IShipmentContainer )
    

class IOriginRouter( Interface ):
    
    def getOrigin( ):
        """
        determine the origin shipping point for an order..
        
        return an IContactInfo and IAddress object to serve as the origin
        of the order for any fufillment process (shipping, processing).
        """    
        
class IRecurringOrder( IOrder ):
    """ marker interface for orders containing recurring line items """

class IVirtualOrder( IOrder ):
    """ marker inteface for orders which are delivered virtually """

class IDonationOrder( IOrder ):
    """ marker interface for orders which contain donations"""

class IOrderSetReport( Interface ):
    """ store adapters that can serialize a set of orders into a report"""

    title = schema.TextLine()
    mime_type = schema.ASCIILine()

    def __call__( orders ):
        """
        return a rendered report string from the given ordrs
        """

class IOrderWorkflowLog( Interface ):
    """ an event log based history of an order's workflow
    """
    def __iter__( ):
        """ iterate through records of the order's history, latest to oldest.
        """

    def last( ):
        """ get the last change to the order
        """

class IOrderWorkflowEntry( Interface ):
    """ a record describing a change in an order's workflow history
    """
    changed_by = schema.ASCIILine( title = _(u"Changed By"), readonly = True )
    change_date = schema.Date( title = _(u"Change Date"), readonly = True)
    change_kind = schema.TextLine( title=_(u"Change Kind"), readonly=True)
    comment = schema.ASCIILine( title = _(u"Comment"), readonly = True, required=False )
    new_state = schema.ASCIILine( title = _(u"New State"), readonly = True)
    previous_state = schema.ASCIILine( title = _(u"Previous State"), readonly = True )
    transition = schema.ASCIILine( title = u"", readonly = True)
    # change type?? (workflow, user


class IPhoneNumber(ITextLine):
    """A Text line field that handles phone number input."""
    
classImplements(PhoneNumber,IPhoneNumber)


class ICreditCardNumber(ITextLine):
    """A Text line field that handles credit card input."""
classImplements(CreditCardNumber,ICreditCardNumber)

class ICreditCardTypeEnumerator(Interface):
    """Responsible for listing credit card types. """

    def acceptedCreditCardTypes(self):
        """ Lists the accepted credit card types. """

    def allCreditCardTypes(self):
        """ List all credit card types. """

class keys:
    """ public annotation keys and static variables
    """

    # how much of the order have we charged
    capture_amount= 'getpaid.capture_amount'

    # processor specific txn id for an order
    processor_txn_id = 'getpaid.processor.uid'

    # name of processor adapter
    processor_name = 'getpaid.processor.name'

    # sucessful call to a processor
    results_success = 1
    results_async = 2

class workflow_states:

    class order:
        # order workflows are executed in parallel

        class finance:
            # name of parallel workflow
            name = "order.finance"

            REVIEWING = 'REVIEWING'
            CHARGEABLE = 'CHARGEABLE'
            CHARGING = 'CHARGING'
            CHARGED = 'CHARGED'
            REFUNDED = 'REFUNDED'
            PAYMENT_DECLINED = 'PAYMENT_DECLINED'
            CANCELLED = 'CANCELLED'
            CANCELLED_BY_PROCESSOR = 'CANCELLED_BY_PROCESSOR'

        class fulfillment:
            # name of parallel workflow
            name = "order.fulfillment"

            NEW = 'NEW'
            PROCESSING = 'PROCESSING'
            DELIVERED = 'DELIVERED'
            WILL_NOT_DELIVER = 'WILL_NOT_DELIVER'

    class shippable_order:
          
        class fulfillment:
            # name of parallel workflow
            name = "order.fulfillment"

            NEW = 'NEW'
            PROCESSING = 'PROCESSING'
            #This is actually The same as delivered for order,
            DELIVERED = 'SHIPPED'
            WILL_NOT_DELIVER = 'WILL_NOT_DELIVER'


            
    class item:
        NEW = 'NEW'
        PROCESSING = 'PROCESSING'
        DELIVER_VIRTUAL = 'DELIVERVIRTUAL'
        CANCELLED = 'CANCELLED'
        SHIPPED = 'SHIPPED'
        #RETURNING = 'RETURNING'
        #RETURNED = 'RETURNED'
        REFUNDING = 'REFUNDING'
        REFUNDED = 'REFUNDED'

    class shipment:
        NEW = 'NEW'
        CHARGING = 'CHARGING'
        DECLINED = 'DECLINED'
        DELIVERED = 'DELIVERED'
        SHIPPED = 'SHIPPED'
        SHIPPABLE = 'SHIPPABLE'
        CHARGED = 'CHARGED'
