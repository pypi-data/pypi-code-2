#             Datat: Data tables for Python
#==============================================================================
# Copyright (c) 2010, Thomas Kluyver

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Datat: Data tables for Python

Thomas Kluyver, 2010. Available under the MIT license:
http://creativecommons.org/licenses/MIT/

To create a datat, use the Datat or DatatNamedRows classes. E.g.
mydatat = datat.Datat(["Column A", "Column B"])
mydatat.append({"Column A": 12, "Column B": "Tree"})

For more information, see the docstrings of those classes, or the online documentation:
"""
from __future__ import absolute_import
import csv
try:     # We'll only offer translate_to_R if the module's there.
    from rpy2 import robjects
except ImportError:
    robjects = None
else:
    from . import rvectors

try: # This is for DatatNamedRows. If OrderedDict is absent, order will be lost.
    from collections import OrderedDict
except:
    try:
        from ordereddict import OrderedDict
    except:
        OrderedDict = dict   # Fallback

class _ColumnsProxy(object):
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
        if newcol and len(newcol) > len(self.__datat):
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
            
class _ColumnsProxy_NamedRows(_ColumnsProxy):
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

class _DatatBase(object):
    """Base class used by Datat and DatatNamedRows. You shouldn't need to use
    this directly."""
    def __init__(self, colnames):
        self.columns = _ColumnsProxy(self, colnames)
        
    def blankdatum(self):
        """Get a dictionary with values set to None, which can be modified and
        appended to the Datat."""
        return dict(zip(self.columns.names, [None]*len(self.columns)))
        
    def unpackables(self):
        """Iterate over the rows, returning a list which can be unpacked into
        several variables for each row. The order of fields matches the column
        order.
        
        for name, age, handedness in peopledatat.unpackables():
            print("{0} is {1} years old".format(name, age))
        """
        for row in self:
            yield [row[colname] for colname in self.columns]
        
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
            temp= {}
            for k,v in self.columns.items():
                col = rvectors.R_vector(v)
                if hasattr(self, "keys"):  # Named rows
                    col.names = list(self.keys())
                temp[k] = col
            return robjects.DataFrame(temp)
            
class Datat(_DatatBase, list):
    """A data table. Instantiate with a list of column names.
    
    Looping over the Datat gives dictionaries mapping field names to values. If
    you prefer to unpack into variables, loop over .unpackables()."""
    __init__ = _DatatBase.__init__
    
    def __repr__(self):
        """Gives a table preview of the first 10 rows."""
        op = "<Datat: {0} records, in {1} columns>\n".format(len(self),\
        len(self.columns))
        op += "|".join(c[:8].rjust(8) for c in self.columns) + "\n"
        op += "+".join("-"*8 for c in self.columns) + "\n"
        for row in self[:10]:
            op += "|".join(str(row[field])[:8].rjust(8)\
            for field in self.columns) + "\n"
        if len(self) > 10:
            op += "..."
        return op
    
    def append(self, datum):
        """Add a datum (as a dict) to the Datat. Any missing fields will be set
        to None."""
        for name in self.columns:
            if name not in datum:
                datum[name] = None
        super(Datat, self).append(datum)
    
        
boolstrs = {"True":True,"False":False}
def _value_magic(rawrow):
    """Utility function: attempts to convert string values read from a CSV file
    to None, True, False, an int or float (or a str) as appropriate."""
    for thing in rawrow:
        thing = thing.strip()
        if not(thing):
            yield None
        elif thing in boolstrs:
            yield boolstrs[thing]
        elif thing.isdigit():
            yield int(thing)
        else:
            try:
                yield float(thing)
            except Exception:
                yield thing
        
def load_csv(csvfile, namescol=None):
    """Loads a Datat from a CSV file, using the first row as headers.
    
    csvfile can be a file object, or the path of a file.
    If namescol is set, the column with that name will be used as row names,
    and a DatatNamedRows will be returned."""
    if not hasattr(csvfile, "readline"):
        csvfile = open(csvfile)
    reader = csv.reader(csvfile)
    headers = [h.strip() for h in next(reader)]
    if namescol and namescol in headers:
        names_ix = headers.index(namescol)
        headers.pop(names_ix)
        datat = DatatNamedRows(headers, namescol)
        for row in reader:
            rowname = row.pop(names_ix)
            datat[rowname] = dict(zip(headers, _value_magic(row)))
    else:
        datat = Datat(headers)
        for row in reader:
            datat.append(dict(zip(headers, _value_magic(row))))
    csvfile.close()
    return datat
    
class DatatNamedRows(_DatatBase, OrderedDict):
    """A data table with rows by name instead of in a sequence. Instantiate by
    passing the column names, and optionally a name for the column containing
    row names (this can be set later as .namescol).
    
    Looping over a DatatNamedRows will give row names. You can use standard
    .items() and .values() methods for row names and content, or just the rows,
    respectively. To unpack row names and fields, use .unpackables().
    
    If OrderedDict is available (built in to Python 2.7/3.1 and later, or the
    ordereddict module from PyPI), rows will be kept in the order they were
    added. Otherwise, the order of rows will be ignored."""
       
    def __init__(self, colnames, namescol=None):
        self.namescol = namescol
        self.columns = _ColumnsProxy_NamedRows(self, colnames)
        OrderedDict.__init__(self)
        
    def __repr__(self):
        """Gives a table preview of the first 10 rows."""
        op = "<Datat (named rows): {0} records, in {1} columns>\n".format(len(self),\
        len(self.columns))
        colnames = [self.namescol or "(name)"] + self.columns.names
        op += "|".join(c[:8].rjust(8) for c in colnames) + "\n"
        op += "+".join("-"*8 for c in colnames) + "\n"
        for i, (rname, row) in enumerate(self.items()):
            op += str(rname)[:8].rjust(8) + ":"
            op += "|".join(str(row[field])[:8].rjust(8)\
            for field in self.columns) + "\n"
            if i >= 9:
                break
        if len(self) > 10:
            op += "..."
        return op
    
    def __setitem__(self, name, row):
        for field in self.columns:
            if field not in row:
                row[field] = None
        super(DatatNamedRows, self).__setitem__(name, row)
        
    def unpackables(self):
        """Loop over the rows, returning names and data to be unpacked:
        
        for rowname, (fieldA, fieldB, fieldC) in dnr.unpackables():
            print(rowname, fieldB)
        """
        for rname, row in self.items():
            yield (rname, [row[colname] for colname in self.columns])
            
    def save_csv(self, csvfile, namescol=None):
        """Saves the Datat to a CSV file, with the headers in the first row.
        
        csvfile can be a file opened for writing, or the path to a file."""
        if not hasattr(csvfile, "write"):
            csvfile = open(csvfile, "w")
        writer = csv.writer(csvfile)
        writer.writerow([self.namescol or '(name)'] + self.columns.names)
        for rowname, datum in self.items():
            writer.writerow([rowname] + [datum[col] for col in self.columns])
        csvfile.close()