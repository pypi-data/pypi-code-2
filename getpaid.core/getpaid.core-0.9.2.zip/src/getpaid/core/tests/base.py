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

"""Doc test runner
"""

__docformat__ = "reStructuredText"

import unittest
from zope.app.testing import placelesssetup, ztapi

from zope.annotation import interfaces as annotation_interfaces
from zope.annotation import attribute

from hurry.workflow import interfaces

import random, string

from zope import component
from zope import interface

from getpaid.core.interfaces import IOrder, IOrderManager, IOrderWorkflowLog
from getpaid.core import order, cart, item as line_item
from getpaid.core.workflow import store, order as oworkflow

class GetPaidTestCase( unittest.TestCase ):

    def setUp( self ):
        coreSetUp( )
        super(GetPaidTestCase, self).setUp()

    def tearDown( self ):
        placelesssetup.tearDown()

def createOrders( how_many=10 ):
    manager = component.getUtility( IOrderManager )

    for i in range(1, how_many):
        o = order.Order()
        o.order_id = str(i)

        o.shopping_cart = sc = cart.ShoppingCart()

        for i in range(0, 10):
            item = line_item.LineItem()
            item.name = "p%s"%random.choice( string.letters )
            item.quantity = random.randint(1,25)
            item.cost = random.randint(30, 100)
            item.item_id = "i%s"%random.choice( string.letters )
            if item.item_id in sc:
                continue
            sc[item.item_id] = item

        o.user_id = "u%s"%random.choice( string.letters )
        #o.finance_workflow.fireTransition('create')
        #o.fulfillment_workflow.fireTransition('create')

        manager.store( o )

        yield o

def createRecurringOrders( how_many=10 ):
    """
    Create some orders with recurring payable content...
    """
    manager = component.getUtility( IOrderManager )

    for i in range(1, how_many):
        o = order.Order()
        o.order_id = str(i)

        o.shopping_cart = sc = cart.ShoppingCart()

        item = line_item.RecurringLineItem()
        item.name = "p%s"%random.choice( string.letters )
        item.quantity = random.randint(1,25)
        item.cost = random.randint(30, 100)
        item.item_id = "%s"%random.choice( string.letters )
        if item.item_id in sc:
            continue
        sc[item.item_id] = item

        o.user_id = "u%s"%random.choice( string.letters )

        manager.store( o )
        from getpaid.core.interfaces import IRecurringOrder
        interface.directlyProvides(o, IRecurringOrder)

        yield o

def coreSetUp( test=None ):
    placelesssetup.setUp()

    ###########################
    # order workflow
    ztapi.provideAdapter( IOrder,
                          interfaces.IWorkflowState,
                          oworkflow.FinanceState,
                          'order.finance')

    ztapi.provideAdapter( IOrder,
                          interfaces.IWorkflowState,
                          oworkflow.FulfillmentState,
                          'order.fulfillment')

    ztapi.provideAdapter( IOrder,
                          interfaces.IWorkflowInfo,
                          oworkflow.FinanceInfo,
                          'order.finance')

    ztapi.provideAdapter( IOrder,
                     interfaces.IWorkflowInfo,
                     oworkflow.FulfillmentInfo,
                    'order.fulfillment')

    ztapi.provideAdapter(annotation_interfaces.IAttributeAnnotatable,
                         annotation_interfaces.IAnnotations,
                         attribute.AttributeAnnotations)

    ztapi.provideUtility(interfaces.IWorkflow,
                         oworkflow.FulfillmentWorkflow(),
                        'order.fulfillment')

    ztapi.provideUtility(interfaces.IWorkflow,
                        oworkflow.FinanceWorkflow(),
                        'order.finance')

    ztapi.provideUtility(interfaces.IWorkflowVersions,
                         store.StoreVersions())

    ztapi.provideUtility( IOrderManager, order.OrderManager() )

    ztapi.provideAdapter( IOrder, IOrderWorkflowLog, order.OrderWorkflowLog )

    ztapi.subscribe( (IOrder, interfaces.IWorkflowTransitionEvent),
                       None,
                       order.recordOrderWorkflow )

    ######################
    # product catalog

