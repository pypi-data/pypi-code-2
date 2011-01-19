# -*- coding: utf-8 -*-
import unittest
import pkg_resources

from ERP5Diff import ERP5Diff
import xupdate_processor
from xupdate_processor import applyXUpdate
from lxml import etree
from cStringIO import StringIO

class TestXUpdateProcessor(unittest.TestCase):
  """
  """

  def _assertXUprocWorks(self, xml_xu_string, xml_doc_string, expected_result_string):
    """
    """
    result_tree = applyXUpdate(xml_xu_string=xml_xu_string,
                              xml_doc_string=xml_doc_string)
    result_string = etree.tostring(result_tree, pretty_print=True)
    self.assertEquals(result_string, expected_result_string,
                      '\n%s\n\n%s' % (result_string, expected_result_string))


  def test_textNodes(self):
    """Update text nodes
    """
    xml_doc_string = """<?xml version="1.0"?>
<erp5>
  <object portal_type="Test">
    <title>A</title>
  </object>
  <object portal_type="Test">
    <title>A</title>
  </object>
  <object portal_type="Test">
    <title>A</title>
  </object>
</erp5>
"""

    xml_xu_string = """<?xml version="1.0"?>
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[2]/title">B</xupdate:update>
  <xupdate:update select="/erp5/object[3]/title">C</xupdate:update>
</xupdate:modifications>
"""

    expected_result_string = """<erp5>
  <object portal_type="Test">
    <title>A</title>
  </object>
  <object portal_type="Test">
    <title>B</title>
  </object>
  <object portal_type="Test">
    <title>C</title>
  </object>
</erp5>
"""

    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_TextNodesWithSpecialchars(self):
    """Update Text Node with special chars and entities
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description1 --- $sdfr&#231;_sdfs&#231;df_oisfsopf</description>
    <first_name type="string">Kamada</first_name>
    <last_name type="string">Kamada</last_name>
      <workflow_action id="edit_workflow">
        <time type="date">2009/08/28 19:12:24.700 GMT+9</time>
      </workflow_action>
  </object>
</erp5>
"""

    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/description">description3 çsdf__sdfççç_df___&amp;amp;&amp;amp;é]]]°°°°°°</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/first_name">Tatuya</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow']/time">2009/08/28 19:12:24.703 GMT+9</xupdate:update>
</xupdate:modifications>
"""

    expected_result_string = """<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description3 &#231;sdf__sdf&#231;&#231;&#231;_df___&amp;amp;&amp;amp;&#233;]]]&#176;&#176;&#176;&#176;&#176;&#176;</description>
    <first_name type="string">Tatuya</first_name>
    <last_name type="string">Kamada</last_name>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:24.703 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_sameID(self):
    """update two dates element which have the same id
    """

    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.550 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.903 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.907 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][2]/time">2009/08/28 19:12:40.905 GMT+9</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][3]/time">2009/08/28 19:12:40.910 GMT+9</xupdate:update>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.550 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.905 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:40.910 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""

    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_insertandRemove(self):
    """insert and remove elements
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313731">
    <local_role type="tokens" id="tk">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
    <local_permission type="tokens" id="Access contents information">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="Add portal content">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="View">&lt;?xml version="1.0"?&gt;</local_permission>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
 <xupdate:remove select="/erp5/object[@id='313731']/local_role[@id='tk']"/>
 <xupdate:append select="/erp5/object[@id='313731']" child="first()">
   <xupdate:element name="local_role"><xupdate:attribute name="type">tokens</xupdate:attribute><xupdate:attribute name="id">tatuya</xupdate:attribute>&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</xupdate:element>                                                  
   <xupdate:element name="JohnDoe">Go to the beach</xupdate:element>
 </xupdate:append>
 <xupdate:insert-before select="/erp5/object[@id='313731']/local_permission[@id='View']">
   <xupdate:element name="local_permission"><xupdate:attribute name="type">tokens</xupdate:attribute><xupdate:attribute name="id">Manage portal content</xupdate:attribute>&lt;?xml version="1.0"?&gt;</xupdate:element>
 </xupdate:insert-before>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313731">
    <local_role type="tokens" id="tatuya">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
    <JohnDoe>Go to the beach</JohnDoe>
    <local_permission type="tokens" id="Access contents information">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="Add portal content">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="Manage portal content">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="View">&lt;?xml version="1.0"?&gt;</local_permission>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_renameElement(self):
    """rename element
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <id type="string">313730</id>
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:rename select="/erp5">erp6</xupdate:rename>
</xupdate:modifications>
"""
    expected_result_string =  """<erp6>
  <object portal_type="Person" id="313730">
    <id type="string">313730</id>
    <title type="string">Tatuya Kamada</title>
  </object>
