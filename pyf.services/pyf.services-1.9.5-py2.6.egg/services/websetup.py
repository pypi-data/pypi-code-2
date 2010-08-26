# -*- coding: utf-8 -*-
"""Setup the pyf.services application"""

import logging

import sys

import transaction
from tg import config

from pyf.services.config.environment import load_environment

__all__ = ['setup_app_command',
           'setup_app']

log = logging.getLogger(__name__)

def setup_app_command():
    if len(sys.argv) < 2:
        raise ValueError, "Please provide a .ini file"
    
    ini_file = sys.argv[1]
    
    from paste.deploy import appconfig
    conf = appconfig('config:%s' % ini_file, relative_to="./")
    
    setup_app(sys.argv[0], conf, sys.argv[2:])
    
def setup_app(command, conf, vars):
    """Place any commands to setup pyf.services here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from pyf.services import model
    from pyf.services.model import DBSession

    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    if not DBSession.query(model.User).filter(model.User.email_address==u'manager@somedomain.com').first():
        manager = model.User()
        manager.user_name = u'manager'
        manager.display_name = u'Example manager'
        manager.email_address = u'manager@somedomain.com'
        manager.password = u'managepass'
        model.DBSession.add(manager)

    if not DBSession.query(model.Group).filter(model.Group.group_name==u'managers').first():
        group = model.Group()
        group.group_name = u'managers'
        group.display_name = u'Managers Group'

        group.users.append(manager)

        model.DBSession.add(group)

    if not DBSession.query(model.Permission).filter(model.Permission.permission_name==u'manage').first():
        permission = model.Permission()
        permission.permission_name = u'manage'
        permission.description = u'This permission give an administrative right to the bearer'
        permission.groups.append(group)

        model.DBSession.add(permission)

    if not DBSession.query(model.User).filter(model.User.email_address==u'editor@somedomain.com').first():
        editor = model.User()
        editor.user_name = u'editor'
        editor.display_name = u'Example editor'
        editor.email_address = u'editor@somedomain.com'
        editor.password = u'editpass'

        model.DBSession.add(editor)

    model.DBSession.flush()
    
    desc = setup_sample_descriptor(model)
    if not desc is None:
        tube, tubelayer = setup_sample_tube(model)
    
        dispatch = setup_dispatch(model, u'3 col csv dispatcher',
                              tube, desc, tubelayer.variant_name)

    transaction.commit()
    print "Successfully setup"
    
def setup_sample_descriptor(model):
    from pyf.services.model import DBSession
    if not DBSession.query(model.Descriptor).filter(model.Descriptor.name==u'simple_csv').first():
        print "creating descriptor"
        desc = model.Descriptor(display_name = u"Simple CSV descriptor",
            default_encoding=u"UTF-8",
            name=u"simple_csv",
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
            """)
        model.DBSession.add(desc)
        model.DBSession.flush()
        return desc
    else:
        return None

def setup_sample_tube(model):
    tube = model.Tube(name=u"simple",
        display_name=u"Simple tube for 3 fields parsing",
        description=u"""- Encloses the XML Writer in a new node that adds a Field4 column
- Modifies the XML Writer template to show that column
- Removes the CSV writer""",
        payload=u"""<config>
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
        <node type="consumer" pluginname="xmlwriter" name="writer_xml">
          <encoding>UTF-8</encoding>
          <target_filename>test_file_%Y%m%d_%H%M%S.xml</target_filename>
          <template type="embedded">
            <![CDATA[
<?xml version="1.0" encoding="UTF-8"?>
<records xmlns:py="http://genshi.edgewall.org/"
xmlns:xi="http://www.w3.org/2001/XInclude">
  <record py:for="record in datas">
    <FieldA py:content="record.Field1" />
    <FieldB py:content="record.Field2" />
    <FieldC py:content="record.Field3" />
  </record>
</records>
            ]]>
          </template>
        </node>
      </children>
    </node>
  </process>
</config>""")
    model.DBSession.add(tube)
    model.DBSession.flush()
    
    tubelayer = model.TubeLayer(
        tube_id=tube.id,
        name=u"recap_adder",
        variant_name="sample",
        display_name=u"Adds a recapitulative column",
        description=u"",
        active=True,
        payload=u"""<modifiers>
  <modifier target="writer_xml" action="enclose">
    <node type="adapter" from="code" name="field4_adder">
      <code type="function">
        <![CDATA[
def iterator(input):
    for i, value in enumerate(input):
        setattr(value, 'Field4', str(i*2))
        yield value
]]>
      </code>
    </node>
  </modifier>
  <modifier target="writer_xml" action="modify">
    <template type="embedded">
      <![CDATA[
<?xml version="1.0" encoding="UTF-8"?>
<records xmlns:py="http://genshi.edgewall.org/"
xmlns:xi="http://www.w3.org/2001/XInclude">
  <record py:for="record in datas">
    <FieldA py:content="record.Field1" />
    <FieldB py:content="record.Field2" />
    <FieldC py:content="record.Field3" />
    <FieldD py:content="record.Field4" />
  </record>
</records>
            ]]>
    </template>
  </modifier>
  <modifier target="writer_csv" action="remove" />
</modifiers>""")
    model.DBSession.add(tubelayer)
    model.DBSession.flush()
    
    return tube, tubelayer

def setup_dispatch(model, display_name, tube, descriptor,
                   variant_name):
    dispatch = model.Dispatch(display_name=display_name,
                              name=display_name.lower().replace(' ', '_'),
                              description=u"",
                              tube_id=tube.id,
                              descriptor_id=descriptor.id,
                              variant_name=variant_name)
    model.DBSession.add(dispatch)
    model.DBSession.flush()
    return dispatch
