# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

import os

from pyf.services import model
from pyf.services.tests.models import ModelTest
from pyf.services.tests import setup_db, teardown_db

from pyf.services.model import DBSession

from pyjon.descriptors import Descriptor

from pyf.componentized import ET
from pyf.componentized.core import Manager as ComponentManager

# this is the location of the test directory relative to the setup.py file
basetestdir = "pyf/services/tests/models"

class TestDescriptor(ModelTest):
    """Unit test case for the ``Tube`` model."""
    klass = model.Descriptor
    attrs = dict(
        name = u"simple_csv",
        display_name = u"Simple CSV descriptor",
        description = u"",
        payload_xml = u"""<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="descriptor.xsd">
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
        payload=u"""
<config>
  <process name="ledger">
    <node type="producer" pluginname="descriptorsource" name="source">
      <children>
        <link name="writer_csv" />
      </children>
    </node>
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
  </process>
</config>
"""
        )

    def test_config_generation(self):
        self.config_obj = self.obj.get_config_tree()
        assert isinstance(self.config_obj, ET._Element)

    def test_process_name(self):
        assert len(self.obj.process_names) == 1
        assert self.obj.process_names[0] == 'ledger'

    def test_manager_instanciation(self):
        manager = self.obj.get_manager()
        assert isinstance(manager, ComponentManager)

    def test_config_content(self):
        self.config_obj = self.obj.get_config_tree()

        process_node = self.config_obj.find('process')
        assert process_node is not None, "Didn't find any 'process' node in the tube configuration"

        nodes = process_node.findall('node')
        assert len(nodes) == 2, "Found %s component nodesinstead of 2" % len(nodes)

        node_names = [node.get('name') for node in nodes]
        assert 'source' in node_names, "Didn't find any 'source' node in the tube process"
        assert 'writer_csv' in node_names, "Didn't find any 'writer_csv' node in the tube process"

        for node in nodes:
            if node.get('name') == 'writer_csv':
                assert node.find('encoding').text.strip() == 'UTF-8', "Encoding is '%s' instead of 'UTF-8'" % node.find('encoding').text
                assert node.find('delimiter').text.strip() == ';', "Delimiter is '%s' instead of ';'" % node.find('delimiter').text

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
        for tmp_filename, result_filename in result_files:
            self.temp_files.append(tmp_filename)
        assert len(result_files) == 1
        return result_files[0]

    def test_process_result(self):
        tmp_filename, result_filename = self.test_process_launch()
        file = open(tmp_filename, 'r')
        line_1 = file.readline()
        assert line_1.strip('\r\n') == '"Field1";"Field2";"Field3"'

        total_lines = 0
        for i, line in enumerate(file):
            if i == 19:
                assert line.strip('\r\n') == '"20";"20";"40"'
            total_lines += 1

        assert total_lines == 500

    def test_params(self):
        """Test tube parameters."""
        self.obj.payload = u"""
<config>
  <process name="ledger">
    <params>
      <param>
        <key>target_date</key>
        <type>datetime</type>
        <name>Target Date</name>
        <description>End date for the extraction</description>
        <default>10/10/1998</default>
      </param>
      <param>
        <key>target_type</key>
        <type>select</type>
        <name>Target Type</name>
        <default>oo</default>
        <options>
          <option label="toto">oo</option>
          <option label="titi">ii</option>
        </options>
      </param>
    </params>
    <node type="producer" pluginname="descriptorsource" name="source">
      <children>
        <link name="writer_csv" />
      </children>
    </node>
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
  </process>
</config>
"""
        expected = {'target_date': {'key': 'target_date',
                                    'type': 'datetime',
                                    'name': 'Target Date',
                                    'description': 'End date for the extraction',
                                    'default': '10/10/1998',
                                    'order': 0},
                    'target_type': {'key': 'target_type',
                                    'type': 'select',
                                    'name': 'Target Type',
                                    'default': 'oo',
                                    'options': [
                                        {'option_label': 'toto', 'option': 'oo'},
                                        {'option_label': 'titi', 'option': 'ii'}],
                                    'order': 1}
                    }


        result = self.obj.get_parameters()

        assert result == expected, "Got for parameters:\n%s\nInstead of:\n%s" % (result, expected)

class TestTubeLayer(ModelTest):
    klass = model.TubeLayer
    attrs = dict(
        name=u"fr_csv_writer",
        variant_name=u"france",
        display_name=u"Ledger French CSV Writer encoding Changer",
        description=u"Changes simple's ledger writer_csv encoding to iso-8859-9",
        active=True,
        payload=u"""
<modifiers>
  <modifier target="writer_csv" action="modify">
      <encoding>ISO-8859-9</encoding>
      <columns>
        <column attribute="Field1">Num</column>
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

        process_node = layered_config.find('process')
        assert process_node is not None, "Didn't find any 'process' node in the tube configuration"

        nodes = process_node.findall('node')
        assert len(nodes) == 2, "Found %s component nodes instead of 2" % len(nodes)

        node_names = [node.get('name') for node in nodes]
        print node_names
        assert 'source' in node_names, "Didn't find any 'source' node in the tube process"
        assert 'writer_csv' in node_names, "Didn't find any 'writer_csv' node in the tube process"

        for node in nodes:
            if node.get('name') == 'writer_csv':
                assert node.find('encoding').text.strip() == 'ISO-8859-9', "Encoding is '%s' instead of 'UTF-8'" % node.find('encoding').text

                columns_node = node.find('columns')
                assert len(columns_node) == 2, "Got %s columns instead of 2" % len(columns_node)

                columns_titles = [n.text.strip() for n in columns_node]
                assert 'Num' in columns_titles, "Didn't find a 'Num' column for the CSV writer"
                assert 'TwoNum' in columns_titles, "Didn't find a 'TwoNum' column for the CSV writer"

                columns_attributes = [n.get('attribute').strip() for n in columns_node]
                assert 'Field1' in columns_attributes, "Didn't find a 'Field1' column attribute for the CSV writer"
                assert 'Field3' in columns_attributes, "Didn't find a 'Field3' column attribute for the CSV writer"

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

        for tmp_filename, result_filename in result_files:
            self.temp_files.append(tmp_filename)

        assert len(result_files) == 1
        return result_files[0]

    def test_layered_process_result(self):
        tmp_filename, result_filename = self.test_layered_process_launch()
        file = open(tmp_filename, 'r')
        line_1 = file.readline().strip('\r\n')
        assert line_1 == '"Num";"TwoNum"', 'Got:\n%s\nInstead of:\n"Num";"TwoNum"' % line_1

        for i, line in enumerate(file):
            if i == 19:
                assert line.strip('\r\n') == '"20";"40"', 'Got:\n%s\nInstead of:\n"20";"40"' % line.strip('\r\n')

        total_lines = i + 1
        file.close()

        assert total_lines == 500, "Got %s lines instead of 500" % total_lines

class TestDispatch(ModelTest):
    klass = model.Dispatch
    attrs = dict(
        name=u"simple_dispatch",
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

        for tmp_filename, result_filename in result_files:
            self.temp_files.append(tmp_filename)
        assert len(result_files) == 1

        return result_files[0]

    def test_input_file_process(self):
        tmp_filename, result_filename = self.test_input_file()
        file = open(tmp_filename, 'r')
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
