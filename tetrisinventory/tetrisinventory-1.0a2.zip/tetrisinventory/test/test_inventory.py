import unittest
from itertools import product, repeat

from tetrisinventory import (
    Inventory,
    InventoryItemDoesntFitError,
    InventoryItemNotFound,
    InventoryDuplicateItemError,
    InvalidInventoryItemError)

class AbstractInventoryTest(unittest.TestCase):
    skip = True
    __test__ = False
    
    def setUp(self):
        self.small_inventory = Inventory(set(product(range(2), repeat=2)))
        self.large_inventory = Inventory(set(product(range(3), repeat=2)))
        
        class vbar(object):
            slots = frozenset(zip(repeat(0), range(3)))
        
        class hbar(object):
            slots = frozenset(zip(range(3), repeat(0)))
        
        class dot(object):
            slots = frozenset([(0,0)])
        
        self.vbar = vbar
        self.hbar = hbar
        self.dot = dot
    
    def assertCanFill(self, adder):
        dots = [self.dot() for _ in xrange(4)]
        for i, j in product(range(2), repeat=2):
            self.assert_(self.small_inventory.can_insert(self.dot(), (i, j)))
        
        for dot, (i, j) in zip(dots, product(range(2), repeat=2)):
            adder(dot, (i, j))
        
        for i, j in product(range(2), repeat=2):
            self.assertFalse(self.small_inventory.can_insert(self.dot(), (i, j)))
        
        return dots # hack for test_multipleXRemove
    
    def assertMultipleXRemove(self, x):
        dots = x()
        for dot in dots:
            self.small_inventory.remove(dot)
        x()
    
    # common tests
    def test_offsetCalculator(self):
        # todo: more complete tests of offset stuff
        class zerocalc(object):
            def __init__(self, inventory):
                self.inventory = inventory
            
            def transform(self, slots, offset):
                return set([0 for slot in slots])
            
            def candidate_offsets(self, slots, item):
                # just pick one so we have a starting point, and brute-force it
                needed_slot = next(iter(item.slots))
                for k, v in slots.iteritems():
                    if v is None:
                        yield k
        
        d1 = self.dot()
        d2 = self.dot()
        
        inv = Inventory(set([0]), zerocalc)
        
        self.assert_(inv.can_insert(d1, 1))
        inv.insert(d1, 1)
        self.assertEqual(inv[0], d1)
        self.assertFalse(inv.can_insert(d2, 20))
        inv.remove(d1)
        self.assert_(inv.can_insert(d1, 1))

class TestBasicInventory(AbstractInventoryTest):
    __test__ = True
    def test_removeFromEmpty(self):
        self.assertRaises(InventoryItemNotFound,
            self.small_inventory.remove, self.dot())

class TestInventoryCollisions(AbstractInventoryTest):
    __test__ = True
    # successes - no collisions
    def test_emptyNoCollide(self):
        self.assertEqual(
            self.small_inventory.collisions(self.dot(), (0, 0)),
            set())
    
    def test_noCollide(self):
        self.small_inventory.insert(self.dot(), (0, 0))
        self.assertEqual(
            self.small_inventory.collisions(self.dot(),(0, 1)),
            set())
    
    # successes - collisions
    def test_oneCollision(self):
        self.small_inventory.insert(self.dot(), (0, 0))
        self.assertEqual(
            self.small_inventory.collisions(self.dot(),(0, 0)),
            set([(0, 0)]))
    
    def test_twoIndependentCollisions(self):
        self.large_inventory.insert(self.dot(), (0, 0))
        self.large_inventory.insert(self.dot(), (0, 1))
        self.assertEqual(
            self.large_inventory.collisions(self.vbar(), (0, 0)),
            set([(0, 0), (0, 1)]))
    
    def test_twoCollisionsSameObject(self):
        very_large_inventory = Inventory(set(product(range(4), repeat=2)))
        
        very_large_inventory.insert(self.vbar(), (0, 0))
        self.assertEqual(
            very_large_inventory.collisions(self.vbar(), (0, 1)),
            set([(0, 1), (0, 2)]))
    
    def test_oneCollisionWithOutside(self):
        """test against collisions with space outside the inventory"""
        self.assertEqual(
            self.small_inventory.collisions(self.dot(), (-1, 0)),
            set([(-1, 0)]))
    
    def test_twoCollisionsWithOutside(self):
        self.assertEqual(
            self.small_inventory.collisions(self.hbar(), (-2, 0)),
            set([(-2, 0), (-1, 0)]))

class TestInventoryInsert(AbstractInventoryTest):
    __test__ = True
    # failures    
    def test_outsideInventory(self):
        self.assertFalse(self.small_inventory.can_insert(self.dot(), (-1, -1)))
    
    def test_intersectsOutsideInventory(self):
        self.assertFalse(self.large_inventory.can_insert(self.hbar(), (-1, 1)))
    
    def test_completeOverlap(self):
        self.small_inventory.insert(self.dot(), (0,0))
        self.assertFalse(self.small_inventory.can_insert(self.dot(), (0,0)))
    
    def test_partialOverlap(self):
        self.large_inventory.insert(self.hbar(), (0, 1))
        self.assertFalse(self.large_inventory.can_insert(self.vbar(), (1, 0)))
    
    def test_duplicate(self):
        # inventory is like a set.
        dot = self.dot()
        self.small_inventory.insert(dot, (0, 0))
        self.assertRaises(InventoryDuplicateItemError,
            self.small_inventory.insert, dot, (1, 0))
    
    def test_removeNonexistent(self):
        dot1 = self.dot()
        dot2 = self.dot()
        self.small_inventory.insert(dot1, (0, 0))
        self.assertRaises(InventoryItemNotFound,
            self.small_inventory.remove, dot2)
    
    # successes
    def test_simpleInsert(self):
        self.assert_(self.small_inventory.can_insert(self.dot(), (0, 0)))
        self.small_inventory.insert(self.dot(), (0, 0))
    
    def test_insertRemove(self):
        d1 = self.dot()
        self.small_inventory.insert(d1, (0, 0))
        self.small_inventory.remove(d1)
        
        self.assert_(self.small_inventory.can_insert(self.dot(), (0, 0)))
    
    def test_insertOffsetRemove(self):
        d1 = self.dot()
        self.small_inventory.insert(d1, (1, 0))
        self.small_inventory.remove(d1)
        
        self.assert_(self.small_inventory.can_insert(self.dot(), (1, 0)))
    
    def test_fillInsert(self):
        return self.assertCanFill(self.small_inventory.insert)
    
    def test_multipleInsertRemove(self):
        self.assertMultipleXRemove(self.test_fillInsert)

