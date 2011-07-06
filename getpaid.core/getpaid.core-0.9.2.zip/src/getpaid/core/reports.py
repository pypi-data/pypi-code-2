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



from zope import interface

import csv, StringIO
import interfaces


def getOrderCreationDate( order ):
    pass
    
def getOrderTotalPrice( order ):
    return order.getTotalPrice()

class Attribute( object ):    
    def __init__(self, name):
        self.name = name
    def __call__( self, order ):
        return getattr( order, self.name, '')
    
def defaults( field_accessor_map, field_order ):
    for fn in field_order:
        if fn not in field_accessor_map:
            field_accessor_map[fn]=Attribute(fn)
    
class AttributeCSVSetReport( object ):

    interface.implements( interfaces.IOrderSetReport )
    
    mime_type = 'text/csv'

    # the order fields appear in a csv report
    field_order = ["order_id", "user_id", "finance_state", "fulfillment_state", "price", "creation_date"]
    
    field_title_map = dict(
        order_id = "Order Id",
        user_id = "Customer Id",
        finance_state = "Status",
        fulfillment_state = "Fulfillment",
        creation_date = "Created",
        price = "Price"
        )

    field_accessor_map = dict( 
        creation_date = getOrderCreationDate,
        price = getOrderTotalPrice
        )
        
    defaults( field_accessor_map, field_order )
    
    def __init__( self, context ):
        self.context = context
        
    def sortOrders( self, orders ):
        return orders

    def writeRows( self, writer, orders ):
        field_getters = []
        for field_name in self.field_order:
            field_getters.append( self.field_accessor_map.get( field_name ) )
            
        for order in orders:
            writer.writerow( [getter( order ) for getter in field_getters ] )
                
    def __call__( self, orders ):
        
        orders = self.sortOrders( orders )
        
        io = StringIO.StringIO()
        writer = csv.writer( io )
        writer.writerow( [ self.field_title_map.get( field_name, field_name) \
                           for field_name in self.field_order ] )
        self.writeRows( self, writer, orders )

        return io.getvalue()

class InventoryCSVReport( AttributeCSVSetReport ):

    field_order = ["product_id", "title", "quantity", "average_unit_price", "price"]
    
    field_accessor_map = dict(
      product_id = lambda x: x['product_id'],
      title = lambda x: x['title'],
      quantity = lambda x: x['quantity'],
      average_unit_price = lambda x: x['price']/float(x['quantity']),
      price = lambda x: x['price']
    )
    
    def sortOrders( self, orders ):
        items = {}
        for o in orders:
            for i in o.shopping_cart.values():
                item_info = items.get( i.item_id )
                if item_info is None:
                    items[ i.item_id ] = item_info = dict( product_id = i.item_id, title = i.title, quantity=0, price=0)
                item_info[ 'quantity'] += i.quantity
                item_info[ 'price' ] += i.quantity * i.price
            
        product_ids = items.keys()
        product_ids.sort()
        return [ items[product_id] for product_id in product_ids ]
    

class FulfillmentCSVReport( AttributeCSVSetReport ):
    
    # the order fields appear in a csv report
    field_order = ["order_id", "name", 'phone', 'email', 'title', 'quantity', 'price']
    
    field_title_map = t = dict( AttributeCSVSetReport.field_title_map )

    field_title_map = dict(
        order_id = "Order Id",
        user_id = "Customer Id",
        finance_state = "Status",
        fulfillment_state = "Fulfillment",
        creation_date = "Created",
        price = "Price"
        )

    field_accessor_map = dict( 
        creation_date = getOrderCreationDate,
        price = getOrderTotalPrice
        )
        
