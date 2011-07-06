import random, string, sys

from zope import interface
from zope.intid.interfaces import IIntIds

from getpaid.core import cart, order, payment, item, interfaces

class Product( object ):

    interface.implements( interfaces.IPayable )

class ProductGenerator( object ):

    _products = {}

    @classmethod
    def find( cls, uid ):
        return cls._products.get( uid )

    def __setitem__( self, k, v ):
        self._products[k] = v

    @classmethod
    def keys( self ):
        return self._products.keys()

    @property
    def uid( self ):
        while 1:
            uid = random.randint( 1, 1000 )
            if uid in self._products:
                continue
            break
        return str(uid)

    @property
    def supplier( self ):
        return unicode( random.choice( ['twax', 'bwax', 'cwax'] ) )

    @property
    def product_code( self ):
        return ''.join( random.sample( string.letters, 5 ) )
    
    @property
    def price( self ):
        return ( random.random()*10 )
    
    def new( self ):
        uid = self.uid
        p = Product()
        
        p.made_payable_by = self.supplier
        p.product_code = self.product_code
        p.price = self.price
        p.uid = uid
        self[ uid ] = p
        return p
    
class ProductIntId( object ):

    interface.implements( IIntIds )

    def queryId( self, ob ):
        return ob.uid
    
class Item( item.PayableShippableLineItem ):

    def resolve( self ):
        return ProductGenerator.find( self.uid )

class Mock( object ): pass

class OrderGenerator( object ):

    def __call__( self ):
        _order = order.Order()
        _order.billing_address = self.bill_address
        _order.shipping_address = self.ship_address
        _order.shopping_cart = self.shopping_cart
        _order.contact_information = self.contact_information
        _order.setOrderId( self.order_id )
        
        return _order

    @property
    def order_id( self ):
        return random.randint( 1, sys.maxint )

    @property
    def shopping_cart( self ):
        shopping_cart = cart.ShoppingCart()
        for i in range( random.randint( 2, 12 ) ):
            item = Item()
            item.uid = random.choice( ProductGenerator.keys() )
            item.quantity = random.randint( 1, 5 )

            if item.uid in shopping_cart:
                shopping_cart[ item.uid ].quantity += item.quantity
                continue
            
            item.name = random.choice( (u"Laser", u"Book", u"Rabbit", u"Snake", u"Lizard") )
            item.description = u''.join( random.sample( string.letters, 30) )
            item.weight = random.random()*3.0
            item.product_code = ''.join( random.sample( string.letters, 8) )
            item.cost = random.randint( 1, 100 )
            shopping_cart[ item.uid ] = item
        return shopping_cart
        
    @property
    def contact_information( self ):
        contact = payment.ContactInformation()
        first_name = random.choice( ("Mary", "Mike", "John", "Steve", "Elizabeth" ) )
        last_name  = random.choice( ("Smith", "Burton", "Appleseed", "Xavier" ) )
        phone  = ''.join( random.sample( string.digits, 9 ) )
        contact.name = u"%s %s"%( first_name, last_name )
        contact.phone = phone
        contact.marketing_preference = random.choice( (True, False ) )
        contact.email_html_format = random.choice( (True, False ) )
        return contact

    @property
    def zip( self ):
        return ''.join( random.sample( string.digits, 5 ) )

    @property
    def state( self ):
        return random.choice( ('US-NY', 'US-CA', 'US-VA', 'US-MA' ) )

    @property
    def city( self ):
        return random.choice( (u"York", u"Lancester", u"Shire", u"Burg" ) )
    
    @property
    def address_line( self ):
        numeral = ''.join( random.sample( string.digits, 3) )
        return u"%s Kittyhawk St"%numeral        

    @property
    def ship_address( self ):
        address = payment.ShippingAddress()
        address.ship_first_line  = self.address_line
        address.ship_city = self.city
        address.ship_state = self.state
        address.ship_country = "US"
        address.ship_postal_code = self.zip
        return address
    
    @property
    def bill_address( self ):
        address = payment.BillingAddress()
        address.bill_first_line  = self.address_line
        address.bill_city = self.city
        address.bill_state = self.state
        address.bill_country = "US"
        address.bill_postal_code = self.zip
        return address



def main():
    products = ProductGenerator()
    for i in range( random.randint(20,30) ):
        products.new()

    orders = OrderGenerator()
    orders = OrderGenerator()
    for i in range( 10 ):
        o = orders()
        print o, o.getSubTotalPrice(), len( o.shopping_cart), o.shopping_cart.size()

if __name__ == '__main__':
    main()
