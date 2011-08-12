'''
Created on 3.7.2011

@author: javl
'''
import unittest
from lxml import etree
import datetime
from copy import deepcopy
from ttr.xml.csv2xml import Csv2Xml

class Test(unittest.TestCase):


    def setUp(self):
        self.es_xsd_fname = "data/ElaboratedData-EventService.xsd"
        self.es_xml_fname = "data/ElaboratedData-EventService_Draft.xml"
        self.bad_es_xml_fname = "data/bad_ElaboratedData-EventService_Draft.xml"
        #self.csv_fname = "data/close_segments_3.csv"
        self.csv_fname = "data/cloase_segments_20110712tp.csv"
        self.xslt_fname = "data/ElaboratedData-EventService.xsl"
        self.csv2xml_fname = "data/csv2xml_etalon.xml"
        self.es_out_etalon = "data/es_out_etalon.xml"
        self.es_merged_fname = "data/es_merged.xml"
        self.es_out_etalon_saved = "data/es_out_etalon_saved.xml"
        self.es_out_xml_fname = "data/es_out.xml"
        
        pass


    def tearDown(self):
        pass

    def test_ctime_as_ISO(self):
        now = datetime.datetime.utcnow()
        print now
        now_str = now.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        print now_str
        print datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        return

    def test_EventService_validity_by_xsd(self):
        es_xsd = etree.parse(self.es_xsd_fname)
        xmlschema = etree.XMLSchema(es_xsd)
        es_xml = etree.parse(self.es_xml_fname)
        self.assertTrue(xmlschema.validate(es_xml))
        bad_es_xml = etree.parse(self.bad_es_xml_fname)
        self.assertFalse(xmlschema.validate(bad_es_xml))
        return
    
    def test_csv2xml(self):
        with open(self.csv_fname, "r") as f:
            convertor = Csv2Xml(f, dialect = "excel", delimiter = ";")
            res_element = convertor.as_element()
            res = etree.tostring(res_element, encoding="UTF-8", pretty_print = True)
            print res
            print len(res)
            self.assertTrue(len(res)> 0)
        out_xml_fname = "data/csv2xml.xml"
        with open(out_xml_fname, "w") as fo:
            fo.write(res)
        
        return
    def test_xslt_transformation(self):
        xslt = etree.parse(self.xslt_fname)
        transformer = etree.XSLT(xslt)
        csv2xml_xml = etree.parse(self.csv2xml_fname)
        now_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        res_tree = transformer(csv2xml_xml, publicationTimeInZulu = etree.XSLT.strparam(now_str))
        res = etree.tostring(res_tree, encoding="UTF-8", pretty_print = True)
        print res
        print len(res)
        self.assertTrue(len(res)> 0)
        out_xml_fname = "data/es_out.xml"
        with open(out_xml_fname, "w") as fo:
            fo.write(res)
    def test_merge_xmls(self):
        es_xml = etree.parse(self.es_xml_fname)
        rec_container = es_xml.find("PayloadPublication")
        self.assertEqual(rec_container.tag, "PayloadPublication")
        len_org = len(rec_container)
        self.assertTrue(len_org > 0)
        
        es_out_etalon = etree.parse(self.es_out_etalon)
        added_recs = es_out_etalon.findall("PayloadPublication/ElaboratedRecord")
        len_adding = len(added_recs)
        self.assertTrue(len_adding > 0)
 
        #rec_container.insert(0, added_recs)
        for rec_el in added_recs:
            rec_container.append(deepcopy(rec_el))
        
        new_len = len(rec_container)
        with open(self.es_merged_fname, "w") as fo:
            fo.write(etree.tostring(es_xml, encoding="UTF-8", pretty_print = True))
        self.assertEqual(new_len, len_org + len_adding)
        
        #try to serialize the original added doc to see, if any recs are missing
        #original es_out_etalon shall have still the same size
        self.assertTrue(len_adding == len(added_recs))
        
        with open(self.es_out_etalon_saved, "w") as fo2:
            fo2.write(etree.tostring(es_out_etalon, encoding="UTF-8", pretty_print = True))

    def csv2xml(self, csv_fname):
        with open(csv_fname, "r") as f:
            convertor = Csv2Xml(f, dialect = "excel", delimiter = ";")
            return convertor.as_element()
            

    def csv2xml2es(self, csv2xml_xml):
        xslt = etree.parse(self.xslt_fname)
        transformer = etree.XSLT(xslt)
        now_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        now_str_quoted = etree.XSLT.strparam(now_str)
        return transformer(csv2xml_xml, publicationTimeInZulu = now_str_quoted)
    
    def validate_es(self, es_xml):
        es_xsd = etree.parse(self.es_xsd_fname)
        xmlschema = etree.XMLSchema(es_xsd)
        xmlschema.assertValid(es_xml)
        return
    
    def test_validate_csv_and_publish(self):
        csv_fname = self.csv_fname
        es_out_xml_fname = self.es_out_xml_fname
        #read csv file in
        try:
            csv2xml_xml = self.csv2xml(csv_fname)
        except Exception, err:
            msg = "Unable to read csv file. Problem: "
            raise Exception(msg + err)
        #convert the file into EventService
        try:
            es_xml = self.csv2xml2es(csv2xml_xml)
        except Exception, err:
            msg = "Unable to transform csv2xml xml into EventService.xml. Problem: "
            raise Exception(msg + err)
        #validate, if resulting es xml is really valid
        try:
            self.validate_es(es_xml)
        except Exception, err:
            msg = "Resulting EventService.xml is not valid: Problem: "
            print msg
            raise
        print "Congratulations: csv file was validated."
        #saving valid EventService.xml for reference
        #there is no other use for this, user can just see, what he created
        with open(es_out_xml_fname, "w") as fo:
            fo.write(etree.tostring(es_xml, encoding = "UTF-8", pretty_print = True))
        print "EventService.xml file created from csv file saved to disk: %s"  % es_out_xml_fname
        #todo: publish validated csv to aws
        return

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()