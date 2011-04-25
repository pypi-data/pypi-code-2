
class UInterval:
    def __init__(self, min, max=None):
        self.min = min
        self.max = max or min

    def __str__(self):
        s = "[%s" % self.min
        if self.min != self.max:
            s += ", %d" % self.max
        s += "]"
        return s

    def __cmp__(self, other):
        if other.min < self.min:
            return 1
        elif other.max > self.max:
            return -1
        else:
            # Other is entirely included in self
            return 0


class URange:
    def __init__(self):
        self.intervals = []

    def __str__(self):
        s = "["
        s += ", ".join([ str(i) for i in self.intervals ])
        s += "]"
        return s

    def _insert_at(self, pos, ui):
        self.intervals.insert(pos, ui)
        self._merge_intervals_at(pos)

    def _merge_intervals_at(self, pos):
        #
        # Merge as much as possible the intervals near to position <p>
        # Iterate because a merged interval can reveal a new possible merge
        #
        while True:
            m = self._merge_neighbours_at(pos)
            if not(m):
                break
            pos = self.intervals.index(m)

    def _merge_neighbours_at(self, pos):
        #print "end merge0", str(self)
        i = self.intervals[pos]
        m1, p1, m2, p2 = None, None, None, None

        # Try to merge to the right and to the left
        if pos > 0:
            p1 = pos-1
            m1 = self._try_merge(self.intervals[p1], i)
            #print "%s %s" % (i1, i), m1

        if pos < len(self.intervals)-1:
            p2 = pos+1
            m2 = self._try_merge(i, self.intervals[p2])
            #print "%s %s" % (i, i2), m2

        # Extend the merge if possible or select the available merge
        if m1 and m2:
            m = self._try_merge(m1, m2)
        else:
            m = m1 or m2

        # No merge possible with direct neighbours?
        if not(m):
            return

        # A merged interval replaces the original one
        self.intervals[pos] = m

        # Remove the intervals that are now merged
        if m2: del self.intervals[p2]
        if m1: del self.intervals[p1]
        #print "end merge1", str(self)
        return m

    def _try_merge(self, i1, i2):
        if i1.max >= i2.min -1:
            m = UInterval(min(i1.min,i2.min), max(i1.max,i2.max))
        else:
            m = None
        return m
    
    def add_char(self, char):
        ui = UInterval(char)
        self.add_interval(ui)

    def add_interval(self, interval):
        #char = interval.min

        for p in range(0, len(self.intervals)):
            i = self.intervals[p]
            if i == interval:
                print "ici"
                return
            if i > interval:
            #if interval < i:
                self._insert_at(p, interval)
                return
            else:
                continue
         
        # If we are here, a new interval must be appended
        self._insert_at(len(self.intervals), interval)

