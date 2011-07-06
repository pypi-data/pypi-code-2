import unittest

from zope import component

from getpaid.core.tests import base
from getpaid.core import cart, item
from getpaid.core.interfaces import \
    IOrderManager, \
    AddRecurringItemException, \
    RecurringCartItemAdditionException


class CartPolicyTests(base.GetPaidTestCase):
    def setUp(self):
        super(CartPolicyTests, self).setUp()
        self.cart = cart.ShoppingCart()
        self.nonrecurring = item.LineItem()
        self.nonrecurring.name = "Non-recurring"
        self.nonrecurring.quantity = 1
        self.nonrecurring.cost = 25
        self.nonrecurring.item_id = "nonrecurring"
        self.recurring = item.RecurringLineItem()
        self.recurring.name = "Recurring"
        self.recurring.quantity = 1
        self.recurring.cost = 25
        self.recurring.item_id = "recurring"
        self.manager = component.getUtility(IOrderManager)
        
    def tearDown(self):
        super(CartPolicyTests, self).tearDown()
        self.recurring = None
        self.nonrecurring = None
        self.manager = None
        
    def testNoAddRecurringToPopulatedCart(self):
        self.cart[self.nonrecurring.item_id] = self.nonrecurring
        self.assertRaises(AddRecurringItemException, 
                          self.cart.__setitem__, 
                          self.recurring.item_id,
                          self.recurring)
    
    def testNoAddRecurringToPopulatedRecurringCart(self):
        self.cart[self.recurring.item_id] = self.recurring
        recurring2 = item.RecurringLineItem()
        recurring2.name = "Recurring 2"
        recurring2.quantity = 1
        recurring2.cost = 25
        recurring2.item_id = "recurring2"
        self.assertRaises(AddRecurringItemException, 
                          self.cart.__setitem__, 
                          recurring2.item_id,
                          recurring2)                          
    
    def testCanAddMultipleNonRecurring(self):
        self.cart[self.nonrecurring.item_id] = self.nonrecurring
        nonrecurring2 = item.LineItem()
        nonrecurring2.name = "Non Recurring 2"
        nonrecurring2.quantity = 1
        nonrecurring2.cost = 25
        nonrecurring2.item_id = "nonrecurring2"
        # This should not raise an InvalidCartException
        self.cart[nonrecurring2.item_id] = nonrecurring2
    
    def testNoAddNonRecurringToRecurringCart(self):
        self.cart[self.recurring.item_id] = self.recurring
        self.assertRaises(RecurringCartItemAdditionException, 
                          self.cart.__setitem__, 
                          self.nonrecurring.item_id,
                          self.nonrecurring)
    

def test_suite():
    return unittest.TestSuite((
        # Unit tests
        unittest.makeSuite(CartPolicyTests),
        ))
