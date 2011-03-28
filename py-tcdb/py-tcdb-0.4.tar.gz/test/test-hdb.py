# -*- coding: utf-8 -*-

import datetime
import os
import unittest
import warnings

from tcdb import hdb
from tcdb import tc


class TestHDBSimple(unittest.TestCase):
    def setUp(self):
        self.hdb = hdb.HDBSimple()
        self.hdb.open('test.hdb', bnum=131071, rcnum=1024, xmsiz=67108864)

    def tearDown(self):
        self.hdb.close()
        self.hdb = None
        os.remove('test.hdb')

    def test_setgetitem(self):
        self.hdb['key'] = 'some string'
        self.assertEqual(self.hdb['key'], 'some string')
        self.assertRaises(KeyError, self.hdb.__getitem__, 'nonexistent key')

    def test_put(self):
        self.hdb.put('key', 'some string')
        self.assertEqual(self.hdb.get('key'), 'some string')
        self.assertEqual(self.hdb.get('nonexistent key'), None)
        self.assertEqual(self.hdb.get('nonexistent key', 'def'), 'def')

    def test_putkeep(self):
        self.hdb.putkeep('key', 'some string')
        self.assertEqual(self.hdb.get('key'), 'some string')
        self.hdb.putkeep('key', 'Never stored')
        self.assertEqual(self.hdb.get('key'), 'some string')

    def test_putcat(self):
        self.hdb.putcat('key', 'some')
        self.hdb.putcat('key', ' text')
        self.assertEquals(self.hdb.get('key'), 'some text')

    def test_putasync(self):
        self.hdb.putasync('key', 'some string')
        self.assertEqual(self.hdb.get('key'), 'some string')

    def test_out_and_contains(self):
        self.assert_('key' not in self.hdb)
        self.hdb.put('key', 'some text')
        self.assert_('key' in self.hdb)
        self.hdb.out('key')
        self.assert_('key' not in self.hdb)
        self.hdb.put('key', 'some text')
        self.assert_('key' in self.hdb)
        del self.hdb['key']
        self.assert_('key' not in self.hdb)

    def test_vsiz(self):
        self.hdb.put('key', 'some text')
        self.assertEqual(self.hdb.vsiz('key'), len('some text'))

    def test_iters(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            self.hdb.put(key, key)

        self.assertEqual(self.hdb.keys(), keys)
        self.assertEqual(self.hdb.values(), keys)
        self.assertEqual(zip(keys, keys), self.hdb.items())

        for key in self.hdb:
            self.assert_(key in keys)

        for value in self.hdb.itervalues():
            self.assert_(value in keys)

    def test_fwmkeys(self):
        objs = ['aa', 'ab', 'ac', 'xx', 'ad']
        for obj in objs:
            self.hdb.put(obj, 'some text')
        self.assertEqual(self.hdb.fwmkeys('a'), ['aa', 'ab', 'ac', 'ad'])
        self.assertEqual(self.hdb.fwmkeys('x'), ['xx'])
        self.assertEqual(self.hdb.fwmkeys('nonexistent key'), [])

    def test_admin_functions(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            self.hdb.put(key, key)

        self.assertEquals(self.hdb.path(), 'test.hdb')

        self.hdb.sync()
        self.assertEquals(len(self.hdb), 5)
        self.assertEquals(self.hdb.fsiz(), 528864)

        self.hdb.vanish()
        self.assertEquals(self.hdb.fsiz(), 528704)

        self.assert_(self.hdb.memsync(True))
        self.assert_(self.hdb.cacheclear())
        self.assertEquals(self.hdb.bnum(), 131071)
        self.assertEquals(self.hdb.align(), 16)
        self.assertEquals(self.hdb.fbpmax(), 1024)
        self.assertEquals(self.hdb.xmsiz(), 67108864)

        self.assert_(self.hdb.optimize(bnum=147451))
        self.assertEquals(self.hdb.bnum(), 147451)
        self.assertEquals(self.hdb.align(), 16)
        self.assertEquals(self.hdb.fbpmax(), 1024)
        self.assertEquals(self.hdb.xmsiz(), 67108864)

        self.assert_(self.hdb.inode())
        self.assert_((datetime.datetime.now()-self.hdb.mtime()).seconds <= 1)
        # Why only OWRITER?!?
        self.assertEquals(self.hdb.omode(), hdb.OWRITER)
        self.assertEquals(self.hdb.type(), tc.THASH)
        self.assertEquals(self.hdb.flags(), hdb.FOPEN)
        self.assertEquals(self.hdb.opts(), 0)
        self.assertEquals(self.hdb.opaque(), '')
        self.assertEquals(self.hdb.bnumused(), 0)
        self.assertEquals(self.hdb.dfunit(), 0)
        self.assert_(self.hdb.defrag(5))

    def test_transaction(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        with self.hdb as db:
            for key in keys:
                db.put(key, key)
        self.assertEquals(len(self.hdb), 5)
        self.hdb.vanish()
        try:
            with self.hdb:
                for key in keys:
                    self.hdb.put(key, key)
                self.hdb['bad key']
        except KeyError:
            pass
        self.assertEquals(len(self.hdb), 0)

    def test_foreach(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']

        def proc(key, value, op):
            self.assertEquals(key, value)
            self.assert_(key in keys)
            self.assertEquals(op, 'test')
            return True

        for key in keys:
            self.hdb.put(key, key)
        self.hdb.foreach(proc, 'test')


class TestHDB(unittest.TestCase):
    def setUp(self):
        self.hdb = hdb.HDB()
        self.hdb.open('test.hdb', bnum=131071, rcnum=1024, xmsiz=67108864)

    def tearDown(self):
        self.hdb.close()
        self.hdb = None
        os.remove('test.hdb')

    def test_setgetitem(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.hdb['obj'] = obj1
            obj2 = self.hdb['obj']
            self.assertEqual(obj1, obj2)

            self.hdb[obj1] = obj1
            obj2 = self.hdb[obj1]
            self.assertEqual(obj1, obj2)
        self.assertRaises(KeyError, self.hdb.__getitem__, 'nonexistent key')

    def test_put(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.hdb.put(obj1, obj1)
            obj2 = self.hdb.get(obj1)
            self.assertEqual(obj1, obj2)
            self.hdb.put(obj1, obj1, raw_key=True)
            obj2 = self.hdb.get(obj1, raw_key=True)
            self.assertEqual(obj1, obj2)
        self.assertEqual(self.hdb.get('nonexistent key'), None)
        self.assertEqual(self.hdb.get('nonexistent key', 'def'), 'def')

    def test_put_str(self):
        str1 = 'some text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_str(obj, str1)
            str2 = self.hdb.get_str(obj)
            self.assertEqual(str1, str2)
            self.hdb.put_str(obj, str1, as_raw=True)
            str2 = self.hdb.get_str(obj, as_raw=True)
            self.assertEqual(str1, str2)
        unicode1 = u'unicode text [áéíóú]'
        for obj in objs:
            self.hdb.put_str(obj, unicode1.encode('utf8'))
            unicode2 = unicode(self.hdb.get_str(obj), 'utf8')
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.hdb.put_str, 'key', 10)
        self.assertEqual(self.hdb.get_str('nonexistent key'), None)
        self.assertEqual(self.hdb.get_str('nonexistent key', 'def'), 'def')

    def test_put_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_unicode(obj, unicode1)
            unicode2 = self.hdb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
            self.hdb.put_unicode(obj, unicode1, as_raw=True)
            unicode2 = self.hdb.get_unicode(obj, as_raw=True)
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.hdb.put_unicode, 'key', 10)
        self.assertEqual(self.hdb.get_unicode('nonexistent key'), None)
        self.assertEqual(self.hdb.get_unicode('nonexistent key', 'def'), 'def')

    def test_put_int(self):
        int1 = 10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_int(obj, int1)
            int2 = self.hdb.get_int(obj)
            self.assertEqual(int1, int2)
            self.hdb.put_int(obj, int1, as_raw=True)
            int2 = self.hdb.get_int(obj, as_raw=True)
            self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.hdb.put_int, 'key', '10')
        self.assertEqual(self.hdb.get_int('nonexistent key'), None)
        self.assertEqual(self.hdb.get_int('nonexistent key', 'def'), 'def')

    def test_put_float(self):
        float1 = 10.10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_float(obj, float1)
            float2 = self.hdb.get_float(obj)
            self.assertEqual(float1, float2)
            self.hdb.put_float(obj, float1, as_raw=True)
            float2 = self.hdb.get_float(obj, as_raw=True)
            self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.hdb.put_float, 'key', 10)
        self.assertEqual(self.hdb.get_float('nonexistent key'), None)
        self.assertEqual(self.hdb.get_float('nonexistent key', 'def'), 'def')

    def test_putkeep(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.hdb.putkeep(obj1, obj1)
            obj2 = self.hdb.get(obj1)
            self.assertEqual(obj1, obj2)
            self.hdb.putkeep(obj1, 'Never stored')
            obj2 = self.hdb.get(obj1)
            self.assertEqual(obj1, obj2)

    def test_putkeep_str(self):
        str1 = 'some text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putkeep_str(obj, str1)
            str2 = self.hdb.get_str(obj)
            self.assertEqual(str1, str2)
            self.hdb.putkeep_str(obj, 'Never stored')
            str2 = self.hdb.get_str(obj)
            self.assertEqual(str1, str2)
        self.assertRaises(AssertionError, self.hdb.putkeep_str, 'key', 10)

    def test_putkeep_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putkeep_unicode(obj, unicode1)
            unicode2 = self.hdb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
            self.hdb.putkeep_unicode(obj, u'Never stored')
            unicode2 = self.hdb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.hdb.putkeep_unicode, 'key', 10)

    def test_putkeep_int(self):
        int1 = 10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putkeep_int(obj, int1)
            int2 = self.hdb.get_int(obj)
            self.assertEqual(int1, int2)
            self.hdb.putkeep_int(obj, int1*10)
            int2 = self.hdb.get_int(obj)
            self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.hdb.putkeep_int, 'key', '10')

    def test_putkeep_float(self):
        float1 = 10.10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putkeep_float(obj, float1)
            float2 = self.hdb.get_float(obj)
            self.assertEqual(float1, float2)
            self.hdb.putkeep_float(obj, float1*10)
            float2 = self.hdb.get_float(obj)
            self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.hdb.put_float, 'key', 10)

    def test_putcat_str(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putcat_str(obj, 'some')
        for obj in objs:
            self.hdb.putcat_str(obj, ' text')
        for obj in objs:
            self.assertEquals(self.hdb.get_str(obj), 'some text')

    def test_putcat_unicode(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putcat_unicode(obj, u'some')
        for obj in objs:
            self.hdb.putcat_unicode(obj, u' text')
        for obj in objs:
            self.assertEquals(self.hdb.get_unicode(obj), u'some text')

    def test_putasync(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.hdb.putasync(obj1, obj1)
            obj2 = self.hdb.get(obj1)
            self.assertEqual(obj1, obj2)

    def test_putasync_str(self):
        str1 = 'some text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putasync_str(obj, str1)
            str2 = self.hdb.get_str(obj)
            self.assertEqual(str1, str2)
        unicode1 = u'unicode text [áéíóú]'
        for obj in objs:
            self.hdb.putasync_str(obj, unicode1.encode('utf8'))
            unicode2 = unicode(self.hdb.get_str(obj), 'utf8')
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.hdb.putasync_str, 'key', 10)

    def test_putasync_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putasync_unicode(obj, unicode1)
            unicode2 = self.hdb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.hdb.putasync_unicode, 'key', 10)

    def test_putasync_int(self):
        int1 = 10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putasync_int(obj, int1)
            int2 = self.hdb.get_int(obj)
            self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.hdb.putasync_int, 'key', '10')

    def test_putasync_float(self):
        float1 = 10.10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.putasync_float(obj, float1)
            float2 = self.hdb.get_float(obj)
            self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.hdb.putasync_float, 'key', 10)

    def test_out_and_contains(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put(obj, obj)
            self.assert_(obj in self.hdb)
            self.hdb.out(obj)
            self.assert_(obj not in self.hdb)

        for obj in objs:
            self.hdb.put(obj, obj)
            self.assert_(obj in self.hdb)
            del self.hdb[obj]
            self.assert_(obj not in self.hdb)

    def test_vsiz(self):
        obj = 1+1j
        self.hdb.put(obj, obj)
        vsiz = self.hdb.vsiz(obj)
        self.assertEqual(vsiz, 48)

        obj = 'some text [áéíóú]'
        self.hdb.put_str(obj, obj)
        vsiz = self.hdb.vsiz(obj)
        self.assertEqual(vsiz, 22)

        obj = u'unicode text [áéíóú]'
        self.hdb.put_str(obj, obj.encode('utf8'))
        vsiz = self.hdb.vsiz(obj)
        self.assertEqual(vsiz, 25)

        obj = 10
        self.hdb.put_int(obj, obj)
        vsiz = self.hdb.vsiz(obj)
        self.assertEqual(vsiz, 4)

        obj = 10.10
        self.hdb.put_float(obj, obj)
        vsiz = self.hdb.vsiz(obj)
        self.assertEqual(vsiz, 8)

    def test_iters(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put(obj, obj)

        self.assertEqual(self.hdb.keys(), objs)
        self.assertEqual(self.hdb.values(), objs)
        self.assertEqual(zip(objs, objs), self.hdb.items())

        for key in self.hdb:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(key in objs)

        for value in self.hdb.itervalues():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(value in objs)

    def test_fwmkeys(self):
        objs = ['aa', 'ab', 'ac', 'xx', 'ad']
        for obj in objs:
            self.hdb.put(obj, 'same value', raw_key=True)
        self.assertEqual(self.hdb.fwmkeys('a'), ['aa', 'ab', 'ac', 'ad'])
        self.assertEqual(self.hdb.fwmkeys('x'), ['xx'])
        self.assertEqual(self.hdb.fwmkeys('nonexistent key'), [])

    def test_add_int(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_int(obj, 10)
        for key in self.hdb:
            self.hdb.add_int(key, 2)
        for key in self.hdb:
            self.assertEqual(self.hdb.get_int(key), 12)

    def test_add_float(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put_float(obj, 10.0)
        for key in self.hdb:
            self.hdb.add_float(key, 2.0)
        for key in self.hdb:
            self.assertEqual(self.hdb.get_float(key), 12.0)

    def test_admin_functions(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.hdb.put(obj, obj)

        self.assertEquals(self.hdb.path(), 'test.hdb')

        self.hdb.sync()
        self.assertEquals(len(self.hdb), 5)
        self.assertEquals(self.hdb.fsiz(), 529072)

        self.hdb.vanish()
        self.assertEquals(self.hdb.fsiz(), 528704)

        self.assert_(self.hdb.memsync(True))
        self.assert_(self.hdb.cacheclear())
        self.assertEquals(self.hdb.bnum(), 131071)
        self.assertEquals(self.hdb.align(), 16)
        self.assertEquals(self.hdb.fbpmax(), 1024)
        self.assertEquals(self.hdb.xmsiz(), 67108864)

        self.assert_(self.hdb.optimize(bnum=147451))
        self.assertEquals(self.hdb.bnum(), 147451)
        self.assertEquals(self.hdb.align(), 16)
        self.assertEquals(self.hdb.fbpmax(), 1024)
        self.assertEquals(self.hdb.xmsiz(), 67108864)

        self.assert_(self.hdb.inode())
        self.assert_((datetime.datetime.now()-self.hdb.mtime()).seconds <= 1)
        # Why only OWRITER?!?
        self.assertEquals(self.hdb.omode(), hdb.OWRITER)
        self.assertEquals(self.hdb.type(), tc.THASH)
        self.assertEquals(self.hdb.flags(), hdb.FOPEN)
        self.assertEquals(self.hdb.opts(), 0)
        self.assertEquals(self.hdb.opaque(), '')
        self.assertEquals(self.hdb.bnumused(), 0)
        self.assertEquals(self.hdb.dfunit(), 0)
        self.assert_(self.hdb.defrag(5))

    def test_transaction(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        with self.hdb as db:
            for obj in objs:
                db.put(obj, obj)
        self.assertEquals(len(self.hdb), 5)
        self.hdb.vanish()
        try:
            with self.hdb:
                for obj in objs:
                    self.hdb.put(obj, obj)
                self.hdb['bad key']
        except KeyError:
            pass
        self.assertEquals(len(self.hdb), 0)

    def test_foreach(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]

        def proc(key, value, op):
            self.assertEquals(key, value)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(key in objs)
            self.assertEquals(op, 'test')
            return True

        for obj in objs:
            self.hdb.put(obj, obj)
        self.hdb.foreach(proc, 'test')


if __name__ == '__main__':
    unittest.main()
