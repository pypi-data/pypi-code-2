# Copyright (c) 2003-2010 gocept gmbh & co. kg, http://www.gocept.com
# Christian Zagrodnick, cz@gocept.com
# See also LICENSE.txt

from StringIO import StringIO
from tcm2sql.tcmfile import TCMFile
import unittest


class TestTCMReader(unittest.TestCase):
    section_contents = """{
            { Foo "1" }
            { Foo "2" }
            { Bar Baz }
            }
        """

    def test_nextline(self):
        f = StringIO("Line1\nLine 2\nLine 3\n")
        tcm = TCMFile(f)
        self.assertEquals(tcm._line, '')
        tcm._next_line()
        self.assertEquals(tcm._line, 'Line1')
        tcm._next_line()
        self.assertEquals(tcm._line, 'Line 2')
        tcm._next_line()
        self.assertEquals(tcm._line, 'Line 3')
        tcm._next_line()
        self.assertEquals(tcm._line, None)

    def test_parse_line(self):
        f = StringIO(self.section_contents)
        tcm = TCMFile(f)
        self.assertEquals(tcm._parse_line(), None)
        self.assertEquals(tcm._parse_line(), ('Foo', '"1"'))
        self.assertEquals(tcm._parse_line(), ('Foo', '"2"'))
        self.assertEquals(tcm._parse_line(), ('Bar', 'Baz'))
        self.assertEquals(tcm._parse_line(), None)

    def test_parse_section(self):
        f = StringIO(self.section_contents)
        tcm = TCMFile(f)
        section = tcm._parse_section('Section', '24')
        self.assertEquals(section['_id'], '24')
        self.assertEquals(section['_name'], 'Section')
        self.assertEquals(section['Foo'], ['"1"', '"2"'])
        self.assertEquals(section['Bar'], ['Baz'])
        self.assertEquals(len(section.keys()), 4)

    def test_parse_toplevel(self):
        tcm_contents = """
            Foo
            {
                { Bla Fasel }
            }

            # THIS IS A COMMENT

            Foo 2
            {
                { Bar Baz }
            }

            Bar
            {
                { Asdf jkl }
            }
        """
        f = StringIO(tcm_contents)
        tcm = TCMFile(f)
        parsed = tcm._parse_toplevel()
        self.assertEquals(len(parsed.keys()), 2)
        self.assertEquals(len(parsed['Foo']), 2)
        self.assertEquals(len(parsed['Bar']), 1)
        self.assertEquals(parsed['Foo'][1]['_id'], '2')
        self.assertEquals(parsed['Foo'][0]['_name'], 'Foo')
        self.assertEquals(parsed['Bar'][0]['_id'], None)
        self.assertEquals(parsed['Bar'][0]['_name'], 'Bar')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTCMReader))
    return suite
