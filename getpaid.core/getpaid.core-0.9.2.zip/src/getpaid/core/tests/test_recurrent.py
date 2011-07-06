import unittest, datetime, doctest

from zope.app.testing import placelesssetup
from zope.testing.doctestunit import DocFileSuite
from zope import component

from getpaid.core.tests import base
from getpaid.core import order
from getpaid.core.interfaces import IOrderManager, workflow_states

class OrderQueryTests( base.GetPaidTestCase ):

    def setUp( self ):
        super( OrderQueryTests, self).setUp()
        self.orders = list( base.createRecurringOrders() )
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

    def testRenewalDateQuery( self ):
        self.orders[0].renewal_date = datetime.datetime.now() - datetime.timedelta( 30 )
        self.manager.storage.reindex( self.orders[0] )

        self.orders[1].renewal_date = datetime.datetime.now() - datetime.timedelta( 120 )
        self.manager.storage.reindex( self.orders[1] )

        # find already expired orders
        now = datetime.datetime.now()
        start_date = now - datetime.timedelta( 125 )
        end_date = now - datetime.timedelta( 7 )
        results = order.query.search( renewal_date = ( start_date, end_date ) )
        self.assertEqual( len(results), 2 )

    def testRenewalDateToday( self ):
        self.orders[0].renewal_date = datetime.datetime.now()
        self.manager.storage.reindex( self.orders[0] )

        # find already expired orders
        now = datetime.datetime.now()
        start_date = now - datetime.timedelta( 1 )
        end_date = now - datetime.timedelta( -1 )
        results = order.query.search( renewal_date = ( start_date, end_date ) )
        self.assertEqual( len(results), 1 )

        self.orders[2].renewal_date = datetime.datetime.now()
        self.manager.storage.reindex( self.orders[2] )

        results = order.query.search( renewal_date = ( start_date, end_date ) )
        self.assertEqual( len(results), 2 )

def test_suite():
    return unittest.TestSuite((
        # Unit tests
        DocFileSuite('../recurrent.txt',
                     setUp=base.coreSetUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        unittest.makeSuite( OrderQueryTests ),
        ))
