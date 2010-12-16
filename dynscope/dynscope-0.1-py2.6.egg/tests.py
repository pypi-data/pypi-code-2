import unittest

class TestCase000Fluid(unittest.TestCase):

    def testSimple(self):
        """test of very simple basic dynamic scope variable assignement"""
        from dynscope import fluid, flet
        with flet():
            fluid.anton = 5
            self.assertEqual(fluid.anton, 5)
            self.assertRaises(AttributeError, getattr, fluid, 'berta')
        self.assertRaises(AttributeError, getattr, fluid, 'anton')

    def testStacked(self):
        """test of stacked dynamic scopes with overloading and inheritance of scope"""
        from dynscope import fluid, flet
        with flet():
            fluid.anton = 5
            fluid.caesar = 99
            with flet(berta=7):
                self.assertEqual(fluid.anton, 5)
                self.assertEqual(fluid.berta, 7)
                self.assertEqual(fluid.caesar, 99)
                with flet(berta=2):
                    self.assertEqual(fluid.anton, 5)
                    self.assertEqual(fluid.berta, 2)
                    self.assertEqual(fluid.caesar, 99)
                self.assertEqual(fluid.anton, 5)
                self.assertEqual(fluid.berta, 7)
                self.assertEqual(fluid.caesar, 99)
            self.assertEqual(fluid.anton, 5)
            self.assertEqual(fluid.caesar, 99)
            self.assertRaises(AttributeError, getattr, fluid, 'berta')
        self.assertRaises(AttributeError, getattr, fluid, 'anton')
        self.assertRaises(AttributeError, getattr, fluid, 'caesar')

    def testIsolated(self):
        """test of isolated dynamic namespaces and independence from global dynamic namespace"""
        from dynscope import fluid, flet, construct
        with flet():
            myfluid, myflet = construct()
            fluid.anton = 77
            with myflet(anton=33):
                self.assertEqual(myfluid.anton,33)
                self.assertEqual(fluid.anton, 77)
            self.assertEqual(fluid.anton, 77)

class TestCase010Threaded(unittest.TestCase):

    def testThreaded(self):
        """test of thread isolation of dynamic namespaces"""
        from dynscope import fluid, flet
        from threading import Thread
        import time

        with flet(anton=7):

            def worker():
                fluid.anton = 9
                fluid.berta = 10
                self.assertEqual(fluid.anton, 9)
                self.assertEqual(fluid.berta, 10)
                time.sleep(2)

            t = Thread(target=worker)
            t.start()
            self.assertEqual(fluid.anton, 7)
            t.join()

        self.assertRaises(AttributeError, getattr, fluid, 'anton')
        self.assertRaises(AttributeError, getattr, fluid, 'berta')

