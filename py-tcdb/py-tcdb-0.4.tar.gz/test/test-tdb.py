# -*- coding: utf-8 -*-

import datetime
import os
import random
import unittest
import warnings

from tcdb import tdb
from tcdb import util


class TestTDB(unittest.TestCase):
    def setUp(self):
        self.tdb = tdb.TDB()
        self.tdb.open('test.tdb', bnum=131071, lcnum=4096, xmsiz=67108864)

    def tearDown(self):
        self.tdb.close()
        self.tdb = None
        os.remove('test.tdb')

    def test_setgetitem(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb[pk] = self.row(pk)
            row = self.tdb[pk]
            self.assertEqual(self.row(pk), row)
        self.assertRaises(KeyError, self.tdb.__getitem__, 'nonexistent key')

    def test_put(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.put(pk, self.row(pk))
            row = self.tdb.get(pk)
            self.assertEqual(self.row(pk), row)
            self.tdb.put(pk, self.row(pk), raw_key=True)
            row = self.tdb.get(pk, raw_key=True)
            self.assertEqual(self.row(pk), row)
            self.tdb.put(pk, self.row(pk), raw_cols=True)
            row = self.tdb.get(pk, schema=self.schema(pk))
            self.assertEqual(self.row(pk), row)
        self.assertEqual(self.tdb.get('nonexistent key'), None)
        self.assertEqual(self.tdb.get('nonexistent key', 'def'), 'def')

    def test_putkeep(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.putkeep(pk, self.row(pk))
            row = self.tdb.get(pk)
            self.assertEqual(self.row(pk), row)
            self.tdb.putkeep(pk, self.row('random value'))
            row = self.tdb.get(pk)
            self.assertEqual(self.row(pk), row)
            self.tdb.putkeep(pk, self.row(pk), raw_key=True)
            row = self.tdb.get(pk, raw_key=True)
            self.assertEqual(self.row(pk), row)
            self.tdb.putkeep(pk, self.row('random value'), raw_key=True)
            row = self.tdb.get(pk, raw_key=True)
            self.assertEqual(self.row(pk), row)
            self.tdb.put(pk, self.row(pk), raw_cols=True)
            row = self.tdb.get(pk, schema=self.schema(pk))
            self.assertEqual(self.row(pk), row)
            self.tdb.putkeep(pk, self.row('random value'), raw_cols=True)
            row = self.tdb.get(pk, schema=self.schema(pk))
            self.assertEqual(self.row(pk), row)

    def test_putcat(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.putcat(pk, self.row(pk))
            row = self.tdb.get(pk)
            self.assertEqual(self.row(pk), row)
            ext_row = self.row(pk)
            ext_row['new key'] = 'new value'
            self.tdb.putcat(pk, {'new key': 'new value'})
            row = self.tdb.get(pk)
            self.assertEqual(ext_row, row)

            self.tdb.put(pk, self.row(pk), raw_key=True)
            row = self.tdb.get(pk, raw_key=True)
            self.assertEqual(self.row(pk), row)
            ext_row = self.row(pk)
            ext_row['new key'] = 'new value'
            self.tdb.putcat(pk, {'new key': 'new value'}, raw_key=True)
            row = self.tdb.get(pk, raw_key=True)
            self.assertEqual(ext_row, row)

            self.tdb.put(pk, self.row(pk), raw_cols=True)
            row = self.tdb.get(pk, schema=self.schema(pk))
            self.assertEqual(self.row(pk), row)
            ext_row = self.row(pk)
            ext_row['new key'] = 'new value'
            ext_schema = self.schema(pk)
            ext_schema['new key'] = str
            self.tdb.putcat(pk, {'new key': 'new value'}, raw_cols=True)
            row = self.tdb.get(pk, schema=ext_schema)
            self.assertEqual(ext_row, row)

    def test_out_and_contains(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.put(pk, self.row(pk))
            self.assert_(pk in self.tdb)
            self.tdb.out(pk)
            self.assert_(pk not in self.tdb)

        for pk in pks:
            self.tdb.put(pk, self.row(pk))
            self.assert_(pk in self.tdb)
            del self.tdb[pk]
            self.assert_(pk not in self.tdb)

    def test_get_col(self):
        row = self.row('some text')
        self.tdb.put('pk', row)
        for k, v in row.items():
            self.assertEqual(self.tdb.get_col('pk', k), v)

        self.tdb.put('pk', row, raw_cols=True)
        self.assertEqual(self.tdb.get_col('pk', 'object'), 1+1j)
        self.assertEqual(self.tdb.get_col('n key', 'n col'), None)
        self.assertEqual(self.tdb.get_col('n key', 'n col', 'def'), 'def')

        self.assertEqual(self.tdb.get_col_str('pk', 'str'), 'string')
        self.assertEqual(self.tdb.get_col_str('n key', 'n col'), None)
        self.assertEqual(self.tdb.get_col_str('n key', 'n col', 'def'), 'def')

        self.assertEqual(self.tdb.get_col_unicode('pk', 'unicode'), u'unicode')
        self.assertEqual(self.tdb.get_col_unicode('n key', 'n col'), None)
        self.assertEqual(self.tdb.get_col_unicode('n key', 'n col','def'), 'def')

        self.assertEqual(self.tdb.get_col_int('pk', 'int'), 10)
        self.assertEqual(self.tdb.get_col_int('n key', 'n col'), None)
        self.assertEqual(self.tdb.get_col_int('n key', 'n col', 'def'), 'def')

        self.assertEqual(self.tdb.get_col_float('pk', 'float'), 10.10)
        self.assertEqual(self.tdb.get_col_float('n key', 'n col'), None)
        self.assertEqual(self.tdb.get_col_float('n key', 'n col', 'def'), 'def')

    def test_vsiz(self):
        pk = 'random text'
        self.tdb.put(pk, self.row(pk))
        vsiz = self.tdb.vsiz(pk)
        self.assertEqual(vsiz, 154)

        self.tdb.put(pk, self.row(pk), raw_cols=True)
        vsiz = self.tdb.vsiz(pk)
        self.assertEqual(vsiz, 146)

    def test_iters(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        pks = [1+1j]
        cols = []
        for pk in pks:
            self.tdb.put(pk, self.row(pk))
            cols.append(self.row(pk))

        self.assertEqual(self.tdb.keys(), pks)
        self.assertEqual(self.tdb.values(), cols)
        self.assertEqual(zip(pks, cols), self.tdb.items())

        for key in self.tdb:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(key in pks)

        for col in self.tdb.itervalues():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(col in cols)

    def test_fwmkeys(self):
        pks = ['aa', 'ab', 'ac', 'xx', 'ad']
        for pk in pks:
            self.tdb.put(pk, {'value': 'some value'}, raw_key=True)
        self.assertEqual(self.tdb.fwmkeys('a'), ['aa', 'ab', 'ac', 'ad'])
        self.assertEqual(self.tdb.fwmkeys('x'), ['xx'])
        self.assertEqual(self.tdb.fwmkeys('nonexistent key'), [])

    def test_add_int(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.put(pk, {'v': 'v', '_num': '10'}, raw_cols=True)
        for key in self.tdb:
            self.tdb.add_int(key, 2)
        for key in self.tdb:
            self.assertEqual(self.tdb.get_col_str(key, '_num'), '12')

    def test_add_float(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.put(pk, {'v': 'v', '_num': '10.10'}, raw_cols=True)
        for key in self.tdb:
            self.tdb.add_float(key, 2.0)
        for key in self.tdb:
            self.assertEqual(self.tdb.get_col_str(key, '_num'), '12.1')

    def test_admin_functions(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for pk in pks:
            self.tdb.put(pk, self.row(pk))

        self.assertEquals(self.tdb.path(), 'test.tdb')

        self.tdb.sync()
        self.assertEquals(len(self.tdb), 5)
        self.assertEquals(self.tdb.fsiz(), 529760)

        self.tdb.vanish()
        self.assertEquals(self.tdb.fsiz(), 528704)

        self.assert_(self.tdb.memsync(True))
        # self.assert_(self.tdb.cacheclear())
        self.assertEquals(self.tdb.bnum(), 131071)
        self.assertEquals(self.tdb.align(), 16)
        self.assertEquals(self.tdb.fbpmax(), 1024)

        self.assert_(self.tdb.optimize(bnum=147451))
        self.assertEquals(self.tdb.bnum(), 147451)
        self.assertEquals(self.tdb.align(), 16)
        self.assertEquals(self.tdb.fbpmax(), 1024)

        self.assert_(self.tdb.inode())
        self.assert_((datetime.datetime.now()-self.tdb.mtime()).seconds <= 1)
        self.assertEquals(self.tdb.flags(), tdb.FOPEN)
        self.assertEquals(self.tdb.opts(), 0)
        self.assertEquals(self.tdb.opaque(), '')
        self.assertEquals(self.tdb.bnumused(), 0)
        self.assertEquals(self.tdb.dfunit(), 0)
        self.assert_(self.tdb.defrag(5))

    def test_transaction(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        with self.tdb as db:
            for pk in pks:
                db.put(pk, {'value': 'some text'})
        self.assertEquals(len(self.tdb), 5)
        self.tdb.vanish()
        try:
            with self.tdb:
                for pk in pks:
                    self.tdb.put(pk, {'value': 'some text'})
                self.tdb['Not exist key']
        except KeyError:
            pass
        self.assertEquals(len(self.tdb), 0)

    def test_foreach(self):
        pks = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]

        def proc(key, value, op):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(key in pks)
            self.assertEquals(op, 'test')
            return True

        for pk in pks:
            self.tdb.put(pk, self.row(pk))
        self.tdb.foreach(proc, 'test')

    def test_qry(self):
        pks = [1+1j, 'some text [áéíóú]', 10, 10.0, 't1', 't2', 't3', 't4']
        for pk in pks:
            cols = self.row(str(pk))
            cols['order'] = random.choice(range(50))
            self.tdb.put(pk, cols, raw_cols=True)

        for pk in pks:
            qry = self.tdb.query()
            qry.addcond('value', tdb.QCSTREQ, str(pk))
            r = qry.search()
            self.assertEqual(len(r), 1)
            self.assertEqual(str(r[0]), str(pk))
            qry.close()

        qry = self.tdb.query()
        qry.addcond('order', tdb.QCNUMLT, '100')
        r = qry.search()
        self.assertEqual(len(r), 8)
        qry.close()

        qry = self.tdb.query()
        qry.addcond('order', tdb.QCNUMLT, '100')
        qry.setlimit(2)
        r = qry.search()
        self.assertEqual(len(r), 2)
        qry.close()

        qry = self.tdb.query()
        qry.addcond('order', tdb.QCNUMLT, '100')
        # Why not tdb.QONUMASC?
        # Looks like that it's better to store numbers as string
        qry.setorder('order', tdb.QOSTRASC)
        r = qry.search()
        self.assertEqual(len(r), 8)
        qry.close()
        last = 0
        for k in r:
            l = self.tdb.get_col_int(k, 'order')
            self.assert_(last <= l)
            last = l

    def test_metasearch(self):
        pks = [1+1j, 'some text [áéíóú]', 10, 10.0, 't1', 't2', 't3', 't4']
        for pk in pks:
            cols = self.row(str(pk))
            cols['order'] = random.choice(range(50))
            self.tdb.put(pk, cols, raw_cols=True)

        qry1 = self.tdb.query()
        qry1.addcond('value', tdb.QCSTREQ, str(pks[0]))
        qry2 = self.tdb.query()
        qry2.addcond('value', tdb.QCSTREQ, str(pks[1]))
        r = tdb.Query.metasearch([qry1, qry2], tdb.MSUNION)
        self.assertEqual(len(r), 2)
        self.assertEqual(str(r[0]), str(pks[0]))
        self.assertEqual(str(r[1]), str(pks[1]))
        qry1.close()
        qry2.close()

    def row(self, value):
        return {
            'value': value,
            'str': 'string',
            'unicode': u'unicode',
            'int': 10,
            'float': 10.10,
            'object': 1+1j
            }

    def schema(self, value):
        return {
            'value': util.get_type(value, True),
            'str': str,
            'unicode': unicode,
            'int': int,
            'float': float,
            'object': None
            }

if __name__ == '__main__':
    unittest.main()
