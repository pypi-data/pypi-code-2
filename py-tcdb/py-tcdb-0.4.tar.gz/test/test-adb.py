# -*- coding: utf-8 -*-

import unittest
import warnings

from tcdb import adb


class TestADBSimple(unittest.TestCase):
    def setUp(self):
        self.adb = adb.ADBSimple()
        self.adb.open('*')

    def tearDown(self):
        self.adb.close()
        self.adb = None

    def test_setgetitem(self):
        self.adb['key'] = 'some string'
        self.assertEqual(self.adb['key'], 'some string')
        self.assertRaises(KeyError, self.adb.__getitem__, 'nonexistent key')

    def test_put(self):
        self.adb.put('key', 'some string')
        self.assertEqual(self.adb.get('key'), 'some string')
        self.assertEqual(self.adb.get('nonexistent key'), None)
        self.assertEqual(self.adb.get('nonexistent key', 'def'), 'def')

    def test_putkeep(self):
        self.adb.putkeep('key', 'some string')
        self.assertEqual(self.adb.get('key'), 'some string')
        self.adb.putkeep('key', 'Never stored')
        self.assertEqual(self.adb.get('key'), 'some string')

    def test_putcat(self):
        self.adb.putcat('key', 'some')
        self.adb.putcat('key', ' text')
        self.assertEquals(self.adb.get('key'), 'some text')

    def test_out_and_contains(self):
        self.assert_('key' not in self.adb)
        self.adb.put('key', 'some text')
        self.assert_('key' in self.adb)
        self.adb.out('key')
        self.assert_('key' not in self.adb)
        self.adb.put('key', 'some text')
        self.assert_('key' in self.adb)
        del self.adb['key']
        self.assert_('key' not in self.adb)

    def test_vsiz(self):
        self.adb.put('key', 'some text')
        self.assertEqual(self.adb.vsiz('key'), len('some text'))

    def test_iters(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            self.adb.put(key, key)

        self.assertEqual(len(self.adb.keys()), len(keys))
        self.assertEqual(len(self.adb.values()), len(keys))
        self.assertEqual(len(zip(keys, keys)), len(self.adb.items()))

        for key in self.adb:
            self.assert_(key in keys)

        for value in self.adb.itervalues():
            self.assert_(value in keys)

    def test_fwmkeys(self):
        objs = ['aa', 'ab', 'ac', 'xx', 'ad']
        for obj in objs:
            self.adb.put(obj, 'same value')
        self.assertEqual(len(self.adb.fwmkeys('a')),
                         len(['aa', 'ab', 'ac', 'ad']))
        self.assertEqual(self.adb.fwmkeys('x'), ['xx'])
        self.assertEqual(self.adb.fwmkeys('nonexistent key'), [])


    def test_admin_functions(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            self.adb.put(key, key)

        self.assertEquals(self.adb.path(), '*')

        self.adb.sync()
        self.assertEquals(len(self.adb), 5)
        self.assertEquals(self.adb.size(), 525656)

        self.adb.vanish()
        self.assertEquals(self.adb.size(), 525376)

    # def test_transaction(self):
    #     keys = ['key1', 'key2', 'key3', 'key4', 'key5']
    #     with self.adb as db:
    #         for key in keys:
    #             db.put(key, key)
    #     self.assertEquals(len(self.adb), 5)
    #     self.adb.vanish()
    #     try:
    #         with self.adb:
    #             for key in keys:
    #                 self.adb.put(key, key)
    #             self.adb['bad key']
    #     except KeyError:
    #         pass
    #     self.assertEquals(len(self.adb), 0)

    def test_foreach(self):
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']

        def proc(key, value, op):
            self.assertEquals(key, value)
            self.assert_(key in keys)
            self.assertEquals(op, 'test')
            return True

        for key in keys:
            self.adb.put(key, key)
        self.adb.foreach(proc, 'test')


class TestADB(unittest.TestCase):
    def setUp(self):
        self.adb = adb.ADB()
        self.adb.open('*')

    def tearDown(self):
        self.adb.close()
        self.adb = None

    def test_setgetitem(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.adb['obj'] = obj1
            obj2 = self.adb['obj']
            self.assertEqual(obj1, obj2)

            self.adb[obj1] = obj1
            obj2 = self.adb[obj1]
            self.assertEqual(obj1, obj2)
        self.assertRaises(KeyError, self.adb.__getitem__, 'nonexistent key')

    def test_put(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.adb.put(obj1, obj1)
            obj2 = self.adb.get(obj1)
            self.assertEqual(obj1, obj2)
            self.adb.put(obj1, obj1, raw_key=True)
            obj2 = self.adb.get(obj1, raw_key=True)
            self.assertEqual(obj1, obj2)
        self.assertEqual(self.adb.get('nonexistent key'), None)
        self.assertEqual(self.adb.get('nonexistent key', 'def'), 'def')

    def test_put_str(self):
        str1 = 'some text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_str(obj, str1)
            str2 = self.adb.get_str(obj)
            self.assertEqual(str1, str2)
            self.adb.put_str(obj, str1, as_raw=True)
            str2 = self.adb.get_str(obj, as_raw=True)
            self.assertEqual(str1, str2)
        unicode1 = u'unicode text [áéíóú]'
        for obj in objs:
            self.adb.put_str(obj, unicode1.encode('utf8'))
            unicode2 = unicode(self.adb.get_str(obj), 'utf8')
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.adb.put_str, 'key', 10)
        self.assertEqual(self.adb.get_str('nonexistent key'), None)
        self.assertEqual(self.adb.get_str('nonexistent key', 'def'), 'def')

    def test_put_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_unicode(obj, unicode1)
            unicode2 = self.adb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
            self.adb.put_unicode(obj, unicode1, as_raw=True)
            unicode2 = self.adb.get_unicode(obj, as_raw=True)
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.adb.put_unicode, 'key', 10)
        self.assertEqual(self.adb.get_unicode('nonexistent key'), None)
        self.assertEqual(self.adb.get_unicode('nonexistent key', 'def'), 'def')

    def test_put_int(self):
        int1 = 10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_int(obj, int1)
            int2 = self.adb.get_int(obj)
            self.assertEqual(int1, int2)
            self.adb.put_int(obj, int1, as_raw=True)
            int2 = self.adb.get_int(obj, as_raw=True)
            self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.adb.put_int, 'key', '10')
        self.assertEqual(self.adb.get_int('nonexistent key'), None)
        self.assertEqual(self.adb.get_int('nonexistent key', 'def'), 'def')

    def test_put_float(self):
        float1 = 10.10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_float(obj, float1)
            float2 = self.adb.get_float(obj)
            self.assertEqual(float1, float2)
            self.adb.put_float(obj, float1, as_raw=True)
            float2 = self.adb.get_float(obj, as_raw=True)
            self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.adb.put_float, 'key', 10)
        self.assertEqual(self.adb.get_float('nonexistent key'), None)
        self.assertEqual(self.adb.get_float('nonexistent key', 'def'), 'def')

    def test_putkeep(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj1 in objs:
            self.adb.putkeep(obj1, obj1)
            obj2 = self.adb.get(obj1)
            self.assertEqual(obj1, obj2)
            self.adb.putkeep(obj1, 'Never stored')
            obj2 = self.adb.get(obj1)
            self.assertEqual(obj1, obj2)

    def test_putkeep_str(self):
        str1 = 'some text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putkeep_str(obj, str1)
            str2 = self.adb.get_str(obj)
            self.assertEqual(str1, str2)
            self.adb.putkeep_str(obj, 'Never stored')
            str2 = self.adb.get_str(obj)
            self.assertEqual(str1, str2)
        self.assertRaises(AssertionError, self.adb.putkeep_str, 'key', 10)

    def test_putkeep_unicode(self):
        unicode1 = u'unicode text [áéíóú]'
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putkeep_unicode(obj, unicode1)
            unicode2 = self.adb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
            self.adb.putkeep_unicode(obj, u'Never stored')
            unicode2 = self.adb.get_unicode(obj)
            self.assertEqual(unicode1, unicode2)
        self.assertRaises(AssertionError, self.adb.putkeep_unicode, 'key', 10)

    def test_putkeep_int(self):
        int1 = 10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putkeep_int(obj, int1)
            int2 = self.adb.get_int(obj)
            self.assertEqual(int1, int2)
            self.adb.putkeep_int(obj, int1*10)
            int2 = self.adb.get_int(obj)
            self.assertEqual(int1, int2)
        self.assertRaises(AssertionError, self.adb.putkeep_int, 'key', '10')

    def test_putkeep_float(self):
        float1 = 10.10
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putkeep_float(obj, float1)
            float2 = self.adb.get_float(obj)
            self.assertEqual(float1, float2)
            self.adb.putkeep_float(obj, float1*10)
            float2 = self.adb.get_float(obj)
            self.assertEqual(float1, float2)
        self.assertRaises(AssertionError, self.adb.put_float, 'key', 10)

    def test_putcat_str(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putcat_str(obj, 'some')
        for obj in objs:
            self.adb.putcat_str(obj, ' text')
        for obj in objs:
            self.assertEquals(self.adb.get_str(obj), 'some text')

    def test_putcat_unicode(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.putcat_unicode(obj, u'some')
        for obj in objs:
            self.adb.putcat_unicode(obj, u' text')
        for obj in objs:
            self.assertEquals(self.adb.get_unicode(obj), u'some text')

    def test_out_and_contains(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put(obj, obj)
            self.assert_(obj in self.adb)
            self.adb.out(obj)
            self.assert_(obj not in self.adb)

        for obj in objs:
            self.adb.put(obj, obj)
            self.assert_(obj in self.adb)
            del self.adb[obj]
            self.assert_(obj not in self.adb)

    def test_vsiz(self):
        obj = 1+1j
        self.adb.put(obj, obj)
        vsiz = self.adb.vsiz(obj)
        self.assertEqual(vsiz, 48)

        obj = 'some text [áéíóú]'
        self.adb.put_str(obj, obj)
        vsiz = self.adb.vsiz(obj)
        self.assertEqual(vsiz, 22)

        obj = u'unicode text [áéíóú]'
        self.adb.put_str(obj, obj.encode('utf8'))
        vsiz = self.adb.vsiz(obj)
        self.assertEqual(vsiz, 25)

        obj = 10
        self.adb.put_int(obj, obj)
        vsiz = self.adb.vsiz(obj)
        self.assertEqual(vsiz, 4)

        obj = 10.10
        self.adb.put_float(obj, obj)
        vsiz = self.adb.vsiz(obj)
        self.assertEqual(vsiz, 8)

    def test_iters(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put(obj, obj)

        self.assertEqual(len(self.adb.keys()), len(objs))
        self.assertEqual(len(self.adb.values()), len(objs))

        for key in self.adb:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(key in objs)

        for value in self.adb.itervalues():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assert_(value in objs)

    def test_fwmkeys(self):
        objs = ['aa', 'ab', 'ac', 'xx', 'ad']
        for obj in objs:
            self.adb.put(obj, 'same value', raw_key=True)
        self.assertEqual(len(self.adb.fwmkeys('a')),
                         len(['aa', 'ab', 'ac', 'ad']))
        self.assertEqual(self.adb.fwmkeys('x'), ['xx'])
        self.assertEqual(self.adb.fwmkeys('nonexistent key'), [])

    def test_add_int(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_int(obj, 10)
        for key in self.adb:
            self.adb.add_int(key, 2)
        for key in self.adb:
            self.assertEqual(self.adb.get_int(key), 12)

    def test_add_float(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put_float(obj, 10.0)
        for key in self.adb:
            self.adb.add_float(key, 2.0)
        for key in self.adb:
            self.assertEqual(self.adb.get_float(key), 12.0)

    def test_admin_functions(self):
        objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
        for obj in objs:
            self.adb.put(obj, obj)

        self.assertEquals(self.adb.path(), '*')

        self.adb.sync()
        self.assertEquals(len(self.adb), 5)
        self.assertEquals(self.adb.size(), 525874)

        self.adb.vanish()
        self.assertEquals(self.adb.size(), 525376)

    # def test_transaction(self):
    #     objs = [1+1j, 'some text [áéíóú]', u'unicode text [áéíóú]', 10, 10.0]
    #     with self.adb as db:
    #         for obj in objs:
    #             db.put(obj, obj)
    #     self.assertEquals(len(self.adb), 5)
    #     self.adb.vanish()
    #     try:
    #         with self.adb:
    #             for obj in objs:
    #                 self.adb.put(obj, obj)
    #             self.adb.get('Not exist key')
    #     except KeyError:
    #         pass
    #     self.assertEquals(len(self.adb), 0)

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
            self.adb.put(obj, obj)
        self.adb.foreach(proc, 'test')


if __name__ == '__main__':
    unittest.main()
