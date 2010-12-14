# Copyright (c) 2003-2010 gocept gmbh & co. kg, http://www.gocept.com
# Christian Zagrodnick, cz@gocept.com
# See also LICENSE.txt

from tcm2sql.Constraint import Constraint
from tcm2sql.Relation import Relation
from tcm2sql.SSDReader import SSDReader
from tcm2sql.Table import Table
import os
import unittest


class TestSSDReader(unittest.TestCase):

    ssd_filename = os.path.join(os.path.dirname(__file__), 'test.ssd')

    def test_read(self):
        self.assertRaises(IOError, SSDReader, 'does-not-exist')
        ssd = SSDReader(self.ssd_filename)
        ssd.build(1)
        pet = ssd.tables['Pet']
        self.assertEquals(len(pet.attrlist), 4)
        self.assertEquals(len(pet.pklist), 1)
        self.assertEquals(len(pet.fklist), 1)
        self.assertEquals(ssd.table_name_mapping[('test.ssd', '1')],
            'Pet')

        r = ssd.relations[0]
        self.assertEquals(r.table1, 'Person')
        self.assertEquals(r.table2, 'Family')
        self.assertEquals(r.field1, 'Family_id')
        self.assertEquals(r.field2, 'id')

        r = ssd.relations[1]
        self.assertEquals(r.table1, 'Pet')
        self.assertEquals(r.table2, 'Person')
        self.assertEquals(r.field1, 'owner')
        self.assertEquals(r.field2, 'id')


class TestTable(unittest.TestCase):

    attrs = ['"#id: serial"',
        '"name: varchar"',
        '"~owner: integer"',
        '"gender: char(1)"',
        ]

    constraints = [
        '"foo: bar"',
        '<ext>',
        ]

    annotations = [r'''"This is a nice Pet.\r\rBut be aware that\r? invalidGender: check (gender in ('m','f'))\ris a constraint, whereas the <ext> is beeing ignored."''']

    def test_attributes(self):
        t = Table()
        t._update_attributes(self.attrs)
        self.assertEqual(len(t.pklist), 1)
        self.assertEqual(t.pklist[0], 'id')
        self.assertEqual(len(t.flaglist), 4)
        self.assertEqual(t.flaglist[0], ('id', '#'))
        self.assertEqual(t.flaglist[1], ('name', ''))
        self.assertEqual(t.flaglist[2], ('owner', '~'))
        self.assertEqual(t.flaglist[3], ('gender', ''))

        t = Table()
        t._update_attributes([])
        self.assertEqual(len(t.pklist), 0)

    def test_constraints(self):
        t = Table()
        t.name = 'somename'
        self.assertEquals(len(t.pklist), 0)
        t._update_constraints(self.constraints)
        self.assertEquals(len(t.pklist), 0)
        self.assertEquals(len(t.clist), 1)
        self.assert_(isinstance(t.clist[0], Constraint))
        self.assertEquals(t.clist[0].name, 'somename_foo')
        self.assertEquals(t.clist[0].rule, 'bar')

        t = Table()
        t.name = 'somename'
        self.assertEquals(len(t.pklist), 0)
        t._update_attributes(self.attrs)
        self.assertEquals(len(t.pklist), 1)
        t._update_constraints(self.constraints)
        self.assertEquals(len(t.pklist), 1)
        self.assertEquals(len(t.clist), 2)
        self.assert_(isinstance(t.clist[0], Constraint))
        self.assertEquals(t.clist[0].name, 'PK_somename')
        self.assert_(isinstance(t.clist[1], Constraint))
        self.assertEquals(t.clist[1].name, 'somename_foo')
        self.assertEquals(t.clist[1].rule, 'bar')


    def test_constraints_from_annotations(self):
        t = Table()
        t.name = 'aname'
        t._update_constraints_from_annotations(self.annotations)
        self.assertEquals(len(t.clist), 1)
        self.assertEquals(t.clist[0].name, 'aname_invalidGender')
        self.assertEquals(t.clist[0].rule, "check (gender in ('m','f'))")


class TestRelation(unittest.TestCase):

    def test_init(self):
        r = Relation(Relation.BINARY)
        self.assertEquals(r.kind, Relation.BINARY)
        self.assertRaises(ValueError, Relation, 4)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSSDReader))
    suite.addTest(unittest.makeSuite(TestTable))
    suite.addTest(unittest.makeSuite(TestRelation))
    return suite
