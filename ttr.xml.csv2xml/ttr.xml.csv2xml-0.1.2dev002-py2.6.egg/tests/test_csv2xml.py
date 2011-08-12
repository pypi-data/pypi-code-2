'''
Created on 3.7.2011

@author: javl
'''

'''CSV string into XML string
==========================

Simple case could be:
    >>> from jvxmlutils.csv2xml import string2xml
    >>> csv_str = """a;b;c
    ... 1;2;3
    ... 11;22;33
    ... 111;222;333"""
    >>> print string2xml(csv_str, delimiter = ";")
    <root><row><a>1</a><b>2</b><c>3</c></row><row><a>11</a><b>22</b><c>33</c></row><row><a>111</a><b>222</b><c>333</c></row></root>

If you like to specify output encoding (default is UTF-8), tell it by encoding parameter
    >>> print string2xml(csv_str, delimiter = ";", encoding = "windows-1250")
    <?xml version='1.0' encoding='windows-1250'?>
    <root><row><a>1</a><b>2</b><c>3</c></row><row><a>11</a><b>22</b><c>33</c></row><row><a>111</a><b>222</b><c>333</c></row></root>


'''

import unittest
from ttr.xml.csv2xml import string2xml, Csv2Xml
import csv
import StringIO
import xml.etree.cElementTree as ElementTree

class DialectSemicolon(csv.Dialect):
    """Describes properties of my CSV format"""
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_NONE


class Test(unittest.TestCase):
    def setUp(self):
        self.csv_1_string = """a;b;c
1;2;3
11;22;33
111;222;333"""
        self.csv_2_string = """a,b,c
1,2,3
11,22,33
111,222,333"""
        self.buff_1 = StringIO.StringIO(self.csv_1_string)
        self.buff_2 = StringIO.StringIO(self.csv_2_string)
        return

    def tearDown(self):
        pass

    def test_named_registered_dialect(self):
        """Testing how dialect_registration works. Not really testing my code.
        """
        dialect_name = "ponaszimu"
        csv.register_dialect(dialect_name, delimiter = "|", quoting = csv.QUOTE_NONE)
        csv.register_dialect(dialect_name, delimiter = ";", quoting = csv.QUOTE_NONE)
        print csv.list_dialects()
        buff = StringIO.StringIO(self.csv_1_string)
        reader = csv.reader(buff, dialect = dialect_name)
        for line in reader:
            print line
        return
    
    def test_dialect_class(self):
        """Testing dialect as instace of Dialect subclass.
        It is only test of cvs module, not of my own code.
        """
        buff = StringIO.StringIO(self.csv_1_string)
        reader = csv.reader(buff, dialect = DialectSemicolon)
        for line in reader:
            print line
        return

    def test_string2xml(self):
        """testing function string2xml from my own code.
        """
        print string2xml(self.csv_2_string)
        return
        
    def test_class_csv2xmlstring(self):
        """
        Test of my actual parser class.
        """
        csv_parser = Csv2Xml(self.buff_1, row_num_att = "rownum", dialect = DialectSemicolon)
        res = csv_parser.as_string()
        print res
        return

    def test_class_csv2xmlstring_excel_dialect(self):
        """
        Test of my actual parser class.
        """
        csv_parser = Csv2Xml(self.buff_2, row_num_att = "rownum", dialect = "excel")
        res = csv_parser.as_string()
        print res
        return


    def test_class_csv2element(self):
        """
        Test of my actual parser class.
        """
        csv_parser = Csv2Xml(self.buff_1, row_num_att = "rownum", dialect = DialectSemicolon)
        res = csv_parser.as_element()
        result_string = ElementTree.tostring(res,"UTF-8")
        print result_string
        return
    def test_iterator(self):
        """test use of iterator, returning Elements"""
        csv_parser = Csv2Xml(self.buff_1, row_num_att = "rownum", dialect = DialectSemicolon)
        for row in csv_parser:
            print type(row)
            text = ElementTree.tostring(row, "UTF-8")
            print text
        return
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