class TestInventoryAdd(AbstractInventoryTest):
    __test__ = True
    #successes
    def test_addTooSmall(self):
        self.assertRaises(InventoryItemDoesntFitError,
            self.small_inventory.add, self.hbar())
    
    def test_addOverCrowded(self):
        self.large_inventory.add(self.vbar())
        self.assertRaises(InventoryItemDoesntFitError,
            self.small_inventory.add, self.hbar())
    
    def test_addFull(self):
        self.test_fillAdd()
        self.assertRaises(InventoryItemDoesntFitError,
            self.small_inventory.add, self.dot())
    
    def test_addDuplicate(self):
        bar = self.vbar()
        self.large_inventory.add(bar)
        self.assertRaises(InventoryDuplicateItemError,
            self.large_inventory.add, bar)
    
    def test_addDuplicateToFull(self):
        dots = self.test_fillAdd()
        self.assertRaises(InventoryDuplicateItemError,
            self.small_inventory.add, dots[0])
    
    # failures
    def test_simpleAdd(self):
        self.small_inventory.add(self.dot())
    
    def test_addRemove(self):
        d1 = self.dot()
        self.small_inventory.add(d1)
        self.small_inventory.remove(d1)
        
        for pos in self.small_inventory.available_slots:
            self.assert_(self.small_inventory.can_insert(self.dot(), pos))
    
    def test_fillAdd(self):
        return self.assertCanFill(lambda item, *args: self.small_inventory.add(item))
    
    def test_multipleAddRemove(self):
        self.assertMultipleXRemove(self.test_fillAdd)

class TestInventoryShiftedAdd(TestInventoryAdd):
    __test__ = True
    def setUp(self):
        super(TestInventoryShiftedAdd, self).setUp()
        
        class vbar(object):
            slots = frozenset(zip(repeat(0), range(1, 4)))
        
        class hbar(object):
            slots = frozenset(zip(range(1, 4), repeat(0)))
        
        class dot(object):
            slots = frozenset([(1,0)])
        
        self.vbar = vbar
        self.hbar = hbar
        self.dot = dot
    
    def assertCanFill(self, adder):
        dots = [self.dot() for _ in xrange(4)]
        for i, j in product(range(-1, 1), range(2)):
            self.assert_(self.small_inventory.can_insert(self.dot(), (i, j)))
        
        for dot, (i, j) in zip(dots, product(range(2), repeat=2)):
            adder(dot, (i, j))
        
        for i, j in product(range(-1, 1), range(2)):
            self.assertFalse(self.small_inventory.can_insert(self.dot(), (i, j)))
        
        return dots # hack for test_multipleXRemove
    
    def test_addRemove(self):
        d1 = self.dot()
        self.small_inventory.add(d1)
        self.small_inventory.remove(d1)
        
        for (a, b) in self.small_inventory.available_slots:
            self.assert_(
                self.small_inventory.can_insert(self.dot(), (a-1, b)))

class TestInventorySubscript(AbstractInventoryTest):
    __test__ = True
    def test_subscriptSimple(self):
        d1 = self.dot()
        d2 = self.dot()
        bar = self.hbar()
        inv = self.large_inventory
        inv.insert(d1, (0, 0))
        inv.insert(d2, (1, 0))
        inv.insert(bar, (0, 1))
        
        self.assertEqual(inv[0, 0], d1)
        self.assertEqual(inv[1, 0], d2)
        self.assertEqual(inv[0, 1], bar)
        self.assertEqual(inv[1, 1], bar)
        self.assertEqual(inv[2, 1], bar)
        
        self.assertRaises(LookupError, lambda: inv[0, 2])
        self.assertRaises(LookupError, lambda: inv[1, 2])
        self.assertRaises(LookupError, lambda: inv[2, 2])
        self.assertRaises(LookupError, lambda: inv[2, 0])
    
    def test_subscriptNonSlot(self):
        self.assertRaises(LookupError, lambda: self.small_inventory[-1, -1])

class TestNullItemInventory(unittest.TestCase):
    __test__ = True
    def setUp(self):
        class item(object):
            slots = frozenset([])
        
        self.item = item
        self.small_inventory = Inventory(set(product(range(2), repeat=2)))
    
    def test_canCollideNull(self):
        self.assertRaises(InvalidInventoryItemError,
            self.small_inventory.collisions, self.item, (0, 0))
    
    def test_canInsertNull(self):
        self.assertRaises(InvalidInventoryItemError,
            self.small_inventory.can_insert, self.item, (0, 0))
    
    def test_addNull(self):
        self.assertRaises(InvalidInventoryItemError,
            self.small_inventory.add, self.item)
    
    def test_insertNull(self):
        self.assertRaises(InvalidInventoryItemError,
            self.small_inventory.insert, self.item, (0, 0))


if __name__ == '__main__':
    unittest.main()
