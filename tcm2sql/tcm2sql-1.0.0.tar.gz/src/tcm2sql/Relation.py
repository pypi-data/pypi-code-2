# Copyright (C) 2003 gocept gmbh & co.kg, 06366 Koethen/Anhalt, Germany
# Christian Zagrodnick, cz@gocept.com
# $Id: Relation.py 31512 2010-12-14 10:13:34Z mac $
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

# Python
import re

# sibling
from helpers import parseString

class Relation:
    # 1: Table which references Table2
    # 2: Table which is being referred by Table1
    # i.e. Table2 has the Primary Key
    # kind: aggregation=1, composition=2, binary=3

    AGGREGATION = 1
    COMPOSITION = 2
    BINARY = 3

    _foreign_key_pattern = re.compile(r'^([^_]+)_(\w+)$')
    
    def __init__(self, kind):
        if not (1 <= kind <= 3):
            raise ValueError, "unkown relation %i" % kind
        self.kind = kind

    def consolidate(self):
        """detect inconsistencies, fill in derived data"""
        if self.kind == self.BINARY:
            if "1" not in (self.constraint1, self.constraint2):
                raise ValueError, "Ambigous reference (%s<-->%s)" % (
                    self.table1, self.table2)
            if "1" == self.constraint1.strip():
                self._switch_relation()
        if not self.field1.strip():
            self._autofill_field1()
        if not self.field2.strip():
            self._autofill_field2()

    def _autofill_field1(self):
        fklist = []
        for fk in self.table1_instance.fklist:
            m = self._foreign_key_pattern.match(fk)
            if m is None:
                continue
            referenced_table_name = m.group(1)
            if self.table2 == referenced_table_name:
                fklist.append(fk)
        if not fklist:
            raise ValueError, "Foreign key not found %r" % self
        self.field1 = ', '.join(fklist)
    
    def _autofill_field2(self):
        pklist = self.table2_instance.getPrimaryKey()
        if pklist != self.table2_instance.pklist:
            self.table2_instance.addConstraint('PK_%s' % self.table2,
                'UNIQUE (%s)' % (', '.join(pklist)))
        self.field2 = ', '.join(pklist)

    def _switch_relation(self):
            # swich 1 and 2 XXX
            switch = self.table1
            self.table1 = self.table2
            self.table2 = switch

            switch = self.table1_instance
            self.table1_instance = self.table2_instance
            self.table2_instance = switch
            
            switch = self.constraint1
            self.constraint1 = self.constraint2
            self.constraint2 = switch
            
            switch = self.field1
            self.field1 = self.field2
            self.field2 = switch
                

    def __eq__(self,other):
        if \
            (self.table1==other.table1) and\
            (self.table2==other.table2) and\
            (self.constraint1==other.constraint1) and\
            (self.constraint2==other.constraint2) and\
            (self.field1==other.field1) and\
            (self.field2==other.field2) and\
            (self.kind==other.kind):
            return 1
        return 0    
       
    def __repr__(self):
        return "[%s]--<[%s]" % (self.table1, self.table2)
    
