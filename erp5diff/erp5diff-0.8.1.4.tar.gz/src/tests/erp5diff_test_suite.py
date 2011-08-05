# -*- coding: utf-8 -*-
import unittest
import pkg_resources

from ERP5Diff import ERP5Diff
from lxml import etree
from cStringIO import StringIO
erp5diff = ERP5Diff()

class TestERP5Diff(unittest.TestCase):
  """
  """

  def _assertERP5DiffWorks(self, old_xml, new_xml, expected_result_string):
    """
    """
    erp5diff.compare(old_xml, new_xml)
    result_tree = erp5diff._result
    result_string = etree.tostring(result_tree, pretty_print=True)
    self.assertEquals(result_string, expected_result_string,
                      '\n%s\n\n%s' % (result_string, expected_result_string))


  def test_textNodes(self):
    """update the texts of the three elements
    """
    old_xml = """<erp5>
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
    new_xml = """<erp5>
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
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/description">description3 &#231;sdf__sdf&#231;&#231;&#231;_df___&amp;amp;&amp;amp;&#233;]]]&#176;&#176;&#176;&#176;&#176;&#176;</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/first_name">Tatuya</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow']/time">2009/08/28 19:12:24.703 GMT+9</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_one_element(self):
    """2. update one element
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
     <description type="text">description2&#233;&#224;@  $*&amp;lt; &amp;lt; -----</description>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
     <description type="text">description3&#233;&#224;@  $*&amp;lt; &amp;lt; -----</description>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/description">description3&#233;&#224;@  $*&amp;lt; &amp;lt; -----</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_one_element_same(self):
    """3. same
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
    <subject_list type="lines">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;list id="i2"&gt;&lt;/list&gt;&lt;/marshal&gt;</subject_list>
    <first_name type="string">Kamada</first_name>
    <last_name type="string">Tatuya</last_name>
    <workflow_action id="edit_workflow">
      <actor type="string">tatuya</actor>
      <time type="date">2009/08/28 19:12:26.631 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <title type="string">Tatuya Kamada</title>
    <subject_list type="lines">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;list id="i2"&gt;&lt;/list&gt;&lt;/marshal&gt;</subject_list>
    <first_name type="string">Kamada</first_name>
    <last_name type="string">Tatuya</last_name>
    <workflow_action id="edit_workflow">
      <actor type="string">tatuya</actor>
      <time type="date">2009/08/28 19:12:26.631 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""

    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0"/>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_text_of_element_and_remove_another_element(self):
    """4. update the texts of the elements and remove an element
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description2&#233;&#224;@  $*&amp;lt; &amp;lt;&amp;lt;&amp;lt;  -----</description>
    <language type="string">en</language>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.432 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description1 --- $sdfr&#231;_sdfs&#231;df_oisfsopf</description>
    <language type="None"/>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/description">description1 --- $sdfr&#231;_sdfs&#231;df_oisfsopf</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/language/attribute::type">None</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/language"/>
  <xupdate:remove select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][2]"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_2_elements_inlcude_symbols(self):
    """5. update two elements includes some symbols
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description2&#233;&#224;@  $*&amp;lt;&amp;lt;-----&amp;gt;&amp;gt;</description>
    <language type="string">jp</language>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <description type="text">description4 sdflkmooo^^^^]]]]]{{{{{{{</description>
    <language type="string">ca</language>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/description">description4 sdflkmooo^^^^]]]]]{{{{{{{</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/language">ca</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_two_element_with_same_id(self):
    """6. update two date element which have same id
    """

    old_xml = """
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
    new_xml = """
<erp5>
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
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][2]/time">2009/08/28 19:12:40.905 GMT+9</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][3]/time">2009/08/28 19:12:40.910 GMT+9</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_insert_and_remove_elemts(self):
    """7. insert and remove elements
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313731">
    <local_role type="tokens" id="tk">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
    <local_permission type="tokens" id="Access contents information">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="Add portal content">&lt;?xml version="1.0"?&gt;</local_permission>
    <local_permission type="tokens" id="View">&lt;?xml version="1.0"?&gt;</local_permission>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
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
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
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
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_nested_xml(self):
    """8. update xml in xml
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313731">
    <local_permission type="tokens" id="View">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_permission>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313731">
    <local_permission type="tokens" id="View">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Assignee&lt;/string&gt;&lt;string&gt;Assignor&lt;/string&gt;&lt;string&gt;Associate&lt;/string&gt;&lt;string&gt;Auditor&lt;/string&gt;&lt;string&gt;Author&lt;/string&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_permission>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313731']/local_permission[@id='View']">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Assignee&lt;/string&gt;&lt;string&gt;Assignor&lt;/string&gt;&lt;string&gt;Associate&lt;/string&gt;&lt;string&gt;Auditor&lt;/string&gt;&lt;string&gt;Author&lt;/string&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_rename_element(self):
    """9. rename element
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name type="string">Tatuya</first_name>
    <last_name type="string">Kamada</last_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <given_name type="string">Tatuya</given_name>
    <family_name type="string">Kamada</family_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/first_name"/>
  <xupdate:remove select="/erp5/object[@id='313730']/last_name"/>
  <xupdate:append select="/erp5/object[@id='313730']" child="first()">
    <xupdate:element name="given_name"><xupdate:attribute name="type">string</xupdate:attribute>Tatuya</xupdate:element>
    <xupdate:element name="family_name"><xupdate:attribute name="type">string</xupdate:attribute>Kamada</xupdate:element>
  </xupdate:append>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_rename_root_element(self):
    """10. rename root element
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <id type="string">313730</id>
    <title type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    new_xml = """
<erp6>
  <object portal_type="Person" id="313730">
    <id type="string">313730</id>
    <title type="string">Tatuya Kamada</title>
  </object>
</erp6>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:rename select="/erp5">erp6</xupdate:rename>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_one_attribute(self):
    """11. Update one attribute
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_role type="tokens" id="fab">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_role type="ccc" id="fab">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_role>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/local_role[@id='fab']/attribute::type">ccc</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_two_attributes(self):
    """12. Update two attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission attr_a='aaa' type="tokens" id="View">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Assignee&lt;/string&gt;&lt;string&gt;Assignor&lt;/string&gt;&lt;string&gt;Associate&lt;/string&gt;&lt;string&gt;Auditor&lt;/string&gt;&lt;string&gt;Author&lt;/string&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_permission>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <local_permission attr_a='ccc' type="ccc" id="View">&lt;?xml version="1.0"?&gt;&lt;marshal&gt;&lt;tuple&gt;&lt;string&gt;Assignee&lt;/string&gt;&lt;string&gt;Assignor&lt;/string&gt;&lt;string&gt;Associate&lt;/string&gt;&lt;string&gt;Auditor&lt;/string&gt;&lt;string&gt;Author&lt;/string&gt;&lt;string&gt;Manager&lt;/string&gt;&lt;string&gt;Owner&lt;/string&gt;&lt;/tuple&gt;&lt;/marshal&gt;</local_permission>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::attr_a">ccc</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/local_permission[@id='View']/attribute::type">ccc</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_update_three_attributes(self):
    """13. Update three attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <title attribute_a="aaa" attribute_b="bbb" attribute_c="ccc" type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <title attribute_a="nnn" attribute_b="nnn" attribute_c="nnn" type="string">Tatuya Kamada</title>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/title/attribute::attribute_a">nnn</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/title/attribute::attribute_b">nnn</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/title/attribute::attribute_c">nnn</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_remove_one_attribute(self):
    """14. Remove one attribute
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name attribute_a="aaa" attribute_b="bbb" attribute_c="ccc" type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name attribute_a="aaa" attribute_b="bbb" type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_c"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_remove_two_attibutes(self):
    """15. Remove two attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name attribute_a="aaa" attribute_b="bbb" attribute_c="ccc" type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name attribute_a="aaa" type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_b"/>
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_c"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)


  def test_remove_three_attributes(self):
    """16. Remove three attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name attribute_a="aaa" attribute_b="bbb" attribute_c="ccc" type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <first_name type="string">Tatuya</first_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_a"/>
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_b"/>
  <xupdate:remove select="/erp5/object[@id='313730']/first_name/attribute::attribute_c"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_append_one_attribute(self):
    """17. Append one attribute
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name type="string">Kamada</last_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name attribute_a="aaa" type="string">Kamada</last_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:append select="/erp5/object[@id='313730']/last_name">
    <xupdate:attribute name="attribute_a">aaa</xupdate:attribute>
  </xupdate:append>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_append_two_attributes(self):
    """18. Append two attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name type="string">Kamada</last_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name attribute_a="aaa" attribute_b="bbb" type="string">Kamada</last_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:append select="/erp5/object[@id='313730']/last_name">
    <xupdate:attribute name="attribute_a">aaa</xupdate:attribute>
    <xupdate:attribute name="attribute_b">bbb</xupdate:attribute>
  </xupdate:append>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_append_three_attibutes(self):
    """19. Append three attributes
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name type="string">Kamada</last_name>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <last_name attribute_a="aaa" attribute_b="bbb" attribute_c="ccc" type="string">Kamada</last_name>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:append select="/erp5/object[@id='313730']/last_name">
    <xupdate:attribute name="attribute_a">aaa</xupdate:attribute>
    <xupdate:attribute name="attribute_b">bbb</xupdate:attribute>
    <xupdate:attribute name="attribute_c">ccc</xupdate:attribute>
  </xupdate:append>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_remove_element_with_same_id(self):
    """20. Remove some elements that have same id
    """

    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.432 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.434 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.432 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.430 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.428 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.426 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.430 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.428 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.426 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][2]"/>
  <xupdate:remove select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][3]"/>
  <xupdate:remove select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][4]"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_test_remove_element_with_same_id_bis(self):
    """21. Modify two elements that have same id
    """
    old_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.432 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.434 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.436 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Person" id="313730">
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/28 19:12:34.424 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/29 19:12:34.432 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/30 19:12:34.434 GMT+9</time>
    </workflow_action>
    <workflow_action id="edit_workflow">
      <time type="date">2009/08/31 19:12:34.436 GMT+9</time>
    </workflow_action>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][2]/time">2009/08/29 19:12:34.432 GMT+9</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][3]/time">2009/08/30 19:12:34.434 GMT+9</xupdate:update>
  <xupdate:update select="/erp5/object[@id='313730']/workflow_action[@id='edit_workflow'][4]/time">2009/08/31 19:12:34.436 GMT+9</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_modify_attributes_of_sequential_objects(self):
    """22. Modify attributes of sequencial objects
    """

    old_xml = """
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
    new_xml = """
<erp5>
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
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/erp5/object[2]/title">B</xupdate:update>
  <xupdate:update select="/erp5/object[3]/title">C</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_nodes_with_qnames(self):
    """23. Modify nodes with Qualified Names
    ERP5Diff should create xpath valid expression with correct prefix
    """
    old_xml = """
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
    new_xml = """
<erp5>
  <object portal_type="Test">
    <anotherprefix:title xmlns:anotherprefix="http://any_uri">A</anotherprefix:title>
  </object>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri" prefix:myattr="anyvalue">B</prefix:title>
  </object>
  <object portal_type="Test">
    <title>A</title>
  </object>
  <erp5:object portal_type="Test" xmlns:erp5="http://www.erp5.org/namespaces/erp5_object">
    <title>B</title>
  </erp5:object>
  <object portal_type="Test">
    <prefix:title xmlns:prefix="http://any_uri">C</prefix:title>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove xmlns:prefixbis="http://any_uri_bis" select="/erp5/object[2]/prefixbis:title"/>
  <xupdate:append xmlns:prefix="http://any_uri" select="/erp5/object[2]" child="first()">
    <xupdate:element name="prefix:title" namespace="http://any_uri"><xupdate:attribute name="prefix:myattr" namespace="http://any_uri">anyvalue</xupdate:attribute>B</xupdate:element>
  </xupdate:append>
  <xupdate:remove xmlns:againanotherprefix="http://any_uri" select="/erp5/object[3]/againanotherprefix:title"/>
  <xupdate:append select="/erp5/object[3]" child="first()">
    <xupdate:element name="title">A</xupdate:element>
  </xupdate:append>
  <xupdate:insert-after xmlns:erp5="http://www.erp5.org/namespaces/erp5_object" select="/erp5/object[3]">
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

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_attibutes_with_qnames(self):
    """24. Modify nodes with Qualified Names
    Works on Attributes specially
    """

    old_xml = """
<erp5>
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="A">A</title>
  </object>
</erp5>
"""
    new_xml = """
<erp5>
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="B">A</title>
  </object>
</erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update xmlns:prefix="http://any_uri" select="/erp5/object/title/attribute::prefix:attr">B</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_attibutes_with_qnames_at_root_level(self):
    """25. Modify nodes with Qualified Names at root level
    Work on Attributes specially
    """
    old_xml = """
<erp5:erp5 xmlns:erp5="http://www.erp5.org/namspaces/erp5_object" a="aaa" b="bbb">
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="A">A</title>
  </object>
</erp5:erp5>
"""
    new_xml = """
<aaa:erp5 xmlns:aaa="http://www.erp5.org/namspaces/aaa" b="bbb" >
  <object portal_type="Test">
    <title xmlns:prefix="http://any_uri" prefix:attr="B">A</title>
  </object>
</aaa:erp5>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:rename xmlns:aaa="http://www.erp5.org/namspaces/aaa" xmlns:erp5="http://www.erp5.org/namspaces/erp5_object" select="/erp5:erp5">aaa:erp5</xupdate:rename>
  <xupdate:remove xmlns:aaa="http://www.erp5.org/namspaces/aaa" select="/aaa:erp5/attribute::a"/>
  <xupdate:update xmlns:prefix="http://any_uri" xmlns:aaa="http://www.erp5.org/namspaces/aaa" select="/aaa:erp5/object/title/attribute::prefix:attr">B</xupdate:update>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_reoder_nodes_to_the_end(self):
    """26. Reorder some nodes to the end of list
    """
    old_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    new_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>3</li>
  <li>4</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/ul/li[3]"/>
  <xupdate:remove select="/ul/li[4]"/>
  <xupdate:insert-after select="/ul/li[7]">
    <xupdate:element name="li">3</xupdate:element>
    <xupdate:element name="li">4</xupdate:element>
  </xupdate:insert-after>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_reoder_nodes_form_the_end(self):
    """26. Reorder some nodes from the end of list
    """
    old_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    new_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>7</li>
  <li>8</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>9</li>
</ul>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/ul/li[7]"/>
  <xupdate:remove select="/ul/li[8]"/>
  <xupdate:insert-after select="/ul/li[2]">
    <xupdate:element name="li">7</xupdate:element>
    <xupdate:element name="li">8</xupdate:element>
  </xupdate:insert-after>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_test_reoder_nodes_at_the_beginning(self):
    """27. Reorder some nodes at the beginning
    """
    old_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    new_xml = """
<ul>
  <li>5</li>
  <li>6</li>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/ul/li[5]"/>
  <xupdate:remove select="/ul/li[6]"/>
  <xupdate:append child="first()">
    <xupdate:element name="li">5</xupdate:element>
    <xupdate:element name="li">6</xupdate:element>
  </xupdate:append>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_reorder_nodes_at_the_end(self):
    """28. Reorder some nodes at the end
    """
    old_xml = """
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
</ul>
"""
    new_xml = """
<ul>
  <li>1</li>
  <li>4</li>
  <li>5</li>
  <li>6</li>
  <li>7</li>
  <li>8</li>
  <li>9</li>
  <li>2</li>
  <li>3</li>
</ul>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove select="/ul/li[2]"/>
  <xupdate:remove select="/ul/li[3]"/>
  <xupdate:insert-after select="/ul/li[9]">
    <xupdate:element name="li">2</xupdate:element>
    <xupdate:element name="li">3</xupdate:element>
  </xupdate:insert-after>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_delete_children_with_withe_space_nodes(self):
    """29. Delete children with white-space as text nodes
    """
    old_xml = """
<object>
  <local_permission type="tokens" id="View">
     <marshal:marshal xmlns:marshal="http://www.erp5.org/namespaces/marshaller">
       <marshal:tuple>
         <marshal:string>Assignee</marshal:string>
         <marshal:string>Assignor</marshal:string>
       </marshal:tuple>
     </marshal:marshal>
   </local_permission>
 </object>
"""
    new_xml = """
<object>
  <local_permission type="tokens" id="View">
     <marshal:marshal xmlns:marshal="http://www.erp5.org/namespaces/marshaller">
       <marshal:tuple>
       </marshal:tuple>
     </marshal:marshal>
   </local_permission>
 </object>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove xmlns:marshal="http://www.erp5.org/namespaces/marshaller" select="/object/local_permission[@id='View']/marshal:marshal/marshal:tuple/marshal:string[1]"/>
  <xupdate:remove xmlns:marshal="http://www.erp5.org/namespaces/marshaller" select="/object/local_permission[@id='View']/marshal:marshal/marshal:tuple/marshal:string[2]"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_delete_children_with_auto_closing_nodes(self):
    """29Bis. Delete childrens with auto-closing nodes
    """
    old_xml = """
<object>
  <local_permission type="tokens" id="View">
     <marshal:marshal xmlns:marshal="http://www.erp5.org/namespaces/marshaller">
       <marshal:tuple>
         <marshal:string>Assignee</marshal:string>
         <marshal:string>Assignor</marshal:string>
       </marshal:tuple>
     </marshal:marshal>
   </local_permission>
 </object>
"""
    new_xml = """
<object>
  <local_permission type="tokens" id="View">
     <marshal:marshal xmlns:marshal="http://www.erp5.org/namespaces/marshaller">
       <marshal:tuple/>
     </marshal:marshal>
   </local_permission>
 </object>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:remove xmlns:marshal="http://www.erp5.org/namespaces/marshaller" select="/object/local_permission[@id='View']/marshal:marshal/marshal:tuple/marshal:string[1]"/>
  <xupdate:remove xmlns:marshal="http://www.erp5.org/namespaces/marshaller" select="/object/local_permission[@id='View']/marshal:marshal/marshal:tuple/marshal:string[2]"/>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_repalce_a_node_by_another_followed_by_modification(self):
    """30. Replace a node by another one followed by a modification
    """
    old_xml = """
<resource reference="Product Ballon de Plage a5962z">
  <title>Ballon de Plage</title>
  <reference>a5962z</reference>
  <sale_price>200.250000</sale_price>
  <purchase_price>100.250000</purchase_price>
  <category>ball_size/s4</category>
  <category>ball_size/s5</category>
  <category>colour/black</category>
  <category>colour/white</category>
  <category>type/product</category>
</resource>
"""
    new_xml = """
<resource reference="Product Ballon de Plage a5962z">
  <title>Ballon de Plage</title>
  <reference>a5962z</reference>
  <sale_price>120.000000</sale_price>
  <ean13>1357913579130</ean13><!--replace purchase_price -->
  <category>ball_size/s4</category>
  <category>ball_size/s6</category><!--first modification to trig the bug -->
  <category>colour/red</category>
  <category>colour/white</category>
  <category>type/product</category>
</resource>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/resource/sale_price">120.000000</xupdate:update>
  <xupdate:remove select="/resource/purchase_price"/>
  <xupdate:update select="/resource/category[2]">ball_size/s6</xupdate:update>
  <xupdate:update select="/resource/category[3]">colour/red</xupdate:update>
  <xupdate:insert-before select="/resource/category[1]">
    <xupdate:element name="ean13">1357913579130</xupdate:element>
  </xupdate:insert-before>
</xupdate:modifications>
"""

    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

  def test_text_node_in_tails(self):
    """31. Check tail of elements ...<node/>blablabla...
    """
    old_xml = """
<ul>
  <node/>blablabla
</ul>
"""
    new_xml = """
<ul>
  <node/>yayaya
</ul>
"""
    expected_result_string = """<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
  <xupdate:update select="/ul"><node/>yayaya
</xupdate:update>
</xupdate:modifications>
"""
    self._assertERP5DiffWorks(old_xml, new_xml, expected_result_string)

if __name__ == '__main__':
  unittest.main()
