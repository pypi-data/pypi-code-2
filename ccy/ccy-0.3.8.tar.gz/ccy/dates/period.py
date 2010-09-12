
__all__ = ['period','Period']


def period(pstr):
    '''Create a period object from a period string'''
    return Period().add_tenure(pstr)



def find_first_of(st, possible):
    possible = tuple(possible)
    lowi = -1
    for p in possible:
        i = st.find(p)
        if i != -1 and (i < lowi or lowi == -1):
            lowi = i
    return lowi


def safediv(x,d):
    if x < 0:
        return -(-x/d)
    else:
        return x/d
    
def safemod(x,d):
    if x < 0:
        return -(-x%d)
    else:
        return x%d

class Period(object):
    
    def __init__(self, months = 0, days = 0):
        self._months = months
        self._days = days
    
    def isempty(self):
        return self.months == 0 and self.days == 0
    
    def add_days(self, days):
        self._days += days
        
    def add_weeks(self, weeks):
        self._days += 7*weeks
    
    def add_months(self, months):
        self._months += months
    
    def add_years(self, years):
        self._months  += 12*years
    
    @property
    def years(self):
        return safediv(self._months,12)
    
    @property
    def months(self):
        return safemod(self._months,12)
    
    @property
    def weeks(self):
        return safediv(self._days,7)
    
    @property
    def days(self):
        return safemod(self._days,7)
    
    @property
    def totaldays(self):
        return 30*self._months + self._days
        
    def __repr__(self):
        '''The period string'''
        p = ''
        y = self.years
        m = self.months
        w = self.weeks
        d = self.days
        if y:
            p = '%sY' % y
        if m:
            p = '%s%sM' % (p,m)
        if w:
            p = '%s%sW' % (p,w)
        if d:
            p = '%s%sD' % (p,d)
        return p
    
    def __str__(self):
        return self.__repr__()
        
    def add_tenure(self, pstr):
        if isinstance(pstr,self.__class__):
            self._months += pstr._months
            self._days += pstr._days
            return self
        st   = str(pstr).upper()
        done = False
        while not done:
            if not st:
                done = True
            else:
                ip = find_first_of(st,'DWMY')
                if ip == -1:
                    raise ValueError("Unknown period %s" % pstr)
                p = st[ip]
                v = int(st[:ip])
                if p == 'D':
                    self.add_days(v)
                elif p == 'W':
                    self.add_weeks(v)
                elif p == 'M':
                    self.add_months(v)
                elif p == 'Y':
                    self.add_years(v)
                st = st[ip+1:]
        return self
    
    def __add__(self, other):
        return Period(self._months+other._months,
                      self._days+other._days)
    
    def __sub__(self, other):
        return Period(self._months-other._months,
                      self._days-other._days)
        
    def __gt__(self, other):
        return self.totaldays > other.totaldays
    
    def __lt__(self, other):
        return self.totaldays < other.totaldays
    
    def __ge__(self, other):
        return self.totaldays >= other.totaldays
    
    def __le__(self, other):
        return self.totaldays <= other.totaldays
    
    def __eq__(self, other):
        return self.totaldays == other.totaldays
    