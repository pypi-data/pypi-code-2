# Copyright (C) 2002 gocept gmbh & co.kg, 06366 Koethen/Anahlt, Germany
# Christian Zagrodnick, cz@gocept.com
# $Id: SSDReader.py 31512 2010-12-14 10:13:34Z mac $
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
import os

# sibling
from Table import Table
from Relation import Relation
from tcmfile import TCMFile
from helpers import parseString

class SSDReader:

    _external_file_pattern = re.compile(r'"(<<)?(.*?)(>>)?"')

    _edge_relation_mapping = {
        'SSDAggregationEdge': Relation.AGGREGATION,
        'SSDCompositionEdge': Relation.COMPOSITION,
        'SSDBinaryAssociationEdge': Relation.BINARY,
    }
        
    def __init__(self, filename):
        """filename is the main filename, root of all evil
        """
        self.filename = filename
        if not os.path.exists(filename):
            raise IOError, '%s does not exist' % filename
       
        # mapping: filename -> ssd structure
        self.tcm = {}

        # mapping: table name -> table
        self.tables = {}

        # mapping: (filename, id) -> name
        self.table_name_mapping= {}

        # list of relations
        self.relations = []

        # mapping child -> parent
        self.parent = {}

    def build(self, optCreateLoggingTables):
            self.read_all()
            self.build_tables()
            self.build_relations()
            self.build_generalizations()
            if optCreateLoggingTables:
                self.build_logtables()

    def read_all(self):
        old_cwd = os.getcwd()
        new_cwd = os.path.dirname(self.filename)
        try:
            if new_cwd:
                os.chdir(new_cwd)
            files = [os.path.basename(self.filename)]
            files_read = []
            while files:
                filename = files[0]
                del(files[0])
                files_read.append(filename)
                ssd_structure = self.read_tcm(filename)
                self.tcm[filename] = ssd_structure
                files += [ filename
                    for filename in self.external_files(ssd_structure)
                    if filename not in files_read
                    ]
        finally:
            os.chdir(old_cwd)
        
    def read_tcm(self, filename):
        f = file(filename)
        tcm = TCMFile(f)
        ssd_structure = tcm.parse()
        return ssd_structure

    def external_files(self, ssd_structure):
        """returns list of filenames
        """
        files = []
        tables = ssd_structure['SSDClassNode']
        for table in tables:
            stereotype = table.get('Stereotype', None)
            if not stereotype:
                continue
            assert len(stereotype) == 1
            stereotype = stereotype[0]
            m = self._external_file_pattern.match(stereotype)
            if m is None:
                continue
            filename = m.group(2)
            filename = filename.strip()
            basename, ext = os.path.splitext(filename)
            if ext != '.ssd':
                continue
            files.append(filename)
        return files
            
    def build_tables(self):
        for filename, ssd in self.tcm.items():
            for node in ssd['SSDClassNode']:
                name = parseString(node['Name'])
                table = self.tables.setdefault(name, Table())
                table.update(filename, **node)
                self.table_name_mapping[(filename, node['_id'])] = name

    def build_relations(self):
        for filename, ssd in self.tcm.items():
            for edge_kind, relation_kind in self._edge_relation_mapping.items():
                for edge in ssd.get(edge_kind, []):
                    relation = Relation(relation_kind)
                    self.relations.append(relation)
                    relation.table1 = parseString(
                        self.table_name_mapping[(filename,
                            edge['Subject1'][0])])
                    relation.table2 = parseString(
                        self.table_name_mapping[(filename,
                            edge['Subject2'][0])])
                    relation.table1_instance = self.tables[relation.table1]
                    relation.table2_instance = self.tables[relation.table2]
                    relation.constraint1 = parseString(edge['Constraint1'])
                    relation.constraint2 = parseString(edge['Constraint2'])
                    relation.field1 = parseString(edge['RoleName1'])
                    relation.field2 = parseString(edge['RoleName2'])
                    relation.consolidate()
                    
    def build_generalizations(self):
        for filename, ssd in self.tcm.items():
            for node in ssd.get('SSDGeneralizationEdge', []):
                parent_id = parseString(node['Subject2'])
                child_id = parseString(node['Subject1'])
                parent_name = self.table_name_mapping[(filename, parent_id)]
                child_name = self.table_name_mapping[(filename, child_id)]
                parent_table = self.tables[parent_name]
                child_table = self.tables[child_name]
                parent_table.addChild(child_table)
                child_table.setParent(parent_table)
                # mainly for backward compatibility:
                self.parent[child_name] = parent_name

    def build_logtables(self):
        log_tables = []
        for table in self.tables.values():
            log_tables.append(table.createLoggingTable())
        for log in log_tables:
            parent = log.getMasterTable().parent
            if parent is not None:
                log.parent = parent.getLoggingTable()
            childs = log.childs = []
            for master_child in log.getMasterTable().childs:
                child = master_child.getLoggingTable()
                childs.append(child)
                self.parent[child.name] = log.name
        for log in log_tables:
            self.tables[log.name] = log

