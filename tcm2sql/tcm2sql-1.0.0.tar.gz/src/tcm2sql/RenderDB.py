# Copyright (C) 2006 gocept gmbh & co.kg, 06112 Halle(Saale), Germany
# Christian Zagrodnick, cz@gocept.com
# Michael Howitz, mh@gocept.com
# $Id: RenderDB.py 31512 2010-12-14 10:13:34Z mac $
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# python
import re

# sibling
from Render import Render as RenderBase

class Render(RenderBase):
    """Abstract renderer class for databases."""
    
    _abstract = True # set it to false on concrete classes

    ### the following methods may have to be overwritten for concrete DBMS ###
    
    def startTransaction(self):
        """Return the command to start a transaction."""
        return "BEGIN;\n"

    def commitTransaction(self):
        """Return the command to commit a transaction."""
        return "COMMIT;\n"

    def createTable(self, tablename, column_list):
        result = ["\nCREATE TABLE %s (" % tablename]
        result.extend(column_list)
        result.append(")")
        return "\n".join(result)

    def dropTable(self, tablename):
        return 'DROP TABLE %s;\n' % tablename

    def renderInheritenceTableFooter(self, tablename, parents, all_tables):
        if tablename in parents.keys():
            return (" INHERITS (%s)" %
                    all_tables[parents[tablename]].name)
        else:
            return ""

    def renderTableFooter(self):
        return ""

    def renderAttribute(self, attr):
        """Render one attribute."""
        return "    %s %s," % (attr[0], attr[1])

    def renderSerialType(self, tablename, columnname, datatype):
        datatype = self.convertType(datatype)
        return ("%s NOT NULL DEFAULT "
                "NEXTVAL('%s_%s_seq'::text)" %
                (datatype, tablename.lower(), columnname.lower()))

    def convertType(self, type):
        "Convert the type to the correct value for the DBMS."
        serial_type = self._serial_pattern.match(type)
        if serial_type is None:
            return type
        serial_type = serial_type.groups()[0]
        if serial_type == "serial":
            serial_type = "INTEGER"
        elif serial_type == "bigserial":
            serial_type = "BIGINT"
        else:
            raise ValueError("Don't know how to convert %s." % serial_type)
        return serial_type


    def renderConstraint(self, name, rule):
        return "    CONSTRAINT %s %s," % (name, rule)

    def copyToTemporaryTable(self, tablename):
        return 'CREATE TEMPORARY TABLE "TMP%s" AS SELECT * FROM %s;\n' % \
               (tablename.replace('"', ''), tablename)
    
    def copyFromTemporaryTable(self, tablename, fields):
        return ('INSERT INTO %s (%s)\n'
                '    SELECT %s FROM "TMP%s";\n' %
                (tablename, fields, fields, tablename.replace('"', '')))

    def createView(self, tablename, columnlist):
        result = ['CREATE VIEW "sv%s" AS' % tablename,
                  '    SELECT',
                  '        ' + ','.join(columnlist),
                  '    FROM %s;' % tablename,
                  '', ]
        return "\n".join(result)

    def dropView(self, tablename):
        return 'DROP VIEW "sv%s";\n' % tablename

    def createSequence(self, tablename, columnname):
        return "CREATE SEQUENCE %s_%s_seq;\n" % (tablename.lower(),
                                                 columnname.lower())

    def dropSequence(self, tablename, columnname):
        return "DROP SEQUENCE %s_%s_seq;\n" % (tablename.lower(),
                                               columnname.lower())

    def renderRelation(self, rel, TABLES):
        """Create foreign key constraint."""
        table1name = TABLES[rel.table1].name
        table2name = TABLES[rel.table2].name
        result = ["ALTER TABLE %s" % table1name,
                  "ADD CONSTRAINT %s" % self._get_foreign_key(table2name,
                                                              rel.field2),
                  "FOREIGN KEY (%s)" % rel.field1,
                  "REFERENCES %s (%s)" % (table2name, rel.field2),
                  ]
        if rel.kind == 1: # aggregation
            result.append("ON DELETE SET NULL")
        elif rel.kind == 2: # composition
            result.extend(["ON DELETE CASCADE",
                           "ON UPDATE CASCADE"])
        elif rel.kind == 3: # binary
            pass # XXX
        result.append(";\n")
        return "\n".join(result)

    def dropRelation(self, rel, TABLES):
        "Drop foreign key constraint."""
        table1name = TABLES[rel.table1].name
        table2name = TABLES[rel.table2].name
        result = ["\nALTER TABLE %s" % table1name,
                  "DROP CONSTRAINT %s" % self._get_foreign_key(table2name,
                                                              rel.field2),
                  ";"]
        return "\n".join(result)

    def logRules(self, TABLES, table, PARENT):
        """Create triggers for logging tables. """
        tn = table.name
        log_table = table.getLoggingTable()
        log_fields = ', '.join(
            map(lambda x: x[0],
                self._inheritedFields(log_table.name, TABLES, PARENT,
                                      fields=[])))
        table_fields = ', '.join(
            map(lambda x: 'new.%s' % (x[0], ),
                self._inheritedFields(tn, TABLES, PARENT, fields=[])))
        
        result = ["""\nCREATE or REPLACE FUNCTION "trig_%s"() """
                  """RETURNS TRIGGER AS '""" %  tn,
                  "    BEGIN",
                  "        INSERT INTO %s (%s)" % (log_table.name, log_fields),
                  "        VALUES (now(), %s);" % table_fields,
                  "        RETURN NULL;",
                  "    END;'",
                  "LANGUAGE 'plpgsql';",
                  "CREATE TRIGGER I%s AFTER INSERT OR UPDATE ON %s" % (tn, tn),
                  'FOR EACH ROW EXECUTE PROCEDURE "trig_%s"();' % tn,
                  'CREATE RULE "U%s" AS ON UPDATE TO %s DO INSTEAD NOTHING;' %\
                  (tn, log_table.name),
                  'CREATE RULE "D%s" AS ON DELETE TO %s DO INSTEAD NOTHING;' %\
                  (tn, log_table.name),
                  '']
        return "\n".join(result)

    def fixup_logging_helper(self, ssd):
        global optCreateLoggingTables
        for table in ssd.tables.values():
            # add LOGUser if logging is on
            if optCreateLoggingTables:
                table.attrlist.insert(0, ('"LOGUser"', 'VARCHAR(32) NOT NULL'))
                table.flaglist.insert(0, ('"LOGUser"', ''))

            # the rest here is only for logging tables
            if not table.isLoggingTable():
                continue
            
            # add LOGTime to logging tables
            table.attrlist.insert(0, ('"LOGTime"',
                'TIMESTAMP NOT NULL DEFAULT now()'))
            table.flaglist.insert(0, ('"LOGTime"', ''))
            
            # set serials to integer in logging tables
            for i in range(0, len(table.attrlist)):
                name, type = table.attrlist[i]
                table.attrlist[i] = (name, self.convertType(type))


    ### The following methods are independent from DBMS. ###
    
    _serial_pattern = re.compile(r"^\s*(serial|bigserial)\s*$")
    
    def __init__(self, *cwd, **kw):
        RenderBase.__init__(self, *cwd, **kw)
        self._foreign_keys = []
        self._fixup_logging()
        if self._abstract:
            raise SystemError('%s is an abstract class, you can not use it '
                              'as a renderer.' % self.__class__.__name__)

    def _layoutFull(self):
        """Returns a string with the table layout."""
        
        TABLES = self.new.tables
        TABLES_VALUES = TABLES.values()
        RELATIONS = self.new.relations
        PARENT = self.new.parent

        ret = self.startTransaction()

        # create tables
        for tableid in self._getOrder(self.new):
            table = TABLES[tableid]
            if table.name is None:
                raise ValueError('Table %s does not exist' % tableid)
            ret += self._renderTable(table, TABLES, RELATIONS, PARENT)
        ret += "\n\n"

        # create sequences for tables
        for (tablename, colname) in self._get_serials(TABLES_VALUES):
            ret += self.createSequence(tablename, colname)
        ret += "\n\n"

        # create relations
        for rel in RELATIONS:
            ret += self.renderRelation(rel, TABLES)
        ret += "\n\n"

        # create logging tables if requested
        if optCreateLoggingTables:
            non_logging_tables = [ table
                                   for table in TABLES_VALUES
                                   if not table.isLoggingTable()
                                   ]
            for table in non_logging_tables:
                ret += self.logRules(TABLES, table, PARENT)

        ret += self.commitTransaction()

        return ret

    def _layoutDiff(self):
        """Returns a string with the diff layout."""
        global optCreateViews
        
        ret = self.startTransaction()

        # drop the foreign key constraints, so tables may be freely dropped
        for rel in self.old.relations:
            ret += self.dropRelation(rel, self.old.tables)
            
        # clean foreign key cache so that numbering if their ids stays constant
        self._foreign_keys = []

        # copy table contents to temporary tables, drop old tables
        dropOrder=self._getOrder(self.old)
        dropOrder.reverse()
        for tid in dropOrder:
            t = self.old.tables[tid]
            ret += self.copyToTemporaryTable(t.name)
            if not t.isLoggingTable() and optCreateViews:
                ret += self.dropView(t.name)
            ret += self.dropTable(t.name)
            ret += "\n" 

        # create the new tables
        for tableid in self._getOrder(self.new):
            ret += self._renderTable(self.new.tables[tableid], self.new.tables,
                                     self.new.relations, self.new.parent)

        # copy data back
        dropedFields=self._dropedFields()
        for t in [t
            for t in self._oldTables()
            for t2 in self._newTables()
            if t == t2
            ]:
            dfThis=\
                map((lambda x: x[1]),
                filter((lambda x: x[0]==t),
                dropedFields))
            fields=','.join(
                filter(lambda x: x not in dfThis,
                map(lambda x: x[0],
                t.attrlist)))
            if fields > '':
                ret += self.copyFromTemporaryTable(t.name, fields)
        ret += "\n\n"
        
        # drop sequences of deleted tables
        for (tablename, colname) in self._get_serials(self._removedTables()):
            ret += self.dropSequence(tablename, colname)
        ret += "\n\n"
        
        # create sequences for new tables
        for (tablename, colname) in self._get_serials(self._addedTables()):
            ret += self.createSequence(tablename, colname)
        ret += "\n\n"

        # create the foreign key constraints
        for rel in self.new.relations:
            ret += self.renderRelation(rel, self.new.tables)

        # create log rules
        global optCreateLoggingTables
        if optCreateLoggingTables:
            for table in [t
                          for t in self.new.tables.values()
                          if not t.isLoggingTable()]:
                ret += self.logRules(self.new.tables, table, self.new.parent)

        ret += self.commitTransaction()
        return ret


    def _renderTable(self, table, TABLES, RELATIONS, PARENT):
        """Render a table."""
        global optCreateViews

        # transforms Attributes with type 'serial'
        attrs = []
        for (name, type) in table.attrlist:
            serial_type = self._serial_pattern.match(type)
            if serial_type is not None:
                type = self.renderSerialType(table.name, name,
                                             serial_type.groups()[0])
            attrs.append((name, type))
        
        # render Attributes
        lines = [self.renderAttribute(attr) for attr in attrs]

        # constraints
        lines.extend([self.renderConstraint(cs.name, cs.rule)
                      for cs in table.clist])
        
        if len(lines):
            # if there are lines remove the komma on the end of the last line
            lines[-1] = lines[-1][:-1]

        ret = self.createTable(table.name, lines)

        # inheritance (generalization)
        ret += self.renderInheritenceTableFooter(table.name, PARENT, TABLES)
    
        ret += self.renderTableFooter()
        
        if not table.isLoggingTable():
            attrlist=map(lambda x: x[0],
                filter(lambda x: '-' not in x[1],
                self._inheritedFields(table.name, TABLES, PARENT, fields=[])))

            if optCreateViews and len(attrlist) > 0:
                ret += "\n"
                ret += self.createView(table.name, attrlist)
        return ret


    def _inheritedFields(self,tableid,TABLES,PARENT,fields=[]):
        #print "in: %s: %s" %(tableid, fields)
        f = []
        if tableid in PARENT.keys():
            f = self._inheritedFields(PARENT[tableid], TABLES, PARENT,
                                      fields=fields)

        try:
            for x in TABLES[tableid].flaglist + f:
                if x not in fields:
                    fields += [x, ]
        except KeyError:
            raise KeyError('Table %s does not exist.' % tableid)

        #print "out: %s: %s" %(tableid,fields)
        return fields       
    
    def _get_foreign_key(self, table, field):
        postfix = ''
        field_name = '_'.join([x.strip() for x in field.split(',')])
        while 1:
            fk_name = 'FK%s_%s%s' % (table, field_name, postfix)
            if fk_name not in self._foreign_keys:
                break
            if postfix == '':
                postfix = 0
            postfix += 1
        self._foreign_keys.append(fk_name)
        return fk_name

    def _fixup_logging(self):
        self.fixup_logging_helper(self.new)
        if self.old:
            self.fixup_logging_helper(self.old)

    def _get_serials(self, tables):
        """Get the columns which are of type 'serial' or 'bigserial'.

        Returns list of tuples (tablename, columnname).
        """
        result = []
        for table in tables:
            for (name, type) in table.attrlist:
                if self._serial_pattern.match(type) is not None:
                    result.append((table.name, name))
        return result
