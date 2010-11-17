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

For more information, see the docstrings of those classes, or the online
documentation:
http://packages.python.org/Datat/
"""
from __future__ import absolute_import
import csv
from . import _base
robjects = _base.robjects
OrderedDict = _base.OrderedDict

            
class Datat(_base.DatatBase, list):
    """A data table. Instantiate with a list of column names.
    
    Looping over the Datat gives dictionaries mapping field names to values. If
    you prefer to unpack into variables, loop over .tuples"""
    def __repr__(self):
        """Gives a table preview of the first 10 rows."""
        op = "<Datat: {0} records, in {1} columns>\n".format(len(self),\
        len(self.columns))
        op += "|".join(c[:8].rjust(8) for c in self.columns) + "\n"
        op += "+".join("-"*8 for c in self.columns) + "\n"
        for row in self.tuples[:10]:
            op += "|".join(str(field)[:8].rjust(8) for field in row) + "\n"
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
        
    def filter(self, *conditions, **kwconditions):
        """Returns a new dataset containing only rows with specific values.
        Use keyword arguments to specify values for each column, or conditions
        as strings for more complex queries.
        
        augbdays = birthdays.filter(Month="August")
        cars.filter("MPG > 30", Model="Ford")
        """
        conditions = [compile(c, "<string>", "eval") for c in conditions]
        newdatat = Datat(self.columns.names)
        for row in self:
            try:
                if all(row[k] == v for k, v in kwconditions.items()) and\
                   all(eval(c, row) for c in conditions):
                    newdatat.append(row)
            except Exception:
                pass
        return newdatat


class DatatNamedRows(_base.DatatBase, OrderedDict):
    """A data table with rows by name instead of in a sequence. Instantiate by
    passing the column names, and optionally a name for the column containing
    row names (this can be set later as .namescol).
    
    Looping over a DatatNamedRows will give row names. You can use standard
    .items() and .values() methods for row names and content, or just the rows,
    respectively. To unpack row names and fields, use .tuples.
    
    If OrderedDict is available (built in to Python 2.7/3.1 and later, or the
    ordereddict module from PyPI), rows will be kept in the order they were
    added. Otherwise, the order of rows will be ignored."""
       
    def __init__(self, colnames, namescol=None):
        self.namescol = namescol
        self.columns = _base.ColumnsProxy_NamedRows(self, colnames)
        self.tuples = _base.UnpackablesProxy_NamedRows(self)
        OrderedDict.__init__(self)
        
    def __repr__(self):
        """Gives a table preview of the first 10 rows."""
        op = "<Datat (named rows): {0} records, in {1} columns>\n"\
               .format(len(self), len(self.columns))
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
        
    def filter(self, *conditions, **kwconditions):
        """Returns a new dataset containing only rows with specific values.
        Use keyword arguments to specify values for each column, or conditions
        as strings for more complex queries.
        
        metalsdatat.filter("Melting_pt > 400")
        apples.filter(Category="Cooker")
        """
        conditions = [compile(c, "<string>", "eval") for c in conditions]
        newdatat = DatatNamedRows(self.columns.names, self.namescol)
        for rname, row in self.items():
            try:
                if all(row[k] == v for k, v in kwconditions.items()) and\
                   all(eval(c, row) for c in conditions):
                    newdatat[rname] = row
            except Exception:
                pass
        return newdatat
            
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
