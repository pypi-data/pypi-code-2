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

import unittest, datetime, doctest

from getpaid.core.tests import base
from getpaid.core import order
from getpaid.core.interfaces import IOrderManager, IOrderWorkflowLog, IOrder, workflow_states

from zope.app.testing import placelesssetup, ztapi
from zope.testing.doctestunit import DocFileSuite

from zope import component 

class OrderLogTests( base.GetPaidTestCase ):
    
    def setUp( self ):
        super(OrderLogTests, self).setUp()
        
    def testLog( self ):
        self.orders = list( base.createOrders() )
        order1 = self.orders[0]
        order1.finance_workflow.fireTransition('create')

        olog = IOrderWorkflowLog( order1 )
        history = list( iter( olog ) )
        self.assertEqual( len( history ), 1 )
        entry = history[0]
        self.assertEqual( entry.transition, u'Create')
        self.assertEqual( entry.new_state, workflow_states.order.finance.REVIEWING)
    
class OrderQueryTests( base.GetPaidTestCase ):

    def setUp( self ):
        super( OrderQueryTests, self).setUp()        
        self.orders = list( base.createOrders() )
        self.manager = component.getUtility( IOrderManager )
        
    def tearDown( self ):
        super( OrderQueryTests, self).tearDown()
        self.orders = None
        self.manager = None
        
    def testDateQuery( self ):
        self.orders[0].creation_date = datetime.datetime.now() - datetime.timedelta( 30 )
        self.manager.storage.reindex( self.orders[0] )
        
        self.orders[1].creation_date = datetime.datetime.now() - datetime.timedelta( 120 )
        self.manager.storage.reindex( self.orders[1] )

        # find orders in the last week
        results = order.query.search( creation_date = datetime.timedelta(7)  )
        self.assertEqual( len(results), 7 )
        
        now = datetime.datetime.now()
        start_date = now - datetime.timedelta( 125 )
        end_date = now - datetime.timedelta( 7 )
        results = order.query.search( creation_date = ( start_date, end_date ) )
        self.assertEqual( len(results), 2 )

        
    def testStateQuery( self ):
        self.orders[0].finance_workflow.fireTransition('create')
        self.orders[0].finance_workflow.fireTransition('authorize')

        self.manager.storage.reindex( self.orders[0] )        

        self.orders[1].finance_workflow.fireTransition('create')        
        self.orders[1].finance_workflow.fireTransition('authorize')
        self.orders[1].finance_workflow.fireTransition('cancel-chargeable')        
        self.manager.storage.reindex( self.orders[1] )

        self.orders[2].finance_workflow.fireTransition('create')        
        self.orders[2].finance_workflow.fireTransition('authorize')
        self.orders[2].finance_workflow.fireTransition('charge-chargeable') 
        self.manager.storage.reindex( self.orders[2] )
        
        self.assertEqual( len( order.query.search( finance_state = workflow_states.order.finance.CHARGEABLE ) ), 1 )
        self.assertEqual( len( order.query.search( finance_state = workflow_states.order.finance.CANCELLED ) ), 1 )
        self.assertEqual( len( order.query.search( finance_state = workflow_states.order.finance.CHARGING ) ), 1 )                

    def testCombinedQuery( self ):
        self.orders[0].finance_workflow.fireTransition('create')
        self.orders[0].finance_workflow.fireTransition('authorize')
        self.orders[0].creation_date = created = datetime.datetime.now() - datetime.timedelta( 30 )
        self.manager.storage.reindex( self.orders[0] )
        self.assertEqual( len( order.query.search( finance_state = workflow_states.order.finance.CHARGEABLE,
                                                   creation_date = ( created - datetime.timedelta(1),
                                                                     created + datetime.timedelta(1) )
                                                   )),
                          1
                          )
                          
def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../order.txt',
                     setUp=base.coreSetUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),    
        DocFileSuite('../options.txt',
                     setUp=base.coreSetUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),    
        unittest.makeSuite( OrderQueryTests ),
        unittest.makeSuite( OrderLogTests ),        
        ))                          