</erp6>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_updateAttribute(self):
    """Update attribute
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_role type="tokens" id="fab">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/local_role[@id='fab']/attribute::type">ccc</xupdate:update>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <local_role type="ccc" id="fab">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_updateTwoAttributes(self):
    """update Two attributes
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission attr_a='aaa' type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::attr_a">ccc</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::type">ccc</xupdate:update>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <local_permission attr_a="ccc" type="ccc" id="View">Data</local_permission>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_removeTwoAttributes(self):
    """remove two attributes
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission attr_a="aaa" attr_b="bbb" type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::attr_a"/>
  <xupdate:remove select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::attr_b"/>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <local_permission type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_insterBefore(self):
    """inster-before
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:insert-before select="/erp5/object[@id='313730']">
    <object id="313731"/>
    <object id="313732"/>
    <object id="313733"/>
  </xupdate:insert-before>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object id="313731"/>
  <object id="313732"/>
  <object id="313733"/>
  <object portal_type="Person" id="313730">
    <local_permission type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_insertAfter(self):
    """inster-after
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission type="tokens" id="View">Data</local_permission>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:insert-after select="/erp5/object[@id='313730']">
    <object id="313731"/>
    <object id="313732"/>
    <object id="313733"/>
  </xupdate:insert-after>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <local_permission type="tokens" id="View">Data</local_permission>
  </object>
  <object id="313731"/>
  <object id="313732"/>
  <object id="313733"/>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_NamspaceAware(self):
    """Namespace handling
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri">A</prefix:title>
  </object>
  <object portal_type="Test">
    <prefixbis:title xmlns:prefixbis="http://any_uri_bis">A</prefixbis:title>
  </object>
  <object portal_type="Test">
    <againanotherprefix:title xmlns:againanotherprefix="http://any_uri">A</againanotherprefix:title>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove xmlns:prefixbis="http://any_uri_bis" select="/erp5/object[2]/prefixbis:title"/>
  <xupdate:append select="/erp5/object[2]" child="first()">
    <xupdate:element name="prefix:title" namespace="http://any_uri"><xupdate:attribute name="prefix:myattr" namespace="http://any_uri">anyvalue</xupdate:attribute>B</xupdate:element>
  </xupdate:append>
  <xupdate:remove xmlns:againanotherprefix="http://any_uri" select="/erp5/object[3]/againanotherprefix:title"/>
  <xupdate:append select="/erp5/object[3]" child="first()">
    <xupdate:element name="title">A</xupdate:element>
  </xupdate:append>
  <xupdate:insert-after select="/erp5/object[3]">
    <xupdate:element name="erp5:object" namespace="http://www.erp5.org/namespaces/erp5_object">
      <xupdate:attribute name="portal_type">Test</xupdate:attribute>
      <title>B</title>
    </xupdate:element>
    <xupdate:element name="object">
      <xupdate:attribute name="portal_type">Test</xupdate:attribute>
      <prefix:title xmlns:prefix="http://any_uri">C</prefix:title>
    </xupdate:element>
  </xupdate:insert-after>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri">A</prefix:title>
  </object>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri" prefix:myattr="anyvalue">B</prefix:title>
  </object>
  <object portal_type="Test">
    <title>A</title>
  </object>
  <erp5:object xmlns:erp5="http://www.erp5.org/namespaces/erp5_object" portal_type="Test">
    <title>B</title>
  </erp5:object>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri">C</prefix:title>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_ModifyAttributesWithQualifiedName(self):
    """Modify Attributes with Qualified Name
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="A">A</title>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update xmlns:prefix="http://any_uri" select="/erp5/object/title/attribute::prefix:attr">B</xupdate:update>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="B">A</title>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_ModifyNodesAtRootLevel(self):
    """Modify nodes with Qualified Names at root level
    """
    xml_doc_string = """
<erp5:erp5 xmlns:erp5="http://www.erp5.org/namspaces/erp5_object" a="aaa" b="bbb">
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="A">A</title>
  </object>
</erp5:erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:rename xmlns:aaa="http://www.erp5.org/namspaces/aaa" xmlns:erp5="http://www.erp5.org/namspaces/erp5_object" select="/erp5:erp5">aaa:erp5</xupdate:rename>
  <xupdate:remove xmlns:aaa="http://www.erp5.org/namspaces/aaa" select="/aaa:erp5/attribute::a"/>
  <xupdate:update xmlns:prefix="http://any_uri" xmlns:aaa="http://www.erp5.org/namspaces/aaa" select="/aaa:erp5/object/title/attribute::prefix:attr">B</xupdate:update>
