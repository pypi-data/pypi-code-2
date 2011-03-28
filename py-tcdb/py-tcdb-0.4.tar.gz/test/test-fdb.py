# -*- coding: utf-8 -*-

import datetime
import os
import unittest
import warnings

from tcdb import fdb
from tcdb import tc


class TestFDBSimple(unittest.TestCase):
    def setUp(self):
        self.fdb = fdb.FDBSimple()
        self.fdb.open('test.fdb', width=255)

    def tearDown(self):
        self.fdb.close()
        self.fdb = None
        os.remove('test.fdb')

    def test_setgetitem(self):
        self.fdb['next'] = 'some text'
        self.assertEqual(self.fdb['max'], 'some text')
        self.assertRaises(Exception, self.fdb.__getitem__, 100)
        self.assertRaises(KeyError, self.fdb.__getitem__, '100')

    def test_put(self):
        self.fdb.put('next', 'some text')
        self.assertEqual(self.fdb.get('max'), 'some text')
        self.assertEqual(self.fdb.get('100'), None)
        self.assertEqual(self.fdb.get('100', 'def'), 'def')

    def test_putkeep(self):
        self.fdb.putkeep('next', 'some text')
        self.assertEqual(self.fdb.get('max'), 'some text')
        self.fdb.putkeep('max', 'Never stored')
        self.assertEqual(self.fdb.get('max'), 'some text')

    def test_putcat(self):
        self.fdb.putcat('next', 'some')
        self.fdb.putcat('max', ' text')
        self.assertEquals(self.fdb.get('max'), 'some text')

    def test_out_and_contains(self):
        self.assert_('1' not in self.fdb)
        self.fdb.put('next', 'some text')
        self.assert_('1' in self.fdb)
        self.fdb.out('max')
        self.assert_('1' not in self.fdb)
        self.fdb.put('next', 'some text')
        self.assert_('1' in self.fdb)
        del self.fdb['max']
        self.assert_('1' not in self.fdb)

    def test_vsiz(self):
        self.fdb.put('next', 'some text')
        self.assertEqual(self.fdb.vsiz('max'), len('some text'))

    def test_iters(self):
        self.assertEqual(self.fdb.keys(), [])
        self.assertEqual(self.fdb.values(), [])
        self.assertEqual(self.fdb.items(), [])

        keys = ['1', '2', '3', '4', '5']
        values = ['value1', 'value2', 'value3', 'value4', 'value5']
        for value in values:
            self.fdb.put('next', value)

        self.assertEqual(self.fdb.keys(), keys)
        self.assertEqual(self.fdb.values(), values)
        self.assertEqual(zip(keys, values), self.fdb.items())

        for key in self.fdb:
            self.assert_(key in keys)

        for value in self.fdb.itervalues():
            self.assert_(value in values)

    def test_range(self):
        keys = ['1', '2', '3', '4', '5']
        values = ['value1', 'value2', 'value3', 'value4', 'value5']
        for value in values:
            self.fdb.put('next', value)

        self.assertEqual(self.fdb.range('min', 'max'), keys)
        self.assertEqual(self.fdb.range('2', '4'), keys[1:-1])

    def test_admin_functions(self):
        values = ['value1', 'value2', 'value3', 'value4', 'value5']
        for value in values:
            self.fdb.put('next', value)

        self.assertEquals(self.fdb.path(), 'test.fdb')

        self.fdb.sync()
        self.assertEquals(len(self.fdb), 5)
        self.assertEquals(self.fdb.fsiz(), 66048)

        self.fdb.vanish()
        self.assertEquals(self.fdb.fsiz(), 256)

        self.assert_(self.fdb.memsync(True))
        # self.assertEquals(self.fdb.min(), 0)
        # self.assertEquals(self.fdb.max(), 0)
        self.assertEquals(self.fdb.width(), 255)
        self.assertEquals(self.fdb.limsiz(), 268435456)
        self.assertEquals(self.fdb.limid(), 1048575)

        self.assert_(self.fdb.inode())
        self.assert_((datetime.datetime.now()-self.fdb.mtime()).seconds <= 1)
        # Why OTRUNC?!?
        self.assertEquals(self.fdb.omode(), fdb.OTRUNC|fdb.OCREAT|fdb.OWRITER)
        self.assertEquals(self.fdb.type(), tc.TFIXED)
        self.assertEquals(self.fdb.flags(), fdb.FOPEN)
        self.assertEquals(self.fdb.opaque(), '')

    def test_transaction(self):
        values = ['value1', 'value2', 'value3', 'value4', 'value5']
        with self.fdb as db:
            for value in values:
                db.put('next', value)
        self.assertEquals(len(self.fdb), 5)
        self.fdb.vanish()
        try:
            with self.fdb:
                for value in values:
                    self.fdb.put('next', value)
                self.fdb['100']
        except KeyError:
            pass
        self.assertEquals(len(self.fdb), 0)

    def test_foreach(self):
        values = ['value1', 'value2', 'value3', 'value4', 'value5']

        def proc(key, value, op):
            self.assert_(1<=key<=5)
            self.assert_(value in values)
            self.assertEquals(op, 'test')
            return True

        for value in values:
            self.fdb.put('next', value)
        self.fdb.foreach(proc, 'test')


