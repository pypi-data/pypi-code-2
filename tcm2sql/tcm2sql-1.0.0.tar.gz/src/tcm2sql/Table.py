# Copyright (C) 2002 gocept gmbh & co.kg, 06366 Koethen/Anahlt, Germany
# Christian Zagrodnick, cz@gocept.com
# $Id: Table.py 31512 2010-12-14 10:13:34Z mac $
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
import sys
from copy import copy, deepcopy

# sibling
from Constraint import Constraint
from helpers import parseString

class Table:
    
    _external_file_pattern = re.compile(r'"(<<)?(.*?.ssd\s*)(>>)?"')
    _attribute_pattern = re.compile(r"^([^A-Za-z]*)(\w+)\s*\:\s*(.+)$")
    _constraint_pattern = re.compile(r"^([\w]+)\s*:\s*(.*)$")
    _serial_pattern = re.compile(r"^\s*serial\s*$")

    def __init__(self, is_logging=False):
        self.filename = None
        self.id = None
        self.name = None
        self.attrlist = []
        self.pklist = []
        self.fklist = []
        self.clist = []
        self.flaglist = []
        self.parent = None
        self.childs = []
        self._is_logging_table = is_logging

    def __str__(self):
        return "%s: (%s,%s,%s,%s,%s)" % (
            self.id,self.name,str(self.attrlist),
            str(self.pklist),str(self.fklist),str(self.clist))
        

    def __cmp__(self,other):
        if(self.name==other.name): return 0
        return -1

    def addConstraint(self,name,op):
        self.clist=self.clist+[Constraint(name,op)]


    def update(self, filename, **kw):
        stereotype = kw['Stereotype']
        m = self._external_file_pattern.match(stereotype[0])
        if m is None:
            master_file = filename
        else:
            master_file = m.group(2)
        if master_file != filename:
            return
        self._update(**kw)

    def _update(self, Name=[], Attribute=[], Operation=[],
            Stereotype=None, Annotation=[], _id=[], **kw):
        self.id = parseString(_id)
        self.name =  parseString(Name[0])
        self.attrlist = []
        self.flaglist = []
        self.pklist = []
        self._update_attributes(Attribute)
        self._update_constraints(Operation)
        self._update_constraints_from_annotations(Annotation)
       
    def _update_attributes(self, attributes):
        attrlist = self.attrlist
        flaglist = self.flaglist
        pklist = self.pklist
        fklist = self.fklist
        for attr in attributes:
            m = self._attribute_pattern.match(parseString(attr))
            if m is None:
                raise ValueError, "invalid aattribute %s.%s" % (
                    self.name, attr)
            flags = m.group(1)
            attrname = m.group(2)
            datatype = m.group(3)
            if '#' in flags:
                pklist.append(attrname)
            if '~' in flags:
                fklist.append(attrname)
            attrlist.append((attrname,datatype))
            flaglist.append((attrname,flags))
    
    def _update_constraints(self, constraints):
        clist = self.clist
        if len(self.pklist) > 0:
            pk_contraint = Constraint("PK_%s" % self.name,
                "PRIMARY KEY (%s)" % ', '.join(self.pklist))
            if not pk_contraint in clist:
                clist.append(pk_contraint)
        for op in constraints:
            op = parseString(op)
            m = self._constraint_pattern.match(op)
            if m is None:
                if op.strip() != '<ext>':
                    raise ValueError, "invalid constraint: %r" % op
                continue
            clist.append(Constraint(
                "%s_%s" % (self.name, m.group(1)), m.group(2)))
    
    def _update_constraints_from_annotations(self, annotations):
        constraints = []
        for a in annotations:
            a = parseString(a)
            lines = a.split('\\r')
            for line in lines:
                line = line.strip()
                if not line.startswith('?'):
                    continue
                c = line[1:].strip()
                constraints.append(c)
        self._update_constraints(constraints)
                

    def setParent(self, parent):
        assert isinstance(parent, Table)
        self.parent = parent

    def addChild(self, child):
        assert isinstance(child, Table)
        if not child in self.childs:
            self.childs.append(child)
   
    def getPrimaryKey(self):
        node = self
        while node:
            if node.pklist:
                return node.pklist[:]
            node = node.parent
        return []
      
    def isLoggingTable(self):
        """returns True if this is a log table"""
        return self._is_logging_table

    def createLoggingTable(self):
        if self.isLoggingTable():
            return self
        log = copy(self)
        log.parent = None
        log.childs = []
        log = deepcopy(log)
        log._is_logging_table = True
        log.pklist = []
        log.fklist = []
        log.clist = []
        log.name = '"LOG%s"' % self.name
        self._log_table = log
        log._master_table = self
        return log

    def getLoggingTable(self):
        if self.isLoggingTable():
            return self
        return self._log_table

    def getMasterTable(self):
        if not self.isLoggingTable():
            return self
        return self._master_table
        

