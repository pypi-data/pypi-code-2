"""This module contains much of the nuts and bolts for datats, but you shouldn't
need to manually use anything in here."""
from __future__ import absolute_import
import csv

try: # For DatatNamedRows. If OrderedDict is absent, order will be lost.
    from collections import OrderedDict
except:
    try:
        from ordereddict import OrderedDict
    except:
        OrderedDict = dict   # Fallback

try:     # We'll only offer translate_to_R if the module's there.
    from rpy2 import robjects
except ImportError:
    robjects = None
else:
    from . import rvectors

class ColumnsProxy(object):
    """The columns of a datat. This behaves somewhat like a Python dictionary.
    You should never need to use the class directly, it will be set up when you
    create a Datat.
    
    N.B. Dictionary-style methods .keys, .values and .items behave like Python 3
    dictionaries; they return generators, not lists."""
    def __init__(self, datat, names):
        self._datat = datat
        self.names = names
        
    def __getitem__(self, key):
        if key not in self.names:
            raise KeyError("No column called {0}".format(key))
        return [d[key] for d in self._datat]
        
    def keys(self):
        for name in self.names:
            yield name
    __iter__ = keys
            
    def values(self):
        for name in self.names:
            yield self[name]
            
    def items(self):
        for name in self.names:
            yield (name, self[name])
        
    def __contains__(self, key):
        return key in self.names
        
    def __repr__(self):
        return "Columns: " + repr(self.names)
        
    def __len__(self):
        return len(self.names)
        
    def __setitem__(self, name, newcol):
        """Add a new column, or replace an existing one. Any missing
        data will be filled in with None, but existing data will only
        be overwritten by values supplied."""
        if newcol and len(newcol) > len(self._datat):
            raise ValueError("Supplied column is too long.")
        if name not in self.names:
            self.names.append(name)
        for datum in self._datat:
            if newcol:
                datum[name] = newcol.pop(0)
            elif name not in datum:
                datum[name] = None
    
    def __delitem__(self, name):
        """Remove an entire column, including its data."""
        self.names.remove(name)
        for datum in self._datat:
            del datum[name]


class ColumnsProxy_NamedRows(ColumnsProxy):
    """The columns of a datat with named rows. This behaves somewhat like a
    Python dictionary. You should never need to use the class directly, it will
    be set up when you create a DatatNamedRows.
    
    N.B. Dictionary-style methods .keys, .values and .items behave like Python 3
    dictionaries; they return generators, not lists."""
    def __getitem__(self, key):
        if key not in self.names:
            raise KeyError("No column called {0}".format(key))
        return OrderedDict((n, d[key]) for n, d in self._datat.items())
        
    def __setitem__(self, name, newcol):
        """Add a new column, or replace an existing one. Any missing
        data will be filled in with None, but existing data will only
        be overwritten by values supplied."""
        if not newcol:
            newcol = {}
        if name not in self.names:
            self.names.append(name)
        for rowname, datum in self._datat.items():
            if rowname in newcol:
                datum[name] = newcol[rowname]
            elif name not in datum:
                datum[name] = None


class UnpackablesProxy(object):
    """Rows can be packed into, and unpacked from, the datat via this interface.
    The values should be in the order of the columns.
    mydatat.tuples.append((a, b, c))
    a,b,c = mydatat.tuples[3]
    
    (You shouldn't need to use the _UnpackablesProxy class directly.)"""
    def __init__(self, datat):
        self._datat = datat
        
    def _unpack(self, itemdict):
        """Utility method: turn a row dictionary into a tuple."""
        return tuple(itemdict[col] for col in self._datat.columns)
    
    def _pack(self, itemtuple):
        """Utility method: turn a row tuple into a dictionary."""
        return dict(zip(self._datat.columns.names, itemtuple))
        
    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._unpack(row) for row in self._datat[key]]
        return self._unpack(self._datat[key])        
    
    def append(self, newrow):
        """Add a tuple to the datat"""
        self._datat.append(self._pack(newrow))
        
    def __len__(self):
        return len(self._datat)
        
    def __iter__(self):
        for row in self._datat:
            yield self._unpack(row)
            
    def __repr__(self):
        replines = ["<Tuples of {0} rows of a Datat>".format(len(self._datat))]
        i = 1
        for row in self:
            replines.append(repr(row))
            i += 1
            if i > 10:
                break
        if len(self._datat) > 10:
            replines.append("...")
        return "\n".join(replines)


class UnpackablesProxy_NamedRows(UnpackablesProxy):
    """Rows can be packed into, and unpacked from, the DatatNamedRows using
    this interface. It behaves like a dictionary, except that looping over it
    will yield tuples like (rowname, (fieldA, fieldB, fieldC)). Use .values() to
    get just the row data, without the name.
    
    mydnr.tuples[rowkey] = a, b, c  # Set
    a, b, c = mydnr.tuples[rowkey]  # Retrieve"""
    __append__ = None
    def __setitem__(self, key, newrow):
        self._datat[key] = self._pack(newrow)
        
    def values(self):
        """Get rows without the row names"""
        for rname in self._datat:
            yield self._unpack(self._datat[rname])
            
    def items(self):
        for rname in self._datat:
            yield rname, self._unpack(self._datat[rname])
    __iter__ = items


class DatatBase(object):
    """Base class used by Datat and DatatNamedRows. You shouldn't need to use
    this directly."""
    def __init__(self, colnames):
        self.columns = ColumnsProxy(self, colnames)
        self.tuples = UnpackablesProxy(self)
        
    def blankdatum(self):
        """Get a dictionary with values set to None, which can be modified and
        appended to the Datat."""
        return dict(zip(self.columns.names, [None]*len(self.columns)))
        
    def save_csv(self, csvfile):
        """Saves the Datat to a CSV file, placing the headers in the first row.
        
        csvfile can be a file opened for writing, or the path to a file."""
        if not hasattr(csvfile, "write"):
            csvfile = open(csvfile, "w")
        writer = csv.writer(csvfile)
        writer.writerow(self.columns.names)
        for datum in self:
            writer.writerow([datum[col] for col in self.columns])
        csvfile.close()
        
    if robjects:
        def translate_to_R(self):
            """Turns the Datat into an R data.frame, using the rpy2 package.
            
            This method will only exist if rpy2 can be imported."""
            temp = {}
            for k, v in self.columns.items():
                col = rvectors.make_r_vector(v)
                temp[k] = col
            return robjects.DataFrame(temp)
