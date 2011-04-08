#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import os.path
from TableData import TableData
from pyutilib.component.core import alias
from decimal import Decimal


# format=
# using=
# query=
# user=
# password=
# table=

class db_Table(TableData):

    def __init__(self):
        TableData.__init__(self)


    def open(self):
        if self.filename is None:
            raise IOError, "No data source name was specified"
        if self.filename[0] == '"':
            self.filename = self.filename[1:-1]
        #
        # Initialize self.db
        #
        self.db = None
        if self._data is not None:
            self.db = self._data
        else:
            try:
                self.db = self.connect(self.filename, self.options)
            except Exception:
                raise

    def read(self):
        #
        # Get the table from the database
        #
        if self.db is None:
            return
        cursor = self.db.cursor()
        tmp = []
        if self.options.query is None:
            if self.options.table is None:
                raise IOError, "Must specify 'query' or 'table' option!"
            self.options.query = '"SELECT * FROM %s"' % self.options.table
        if not self.options.table is None:
            for row in cursor.columns(table=self.options.table):
                tmp.append(row.column_name)
            tmp=[tmp]
        else:
            # TODO: extend this logic to create a header row for a SQL query
            pass
        #print "DATA start",self.options.query
        cursor.execute(self.options.query[1:-1])
        for row in cursor:
            #print "DATA",list(row)
            ttmp=[]
            for data in list(row):
                if isinstance(data,Decimal):
                    ttmp.append(float(data))
                elif data is None:
                    ttmp.append('.')
                else:
                    ttmp.append(data)
            tmp.append(ttmp)
        #print 'FINAL',tmp
        #
        # Process data from the table
        #
        if type(tmp) in (int,long,float):
            if not self.options.param is None:
                self._info = ["param",self.options.param,":=",tmp]
            elif len(self.options.symbol_map) == 1:
                self._info = ["param",self.options.symbol_map[self.options.symbol_map.keys()[0]],":=",tmp]
            else:
                raise IOError, "Data looks like a parameter, but multiple parameter names have been specified: %s" % str(self.options.symbol_map)
        elif len(tmp) == 0:
            raise IOError, "Empty range '%s'" % self.options.range
        else:
            self._set_data(tmp[0], tmp[1:])
        return True

    def close(self):
        if self._data is None and not self.db is None:
            del self.db

    def connect(self, connection, options, kwds={}):
        try:
            mod = __import__(options.using)
            args = [connection]
            if not options.user is None:
                args.append(options.user)
            if not options.password is None:
                args.append(options.password)
            #print "XXX",args,self.options
            return mod.connect(*args, **kwds)
        except ImportError:
            return None
        

try:
    import pyodbc

    class pyodbc_db_Table(db_Table):

        alias('pyodbc', "Manage IO with a %s database interface" % 'pyodbc')

        def __init__(self):
            db_Table.__init__(self)
            self.using = 'pyodbc'

        def connect(self, connection, options):
            if not options.driver is None:
                ctype = options.driver
            elif '.' in connection:
                ctype = connection.split('.')[-1]
            connection = self.create_connection_string(ctype, connection, options)
            if ctype in ['xls','excel'] or '.xls' in connection:
                return db_Table.connect(self, connection, options, {'autocommit':True})
            return db_Table.connect(self, connection, options)
        
        def create_connection_string(self, ctype, connection, options):
            if ctype in ['xls', 'excel']:
                return "Driver={Microsoft Excel Driver (*.xls)}; Dbq=%s;" % connection
            if ctype in ['mdb', 'access']:
                return "Driver={Microsoft Access Driver (*.mdb)}; Dbq=%s;" % connection
            return connection
                    
except ImportError:
    pass


for module in ['pymysql']:
    try:
        __import__(module)
        class tmp(db_Table):
            alias(module, "Manage IO with a %s database interface" % module)
            def __init__(self):
                db_Table.__init__(self)
                self.using = module

    except ImportError:
        pass

