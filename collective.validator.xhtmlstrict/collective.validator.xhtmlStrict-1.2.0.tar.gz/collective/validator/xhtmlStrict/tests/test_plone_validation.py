import unittest
import zope.testing
	
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 
#from Products.PortalTransforms.transforms.safe_html import register

from Products.PloneTestCase import PloneTestCase as ptc

from collective.validator.xhtmlStrict.adapter import W3cStrict
from collective.validator.xhtmlStrict.interfaces.interfaces import IW3cStrict
from collective.validator.base.content.ValidationTool import ValidationTool

class TestPloneStrict(ptc.PloneTestCase):

    def test_wrong_text_result(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.getValidationResults('afgdfg')
        right = {'m:warnings': {'m:warninglist': [{'m:col': 0,
                                                   'm:line': 0,
                                                   'm:message': u'Unable to Determine Parse Mode!'},
                                                  {'m:col': 0,
                                                   'm:line': 0,
                                                   'm:message': u'DOCTYPE Override in effect!'}],
                                'm:warningcount': 2},
                 'm:errors': {'m:errorlist': [{'m:col': 0,
                                               'm:line': 1,
                                               'm:message': u'character "a" not allowed in prolog'},
                                              {'m:col': 6,
                                               'm:line': 1,
                                               'm:message': u'end of document in prolog'}],
                              'm:errorcount': 2},
                 'm:validity': False}
        self.assertEquals(result, right)

    def test_create_result_right(self):
        """try to validate a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        right = {'m:warnings': {'m:warninglist': [{'m:col': 0,
                                                   'm:line': 0,
                                                   'm:message': u'DOCTYPE Override in effect!'}],
                                'm:warningcount': 1},
                 'm:errors': {'m:errorlist': [{'m:col': 15,
                                               'm:line': 182,
                                               'm:message': u'there is no attribute "name"'},
                                              {'m:col': 57,
                                               'm:line': 185,
                                               'm:message': u'document type does not allow element "label" here; missing one of "p",\
 "h1", "h2", "h3", "h4", "h5", "h6", "div", "pre", "address", "fieldset", "ins", "del" start-tag'}],
                              'm:errorcount': 2},
                 'm:validity': False} 
        self.assertEquals(validation,right)

    def test_search(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        result = validator.search()
        self.assertEquals(len(result), 1)

    def test_empty_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.dumpErrors("")
        self.assertEquals(result, "")
  
    def test_right_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        var = {'m:line':12,'m:message':'hello world','m:col':5}
        value = []
        value.append(var)
        st = "\
<dl><dt>%s/%s</dt><br>\
<dd>row: %s, column: %s</dd><dd><em>%s</em></dd></dl>" % (1, 1, var['m:line'], var['m:col'], var['m:message'])
        result = validator.dumpErrors(value)
        self.assertEquals(result, st)

    def test_wrong_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.dumpErrors('some string')
        self.assertEquals(result, "wrong list")

    def test_report_strict(self):
        """create the report"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        result, nerr, nwarn,validity = validator.createReportPage(validation,self.folder.doc.Title(), 'www.plone.org')
        report = '\
<h2></h2>\
<pre><a href="www.plone.org">www.plone.org</a></pre>\
<p style="margin-top:0px;">Page validation failed<br>\
<h3>Found 2 errors</h3>\
<dl>\
<dt>1/2</dt><br>\
<dd>row: 182, column: 15</dd>\
<dd><em>there is no attribute "name"</em></dd>\
<dt>2/2</dt><br>\
<dd>row: 185, column: 57</dd>\
<dd><em>document type does not allow element "label" here; missing one of "p",\
 "h1", "h2", "h3", "h4", "h5", "h6", "div", "pre", "address", "fieldset", "ins", "del" start-tag</em></dd></dl>\
<h3>Found 1 warnings</h3><dl><dt>1/1</dt><br><dd>row: 0, column: 0</dd><dd><em>DOCTYPE Override in effect!</em></dd></dl></p><br>'

        self.assertEquals(result,report)
        self.assertEquals(nerr,2)
        self.assertEquals(nwarn,1)
        self.assertEquals(validity,False)

    def test_right_description(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.createDescription(5,1,2)
        self.assertEquals(result, '5 errors, 1 warnings in 2 file(s)')

    def test_right_ReportErr(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.createReportErr(2)
        self.assertEquals(result, '<h3>Found 2 errors</h3>')

    def test_right_ReportWarn(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        result = validator.createReportWarn(5)
        self.assertEquals(result, '<h3>Found 5 warnings</h3>')





    def test_mail_body(self):
        """create the report for a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cStrict(vt_context)
        self.folder.invokeFactory('Document', id='doc',title='Some Title')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        fileout,nerr,nwarn, validity = validator.createReportPage(validation,self.folder.doc.Title(), 'www.plone.org')
        result = validator.createReportMail(fileout,nerr, nwarn,1)
        right = u'\
<html>\
<head>\
<title>Portal validation</title></head>\
<body>\
<h3>Validation Results for XHTML 1.0 Strict</h3>\
<h3>2 errors, 1 warnings in 1 file(s)</h3>\
<h2>Some Title</h2>\
<pre><a href="www.plone.org">www.plone.org</a></pre>\
<p style="margin-top:0px;">Page validation failed<br>\
<h3>Found 2 errors</h3>\
<dl>\
<dt>1/2</dt><br>\
<dd>row: 182, column: 15</dd>\
<dd><em>there is no attribute "name"</em></dd>\
<dt>2/2</dt><br><dd>row: 185, column: 57</dd>\
<dd><em>document type does not allow element "label" here; missing one of "p",\
 "h1", "h2", "h3", "h4", "h5", "h6", "div", "pre", "address", "fieldset", "ins", "del" start-tag</em></dd></dl>\
<h3>Found 1 warnings</h3>\
<dl><dt>1/1</dt><br><dd>row: 0, column: 0</dd><dd><em>DOCTYPE Override in effect!</em></dd></dl></p><br><br></body></html>'

        self.assertEquals(result,right)

    
ptc.setupPloneSite()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneStrict))
    return suite

