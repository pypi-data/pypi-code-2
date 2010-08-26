# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

import os

from pyf.services import model
from pyf.services.tests.models import ModelTest
from pyf.services.tests import setup_db, teardown_db

from pyf.services.model import DBSession

from pyjon.descriptors import Descriptor

from ConfigParser import SafeConfigParser

from pyf.componentized.core import Manager as ComponentManager

# this is the location of the test directory relative to the setup.py file
basetestdir = "pyf.services/tests/models"

class TestDescriptor(ModelTest):
    """Unit test case for the ``Tube`` model."""
    klass = model.Descriptor
    attrs = dict(
        display_name = u"Simple CSV descriptor",
        description = u"",
        payload_xml = """<?xml version="1.0" encoding="UTF-8"?>
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="descriptor.xsd">
    <header>
        <format name="csv">
            <startline>1</startline>
            <delimiter>;</delimiter>
        </format>
    </header>
    <fields>
        <field name="Field1" mandatory="true">
            <source>1</source>
            <type>int</type>
        </field>
        <field mandatory="false" name="Field2">
            <source>2</source>
            <type>string</type>
        </field>
        <field mandatory="false" name="Field3">
            <source>3</source>
            <type>string</type>
        </field>
        <field mandatory="false" name="Field4">
            <source>4</source>
            <type>string</type>
        </field>
    </fields>
</descriptor>
        """,
        default_encoding="UTF-8")
    
    def test_descriptor_instanciation(self):
        desc = self.obj.get_descriptor_object()
        
        assert isinstance(desc, Descriptor)
        
    def test_descriptor_reading(self):
        desc = self.obj.get_descriptor_object()
        file_obj = open('%s/test.csv' % basetestdir)
        
        num = 0
        for line in desc.read(file_obj):
            assert line.Field1 == num
            assert line.Field2 in ['toto', 'titi', 'tata', 'tutu']
            assert line.Field3 in ['foo', 'bar', 'gal', 'doh']
            assert line.Field4 in ['yop', 'yip', 'youp', 'yap']
            num += 1
        
        file_obj.close()
        
        assert num == 200
        


class TestTube(ModelTest):
    """Unit test case for the ``Tube`` model."""
    klass = model.Tube
    attrs = dict(
        name=u"simple",
        display_name=u"Simple tube",
        description=u"",
        payload_ini="""
<config>
  <process name="ledger">
    <node type="producer" pluginname="descriptorsource" name="source">
      <children>
        <node type="consumer" pluginname="csvwriter" name="writer_csv">
          <columns>
            <column>Field1</column>
            <column>Field2</column>
            <column>Field3</column>
          </columns>
          <encoding>UTF-8</encoding>
          <delimiter>;</delimiter>
          <target_filename>test_file_%Y%m%d_%H%M%S.csv</target_filename>
        </node>
      </children>
    </node>
  </process>
</config>
"""
        )
    
    def test_config_generation(self):
        self.config_obj = self.obj.get_process_config()
        assert isinstance(self.config_obj, SafeConfigParser)
        
    def test_process_name(self):
        assert len(self.obj.process_names) == 1
        assert self.obj.process_names[0] == 'ledger'
        
    def test_manager_instanciation(self):
        manager = self.obj.get_manager()
        assert isinstance(manager, ComponentManager)
        
    def test_config_content(self):
        self.config_obj = self.obj.get_process_config()
        assert self.config_obj.has_section('profile_main')
        assert self.config_obj.has_section('profiles')
        assert self.config_obj.has_section('process_ledger')
        assert self.config_obj.get('process_ledger',
                                   'writer_csv_encoding').strip() == 'UTF-8'
        assert self.config_obj.get('process_ledger',
                                   'writer_csv_delimiter').strip() == ';'
                                   
    def test_process_launch(self):
        class TestData(object):
            def __init__(self, val):
                self.val = val
                
                self.Field1 = str(val)
                self.Field2 = val
            
            @property
            def Field3(self):
                return self.val * 2
        
        def get_data(rangenum):
            for i in xrange(rangenum):
                yield TestData(i+1)
        
        result_files = self.obj.flow(source=get_data(500))
        for file in result_files:
            self.temp_files.append(file)
        assert len(result_files) == 1
        return result_files[0]
        
    def test_process_result(self):
        file = open(self.test_process_launch(), 'r')
        line_1 = file.readline()
        assert line_1.strip('\r\n') == '"Field1";"Field2";"Field3"'
        
        total_lines = 0
        for i, line in enumerate(file):
            if i == 19:
                assert line.strip('\r\n') == '"20";"20";"40"'
            total_lines += 1
        
        assert total_lines == 500
        