</xupdate:modifications>
"""
    expected_result_string =  """<aaa:erp5 xmlns:aaa="http://www.erp5.org/namspaces/aaa" b="bbb">
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="B">A</title>
  </object>
</aaa:erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_NodeCreationWithMultipleSubElements(self):
    """check that creation of new node with multiple sub elements,
    will not append them in reverse order
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Test"/>
  <object1/>
  <object2/>
  <object3/>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
   <xupdate:insert-after select="/erp5/object[1]">
    <xupdate:element name="workflow_action">
      <xupdate:attribute name="id">edit_workflow</xupdate:attribute>
      <action type="string">edit</action>
      <comment type="None"/>
      <error_message type="string"/>
      <state type="string">current</state>
    </xupdate:element>
  </xupdate:insert-after>
  <xupdate:insert-after select="/erp5/object1">
    <action type="string">edit</action>
    <comment type="None"/>
    <error_message type="string"/>
    <state type="string">current</state>
  </xupdate:insert-after>
  <xupdate:insert-before select="/erp5/object3">
    <action type="string">edit</action>
    <comment type="None"/>
    <error_message type="string"/>
    <state type="string">current</state>
  </xupdate:insert-before>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Test"/>
  <workflow_action id="edit_workflow">
    <action type="string">edit</action>
    <comment type="None"/>
    <error_message type="string"/>
    <state type="string">current</state>
  </workflow_action>
  <object1/>
  <action type="string">edit</action>
  <comment type="None"/>
  <error_message type="string"/>
  <state type="string">current</state>
  <object2/>
  <action type="string">edit</action>
  <comment type="None"/>
  <error_message type="string"/>
  <state type="string">current</state>
  <object3/>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_PI_and_Comments(self):
    """processing-instruction and comments
    """
    xml_doc_string = """
 <erp5>
   <object portal_type="Person" id="313730">
     <id type="string">313730</id>
     <title type="string">Tatuya Kamada</title>
   </object>
 </erp5>
 """
    xml_xu_string = """
 <xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
   <xupdate:insert-after select="/erp5/object[@id='313730']">
     <xupdate:processing-instruction name="aaa">type="aaa"</xupdate:processing-instruction>
     <xupdate:comment>This text is a comment</xupdate:comment>
   </xupdate:insert-after>
 </xupdate:modifications>
 """
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <id type="string">313730</id>
    <title type="string">Tatuya Kamada</title>
  </object>
  <?aaa type="aaa"?>
  <!--This text is a comment-->
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_variables(self):
    """variables
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:variable name="person" select="/erp5/object[@id='313730']"/>
  <xupdate:insert-after select="/erp5/object[@id='313730']">
    <xupdate:value-of select="$person"/>
  </xupdate:insert-after>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_valueOf(self):
    """value-of
    """
    xml_doc_string = """
<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    xml_xu_string = """
<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:insert-after select="/erp5/object[@id='313730']">
    <xupdate:value-of select="/erp5/object[@id='313730']"/>
  </xupdate:insert-after>
</xupdate:modifications>
"""
    expected_result_string =  """<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    self._assertXUprocWorks(xml_xu_string, xml_doc_string,
                            expected_result_string)

  def test_OOofiles1(self):
    """
    """
    orig_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/test_ooo_1.xml')
    xu_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/xu_ooo_1.xml')
    destination_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/dest_ooo_1.xml')

    result_tree = applyXUpdate(xml_xu_filename=xu_filename,
                               xml_doc_filename=orig_filename)
    destination_tree = etree.parse(destination_filename)
    destination_buffer = StringIO()
    result_buffer = StringIO()
    destination_tree.write_c14n(destination_buffer)
    result_tree.write_c14n(result_buffer)
    erp5diff = ERP5Diff()
    erp5diff.compare(result_buffer.getvalue(), destination_buffer.getvalue())
    self.assertEquals(etree.tostring(erp5diff._result),
    '<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0"/>')

  def test_OOofiles2(self):
    """
    """
    orig_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/test_ooo_2.xml')
    xu_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/xu_ooo_2.xml')
    destination_filename = pkg_resources.resource_filename(
                            xupdate_processor.xuproc.__name__,
                            'tests/dest_ooo_2.xml')
    result_tree = applyXUpdate(xml_xu_filename=xu_filename, xml_doc_filename=orig_filename)
    destination_tree = etree.parse(destination_filename)
    destination_buffer = StringIO()
    result_buffer = StringIO()
    destination_tree.write_c14n(destination_buffer)
    result_tree.write_c14n(result_buffer)

    erp5diff = ERP5Diff()
    erp5diff.compare(result_buffer.getvalue(), destination_buffer.getvalue())
    self.assertEquals(etree.tostring(erp5diff._result),
    '<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0"/>')


if __name__ == '__main__':
  unittest.main()