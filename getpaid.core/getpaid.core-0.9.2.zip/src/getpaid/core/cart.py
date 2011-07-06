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
$Id: cart.py 3572 2010-05-13 05:59:41Z dglick $
"""

import decimal

from zope import component
from zope.interface import implements

from zope.app.container.ordered import OrderedContainer

from zope.annotation.interfaces import IAttributeAnnotatable

import interfaces

class ShoppingCart( OrderedContainer ):
    """
    A shopping cart
    """
    implements( interfaces.IShoppingCart, IAttributeAnnotatable )

    last_item = None
    
    def size( self ):
        return sum(i.quantity for i in self.values())
    
    def __setitem__( self, key, value ):
        if self.size() and interfaces.IRecurringLineItem.providedBy(value):
            msg = "Unable to add recurring item to cart with existing items."
            raise interfaces.AddRecurringItemException(msg)
            
        if self.is_recurring():
            msg = "Unable to add new item to cart with an existing recurring item."
            raise interfaces.RecurringCartItemAdditionException(msg)
        
        super(ShoppingCart, self).__setitem__( key, value)
        self.last_item = key
    
    def __delitem__( self, key ):
        if not key in self:
            return
        super( ShoppingCart, self).__delitem__( key )
        if self.last_item == key:
            if len(self)>0:
                self.last_item = self.keys()[-1]
            else:
                self.last_item = None
    
    def is_recurring(self):
        recurring = 0
        non_recurring = 0
        for i in self.values():
            if interfaces.IRecurringLineItem.providedBy(i):
                recurring += 1
            else:
                non_recurring += 1

        if recurring > 0 and non_recurring > 0:
            raise Exception('Carts containing both recurring and non-recurring items '
                            'are not supported.')
        elif recurring > 1:
            raise Exception('Carts containing multiple recurring items not supported.')
        elif recurring == 1:
            return True
        return False


class CartItemTotals( object ):

    implements( interfaces.ILineContainerTotals )
    
    def __init__( self, context ):
        self.shopping_cart = context

    def getTotalPrice( self ):
        if not self.shopping_cart:
            return 0
        
        total = 0
        total += float(self.getSubTotalPrice())
        total += float(self.getShippingCost())
        for tax in self.getTaxCost():
            total += tax['value']
        
        return float( str( total ) )            

    def getSubTotalPrice( self ):
        if not self.shopping_cart:
            return 0
        total = 0
        for item in self.shopping_cart.values():
            d = decimal.Decimal ( str(item.cost ) ) * item.quantity
            total += d        
        return total
        
    def getShippingCost( self ):
        if not interfaces.IShippableOrder.providedBy( self ):
            return 0
        return decimal.Decimal( str( self.shipping_cost ) )

    def getTaxCost( self ):
        """ get the list of dictionaries containing the tax info """
        tax_utility = component.getUtility( interfaces.ITaxUtility )
        return tax_utility.getTaxes( self )