class TestTubeLayer(ModelTest):
    klass = model.TubeLayer
    attrs = dict(
        variant_name="france",
        display_name=u"Ledger French CSV Writer encoding Changer",
        description=u"Changes simple's ledger writer_csv encoding to iso-8859-9",
        active=True,
        payload_ini="""
<modifiers>
  <modifier target="writer_csv" action="modify">
      <encoding>ISO-8859-9</encoding>
      <columns>
        <column attribute="Field1">Num</column>
        <column>Field2</column>
        <column attribute="Field3">TwoNum</column>
      </columns>
  </modifier>
</modifiers>
""")
    
    def do_get_dependencies(self):
        return dict(tube = TestTube().setup())
                #descriptor = TestDescriptor().setup())
    
    def test_tube_relation(self):
        assert isinstance(self.obj.tube, model.Tube)
                    
    def test_layered_config_generation(self):
        self.obj.tube.get_layered_config(variant=self.obj.variant_name)
    
    def test_layered_config_content(self):
        layered_config = \
                self.obj.tube.get_layered_config(variant=self.obj.variant_name)
        
        assert layered_config.has_section('profile_main')
        assert layered_config.has_section('profiles')
        assert layered_config.has_section('process_ledger')
        assert layered_config.get('process_ledger',
                                'writer_csv_encoding').strip() == 'ISO-8859-9'
        assert layered_config.get('process_ledger',
                                   'writer_csv_delimiter').strip() == ';'
                                   
    def test_layered_process_launch(self):
        class TestData(object):
            def __init__(self, val):
                self.val = val
                
                self.Field1 = str(val)
                self.Field2 = val
            
            @property
            def Field3(self):
                return self.val * 2
        
        def get_data(rangenum):
            for i in xrange(rangenum):
                yield TestData(i+1)
        
        result_files = self.obj.tube.flow(source=get_data(500),
                                          variant=self.obj.variant_name)
        for file in result_files:
            self.temp_files.append(file)
        assert len(result_files) == 1
        return result_files[0]
        
    def test_layered_process_result(self):
        file = open(self.test_layered_process_launch(), 'r')
        line_1 = file.readline()
        print line_1
        assert line_1.strip('\r\n') == '"Num";"Field2";"TwoNum"'
        
        total_lines = 0
        for i, line in enumerate(file):
            if i == 19:
                print line
                assert line.strip('\r\n') == '"20";"20";"40"'
            total_lines += 1
            
        file.close()
        
        assert total_lines == 500
        
class TestComplexTubeLayer(TestTubeLayer):
    klass = model.TubeLayer
    attrs = dict(
        variant_name="france",
        display_name=u"Ledger French CSV Writer encoding Changer",
        description=u"Changes simple's ledger writer_csv encoding to iso-8859-9",
        active=True,
        payload_ini="""
<modifiers>
  <modifier target="writer_csv" action="enclose">
    <node type="adapter" from="code" name="field4_adder">
      <code type="function">
        <![CDATA[
def iterator(input):
    for i, value in enumerate(input):
        setattr(value, 'ThreeNum', value.Field1 * 3)
        yield value
]]>
      </code>
    </node>
  </modifier>
  <modifier target="writer_csv" action="modify">
      <encoding>ISO-8859-9</encoding>
      <columns>
        <column attribute="Field1">Num</column>
        <column>Field2</column>
        <column attribute="Field3">TwoNum</column>
        <column>ThreeNum</column>
      </columns>
  </modifier>
</modifiers>
""")
    
    def test_layered_process_result(self):
        file = open(self.test_layered_process_launch(), 'r')
        line_1 = file.readline()
        print line_1
        assert line_1.strip('\r\n') == '"Num";"Field2";"TwoNum";"ThreeNum"'
        
        total_lines = 0
        for i, line in enumerate(file):
            if i == 19:
                print line
                assert line.strip('\r\n') == '"20";"20";"40";"60"'
            total_lines += 1
        
        file.close()
        
        assert total_lines == 500
        
class TestDispatch(ModelTest):
    klass = model.Dispatch
    attrs = dict(
        display_name=u"Dispatcher for simple descriptor and simple tube",
        description=u"")
    
    def do_get_dependencies(self):
        return dict(tube = TestTube().setup(),
                    descriptor = TestDescriptor().setup())
        
    def test_input_error(self):
        raised_error = False
        try:
            self.obj.process_file(None,
                                  variant=False,
                                  encoding=None)
        except ValueError, error:
            assert str(error) == "This tube needs a source"
            raised_error = True
        
        assert raised_error
        
    def test_input_file(self):
        file_obj = open('%s/test.csv' % basetestdir)
        
        result_files = self.obj.process_file(file_obj,
                                             variant=False,
                                             encoding=None)
        file_obj.close()
        
        for file in result_files:
            self.temp_files.append(file)
        assert len(result_files) == 1
        
        return result_files[0]
    
    def test_input_file_process(self):
        file = open(self.test_input_file(), 'r')
        line_1 = file.readline()
        print line_1
        assert line_1.strip('\r\n') == '"Field1";"Field2";"Field3"'
        
        total_lines = 0
        for i, line in enumerate(file):
            line_array = line.strip('\r\n').replace('"','').split(';')
            
            assert int(line_array[0]) == i
            assert line_array[1] in ['toto', 'titi', 'tata', 'tutu']
            assert line_array[2] in ['foo', 'bar', 'gal', 'doh']
            
            if i == 19:
                print line
                assert line.strip('\r\n') == '"19";"tata";"gal"'
            total_lines += 1
            
        file.close()
        
        assert total_lines == 200