class TestFDB(unittest.TestCase):
    def setUp(self):
        self.fdb = fdb.FDB()
        self.fdb.open('test.fdb', width=255)

    def tearDown(self):
        self.fdb.close()
        self.fdb = None
        os.remove('test.fdb')

    def test_setgetitem(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.fdb[fdb.IDNEXT] = obj1
            obj2 = self.fdb[fdb.IDMAX]
            self.assertEqual(obj1, obj2)
        self.assertRaises(Exception, self.fdb.__getitem__, 'text')
        self.assertRaises(KeyError, self.fdb.__getitem__, 100)

    def test_put(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for key, obj1 in enumerate(objs):
            self.fdb.put(key+1, obj1)
            obj2 = self.fdb.get(key+1)
            self.assertEqual(obj1, obj2)
        self.assertEqual(self.fdb.get(100), None)
        self.assertEqual(self.fdb.get(100, 'def'), 'def')

    def test_put_str(self):
        str1 = 'some text [áéíóú]'
        self.fdb.put_str(fdb.IDNEXT, str1)
        str2 = self.fdb.get_str(fdb.IDMAX)
        self.assertEqual(str1, str2)
        unicode1 = u'unicode text [áéíóú]'
        self.fdb.put_str(fdb.IDNEXT, unicode1.encode('utf8'))
        unicode2 = unicode(self.fdb.get_str(fdb.IDMAX), 'utf8')
        self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.fdb.put_str, 'key', 10)
        self.assertEqual(self.fdb.get_str(100), None)
        self.assertEqual(self.fdb.get_str(100, 'def'), 'def')

    def test_put_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        self.fdb.put_unicode(fdb.IDNEXT, unicode1)
        unicode2 = self.fdb.get_unicode(fdb.IDMAX)
        self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.fdb.put_unicode, 'key', 10)
        self.assertEqual(self.fdb.get_unicode(100), None)
        self.assertEqual(self.fdb.get_unicode(100, 'def'), 'def')

    def test_put_int(self):
        int1 = 10
        self.fdb.put_int(fdb.IDNEXT, int1)
        int2 = self.fdb.get_int(fdb.IDMAX)
        self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.fdb.put_int, 'key', '10')
        self.assertEqual(self.fdb.get_int(100), None)
        self.assertEqual(self.fdb.get_int(100, 'def'), 'def')

    def test_put_float(self):
        float1 = 10.10
        self.fdb.put_float(fdb.IDNEXT, float1)
        float2 = self.fdb.get_float(fdb.IDMAX)
        self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.fdb.put_float, 'key', 10)
        self.assertEqual(self.fdb.get_float(100), None)
        self.assertEqual(self.fdb.get_float(100, 'def'), 'def')

    def test_putkeep(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for key, obj1 in enumerate(objs):
            self.fdb.putkeep(key+1, obj1)
            obj2 = self.fdb.get(key+1)
            self.assertEqual(obj1, obj2)
            self.fdb.putkeep(key+1, 'Never stored')
            obj2 = self.fdb.get(key+1)
            self.assertEqual(obj1, obj2)

    def test_putkeep_str(self):
        str1 = 'some text [áéíóú]'
        self.fdb.putkeep_str(fdb.IDNEXT, str1)
        str2 = self.fdb.get_str(fdb.IDMAX)
        self.assertEqual(str1, str2)
        self.fdb.putkeep_str(fdb.IDMAX, 'Never stored')
        str2 = self.fdb.get_str(fdb.IDMAX)
        self.assertEqual(str1, str2)
        self.assertRaises(AssertionError, self.fdb.putkeep_str, 'key', 10)

    def test_putkeep_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        self.fdb.putkeep_unicode(fdb.IDNEXT, unicode1)
        unicode2 = self.fdb.get_unicode(fdb.IDMAX)
        self.assertEqual(unicode1, unicode2)
        self.fdb.putkeep_unicode(fdb.IDMAX, u'Never stored')
        unicode2 = self.fdb.get_unicode(fdb.IDMAX)
        self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.fdb.putkeep_unicode, 'key', 10)

    def test_putkeep_int(self):
        int1 = 10
        self.fdb.putkeep_int(fdb.IDNEXT, int1)
        int2 = self.fdb.get_int(fdb.IDMAX)
        self.assertEqual(int1, int2)
        self.fdb.putkeep_int(fdb.IDMAX, int1*10)
        int2 = self.fdb.get_int(fdb.IDMAX)
        self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.fdb.putkeep_int, 'key', '10')

    def test_putkeep_float(self):
        float1 = 10.10
        self.fdb.putkeep_float(fdb.IDNEXT, float1)
        float2 = self.fdb.get_float(fdb.IDMAX)
        self.assertEqual(float1, float2)
        self.fdb.putkeep_float(fdb.IDMAX, float1*10)
        float2 = self.fdb.get_float(fdb.IDMAX)
        self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.fdb.put_float, 'key', 10)

    def test_putcat_str(self):
        self.fdb.putcat_str(fdb.IDNEXT, 'some')
        self.fdb.putcat_str(fdb.IDMAX, ' text')
        self.assertEquals(self.fdb.get_str(fdb.IDMAX), 'some text')

    def test_putcat_unicode(self):
        self.fdb.putcat_unicode(fdb.IDNEXT, u'some')
        self.fdb.putcat_unicode(fdb.IDMAX, u' text')
        self.assertEquals(self.fdb.get_unicode(fdb.IDMAX), u'some text')

    def test_out_and_contains(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for key, obj in enumerate(objs):
            self.fdb.put(key+1, obj)
            self.assert_(key+1 in self.fdb)
            self.fdb.out(key+1)
            self.assert_(key+1 not in self.fdb)

        for obj in objs:
            self.fdb.put(key+1, obj)
            self.assert_(key+1 in self.fdb)
            del self.fdb[key+1]
            self.assert_(key+1 not in self.fdb)

    def test_slice(self):
        self.assertEqual(self.fdb[1:3], [])
        self.assertEqual(self.fdb[3:1:-1], [])
        self.assertEqual(self.fdb[1:], [])
        self.assertEqual(self.fdb[:1:-1], [])
        nums = range(10)
        for n in nums[1:]:
            self.fdb[n] = n
        self.assertEqual(self.fdb[1:3], nums[1:3])
        self.assertEqual(self.fdb[3:1:-1], nums[3:1:-1])
        self.assertEqual(self.fdb[1:], nums[1:])
        self.assertEqual(self.fdb[:1:-1], nums[:1:-1])

    def test_vsiz(self):
        obj = 1+1j
        self.fdb.put(fdb.IDNEXT, obj)
        vsiz = self.fdb.vsiz(fdb.IDMAX)
        self.assertEqual(vsiz, 48)

        obj = 'some text [áéíóú]'
        self.fdb.put_str(fdb.IDNEXT, obj)
        vsiz = self.fdb.vsiz(fdb.IDMAX)
        self.assertEqual(vsiz, 22)

        obj = u'unicode text [áéíóú]'
        self.fdb.put_str(fdb.IDNEXT, obj.encode('utf8'))
        vsiz = self.fdb.vsiz(fdb.IDMAX)
        self.assertEqual(vsiz, 25)

        obj = 10
        self.fdb.put_int(fdb.IDNEXT, obj)
        vsiz = self.fdb.vsiz(fdb.IDMAX)
        self.assertEqual(vsiz, 4)

        obj = 10.10
        self.fdb.put_float(fdb.IDNEXT, obj)
        vsiz = self.fdb.vsiz(fdb.IDMAX)
        self.assertEqual(vsiz, 8)

    def test_iters(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for key, obj in enumerate(objs):
            self.fdb.put(key+1, obj)

        self.assertEqual(self.fdb.keys(), range(1, len(objs)+1))
        self.assertEqual(self.fdb.values(), objs)
        self.assertEqual(zip(range(1, len(objs)+1), objs), self.fdb.items())

        for key in self.fdb:
            self.assert_(key in range(1, len(objs)+1))

        for value in self.fdb.itervalues():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(value in objs)

    def test_range(self):
        objs = zip([10**x for x in range(6)], range(6))
        for k, v in objs:
            self.fdb.put_int(k, v)

        self.assertEqual(self.fdb.range(fdb.IDMIN, fdb.IDMAX),
                         [1, 10, 100, 1000, 10000, 100000])
        self.assertEqual(self.fdb.range(10, 10000), [10, 100, 1000, 10000])
        self.assertEqual(self.fdb.range(100, 1000), [100, 1000])

    def test_add_int(self):
        self.fdb.put_int(fdb.IDNEXT, 10)
        self.fdb.add_int(fdb.IDMAX, 2)
        self.assertEqual(self.fdb.get_int(fdb.IDMAX), 12)

    def test_add_float(self):
        self.fdb.put_float(fdb.IDNEXT, 10.0)
        self.fdb.add_float(fdb.IDMAX, 2.0)
        self.assertEqual(self.fdb.get_float(fdb.IDMAX), 12.0)

    def test_admin_functions(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for key, obj in enumerate(objs):
            self.fdb.put(key+1, obj)

        self.assertEquals(self.fdb.path(), 'test.fdb')

        self.fdb.sync()
        self.assertEquals(len(self.fdb), 5)
        self.assertEquals(self.fdb.fsiz(), 66048)

        self.fdb.vanish()
        self.assertEquals(self.fdb.fsiz(), 256)

        self.assert_(self.fdb.memsync(True))
        self.assertEquals(self.fdb.min(), 0)
        self.assertEquals(self.fdb.max(), 0)
        self.assertEquals(self.fdb.width(), 255)
        self.assertEquals(self.fdb.limsiz(), 268435456)
        self.assertEquals(self.fdb.limid(), 1048575)

        # FIX optimize throw an exception.
        # self.assert_(self.fdb.optimize(width=1024))
        # self.assertEquals(self.fdb.width(), 1024)
        # self.assertEquals(self.fdb.limsiz(), 268435456)
        # self.assertEquals(self.fdb.limid(), 1048575)

        self.assert_(self.fdb.inode())
        self.assert_((datetime.datetime.now()-self.fdb.mtime()).seconds <= 1)
        # Why OTRUNC?!?
        self.assertEquals(self.fdb.omode(), fdb.OTRUNC|fdb.OCREAT|fdb.OWRITER)
        self.assertEquals(self.fdb.type(), tc.TFIXED)
        self.assertEquals(self.fdb.flags(), fdb.FOPEN)
        self.assertEquals(self.fdb.opaque(), '')

    def test_transaction(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        with self.fdb as db:
            for key, obj in enumerate(objs):
                db.put(key+1, obj)
        self.assertEquals(len(self.fdb), 5)
        self.fdb.vanish()
        try:
            with self.fdb:
                for key, obj in enumerate(objs):
                    self.fdb.put(key+1, obj)
                self.fdb[100]
        except KeyError:
            pass
        self.assertEquals(len(self.fdb), 0)

    def test_foreach(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]

        def proc(key, value, op):
            self.assert_(1<=key<=5)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(value in objs)
            self.assertEquals(op, 'test')
            return True

        for key, obj in enumerate(objs):
            self.fdb.put(key+1, obj)
        self.fdb.foreach(proc, 'test')


if __name__ == '__main__':
    unittest.main()
