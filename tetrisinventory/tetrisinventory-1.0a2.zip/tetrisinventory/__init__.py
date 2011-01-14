from tetrisinventory.compat import izip_longest

def builder(constructor):
    """Create a container using a generator.
    
    The constructor is called with the return value of the decorated function.
        
        >>> from itertools import izip_longest
        >>> @builder(tuple)
        ... def ndim_sub(v1, v2):
        ...     for a, b in izip_longest(v1, v2, fillvalue=0):
        ...         yield a - b
        ...
        >>> ndim_sub((0, 1), (1, 2, 3)) == (-1, -1, -3)
        True
        
    Non-generator return values can be used as well, of course::
        
        >>> from itertools import chain
        >>> s = builder(set)(chain)(["ab"], "cd")
        >>> s == set(['ab', 'c', 'd'])
        True
    
    """
    # should really get added to the builtins
    def decorator(f):
        def g(*args, **kwargs):
            return constructor(f(*args, **kwargs))
        
        return g
    return decorator

@builder(tuple)
def nsub(v1, v2):
    for a, b in izip_longest(v1, v2, fillvalue=0):
        yield a - b

class NDimensionalOffsetController(object):
    def __init__(self, inventory):
        self.inventory = inventory
    
    @builder(set)
    def transform(self, slots, offset):
        for pos in slots:
            new_slot = list(pos)
            for i, delta in enumerate(offset):
                new_slot[i] += delta
            
            yield tuple(new_slot)
    
    def candidate_offsets(self, slots, item):
        # just pick one so we have a starting point, and brute-force it
        needed_slot = next(iter(item.slots))
        for k, v in sorted(slots.iteritems(), key=lambda (k, v): k[::-1]):
            if v is None:
                yield nsub(k, needed_slot)

    
class InventoryItemDoesntFitError(ValueError):
    pass

class InventoryItemNotFound(ValueError):
    pass

class InventoryDuplicateItemError(ValueError):
    pass

class InvalidInventoryItemError(TypeError):
    pass

def adds_item(f):
    def g(self, item, *args, **kwargs):
        if not item.slots:
            raise InvalidInventoryItemError(item)
        return f(self, item, *args, **kwargs)
    
    return g

class Inventory(object):
    """Implements a Diablo-style 'Tetris Inventory' of unique items
    
    An item is not permitted to be added to an inventory more than once.
    Semantically, inventories are sets, although with additional constraints
    formed by the concept of item tiles/"slots".
    
    """
    def __init__(self, available_slots,
            offset_controller=NDimensionalOffsetController):
        """Create inventory space with `available_slots` as the available slots
        
        May optionally pass an alternate offset controller. The default
        calculator does n-dimensional translation and offset generation.
        
        """
        self.available_slots = dict.fromkeys(available_slots)
        self.items = {}
        self.offset_controller = offset_controller(self)
    
    def _can_insert(self, slots):
        """Internal insert check using slots instead of items+offsets."""
        return not self._collisions(slots)
    
    def _collisions(self, slots):
        """Internal collisions lister using slots instead of items+offsets."""
        return slots - set(
            k for k, v in self.available_slots.iteritems() if v is None)
    
    @adds_item
    def collisions(self, item, offset):
        return self._collisions(
            self.offset_controller.transform(item.slots, offset))
    
    def can_insert(self, item, offset):
        """Check whether an item can be added at a given offset
        
        will probably be removed later, as .collisions(item, offset) is more
        general.
        
        """
        return not self.collisions(item, offset)
    
    @adds_item
    def insert(self, item, offset):
        if item in self.items:
            raise InventoryDuplicateItemError(item)
        
        offset_slots = self.offset_controller.transform(item.slots, offset)
        if not self._can_insert(offset_slots):
            raise InventoryItemDoesntFitError(item)
        
        self.available_slots.update(dict.fromkeys(offset_slots, item))
        self.items[item] = offset
    
    @adds_item
    def add(self, item):
        candidates = self.offset_controller.candidate_offsets(
            self.available_slots, item)
        for offset in candidates:
            try:
                self.insert(item, offset)
            except InventoryItemDoesntFitError:
                continue
            else:
                return offset
        else:
            if item in self.items:
                raise InventoryDuplicateItemError(item)
            raise InventoryItemDoesntFitError(item)
    
    def remove(self, item):
        try:
            offset = self.items.pop(item)
        except KeyError:
            raise InventoryItemNotFound(item)
        
        self.available_slots.update(dict.fromkeys(
            self.offset_controller.transform(item.slots, offset)))
        
        return offset
    
    def __getitem__(self, pos):
        """get the item taking up slot ``pos``.
        
        If no item is taking up this slot, KeyError is raised
        
        """
        item = self.available_slots[pos]
        if item is None:
            raise KeyError(pos)
        else:
            return item
