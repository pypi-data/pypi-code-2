import re

import sqlalchemy

class Container(object):
    """
    a container for other object that allows iteration and dict-like access
    """
    def __init__(self, cdict=None):
        """
        cdict may be a dictionary that will be used to initialize the Container
        """
        self._attrs = []
        self._n = 0
        if cdict:
            for key, value in cdict.iteritems():
                self.add_element(key, value)

    def add_element(self, key, value):
        setattr(self, key, value)
        if not key in self._attrs:
            self._attrs += [key]

    def keys(self):
        return self._attrs

    def __contains__(self, key):
        return key in self._attrs
 
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        return self.add_element(key, value)
    
    def __iter__(self):
        self._n = 0
        return self

    def next(self):
        """return the next item in the data set or raise StopIteration"""

        try:
            r = getattr(self, self._attrs[self._n])
            self._n += 1
        except:
            self._n = 0
            raise StopIteration
      
        return r

    def __repr__(self):
        return "%s" % self._attrs

    def keys(self):
        return self._attrs

    def get(self, key, default=None):
        return getattr(self, key, default)


def check_sqlalchemy_version(req):
    """
    It only works if pkg_resources is present
    """
    SA_VER = sqlalchemy.__version__

    def fatal_exit():
        import sys
        msg = "Sqlkit requires at least version %s, found %s"
        print msg % (req, SA_VER)
        sys.exit(1)

    def warning():
        import warnings
        msg = ("You have %s version of sqlalchemy. Sqlkit is tested with " +
              "version newer that %s. You shouldn't have problems " +
              "but we're not sure" )
        warnings.warn(msg % (SA_VER, req))
    
    try:
        from pkg_resources import parse_version as pv
        if pv(sqlalchemy.__version__) >= pv(req):
            return  
        elif pv(sqlalchemy.__version__) < pv('0.5'):
            return fatal_exit()
        else:
            warning()
    except ImportError, e:
        ## don't quit just becouse they don't have pkg_resources
        return True


def str2list(list_or_string):
    """
    input parsing common func
    """
    
    if isinstance(list_or_string, basestring):
        return re.split('[ ,]*', list_or_string)
    return list_or_string or []



if __name__ == '__main__' :

    c = Container()
    c.add_element('uno', 1)
    print c.keys()
    print 'uno' in c
    c['due'] = 2
    c['tre'] = 3
    c['quattro'] = 4
    print c.due
    for x in c:
        if x>2:
            break
        print x
        
    for x in c:
        print x

    print str2list('uno,due, tre')
    print str2list(['uno','due', 'tre'])
    
