from heapq import heappop, heapreplace, heapify
from itertools import imap, groupby
from operator import itemgetter

try:
    from heapq import merge
    
except ImportError:
    def merge(*iterables):
        '''Merge multiple sorted inputs into a single sorted output.
        
        Similar to `sorted(itertools.chain(*iterables))` but returns a generator,
        does not pull the data into memory all at once, and assumes that each of
        the input streams is already sorted (smallest to largest).
        
        >>> list(merge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
        [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]
        
        '''
        _heappop, _heapreplace, _StopIteration = (heappop, heapreplace,
                                                  StopIteration)
        
        h = []
        h_append = h.append
        for itnum, it in enumerate(map(iter, iterables)):
            try:
                next = it.next
                h_append([next(), itnum, next])
            except _StopIteration:
                pass
        heapify(h)
        
        while 1:
            try:
                while 1:
                    val, itnum, next = s = h[0] # raises IndexError when h
                                                # is empty
                    yield val
                    s[0] = next() # raises StopIteration when exhausted
                    _heapreplace(h, s)          # restore heap condition
            except _StopIteration:
                _heappop(h)                     # remove empty iterator
            except IndexError:
                return

def merge_iterators(iterators, key=None):
    ''' Merge multiple sorted inputs into a sorted output
    of grouped items according to key (while there is at least one of the
    iterators that still have values).
    
    Warning:
        - The iterators must be sorted by key
        - Only one item is supported by unique key in each iterator.
          If you have more, please do groupby on key
          and pass that item to the merge_iterators function.
        - Key should be a function: it will get applied on all iterator items
          to get the uniquelinking value.
        - To different key getter, set key as a list:
          one key per iterator, in the same order.
    
    >>> from pyf.dataflow.merging import merge_iterators
    >>> list(merge_iterators([xrange(4), xrange(1,5), [2,3]]))
    [(0, None, None), (1, 1, None), (2, 2, 2), (3, 3, 3), (None, 4, None)]
    '''
    itlen = len(iterators)

    def prepare_merging(iterable, pos):
        if key is None:
            for item in iterable:
                yield (item, pos, item)
        else:
            if isinstance(key, list) or isinstance(key, tuple):
                key_getter = key[pos]
            else:
                key_getter = key
            
            for item in iterable:
                yield (key_getter(item), pos, item)

    def untangle(values):
        items = [None] * itlen

        for k2, position, item in values:
            items[position] = item

        return tuple(items)

    merged = merge(*[prepare_merging(iterator, i)
                     for i,iterator in enumerate(iterators)])

    return imap(untangle,
                imap(itemgetter(1),
                     groupby(merged, key=itemgetter(0))))
