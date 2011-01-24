import unittest

class AsBoolTests(unittest.TestCase):
    def asBool(self, *a, **kw):
        from z3c.appconfig.utils import asBool
        return asBool(*a, **kw)

    def testNonString(self):
        self.assertEqual(self.asBool(None), False)
        self.assertEqual(self.asBool(1), True)

    def testTrueStrings(self):
        self.assertEqual(self.asBool("true"), True)
        self.assertEqual(self.asBool("yes"), True)
        self.assertEqual(self.asBool("on"), True)

    def testFalseStrings(self):
        self.assertEqual(self.asBool("false"), False)
        self.assertEqual(self.asBool("no"), False)
        self.assertEqual(self.asBool("off"), False)

    def testCaseInsensitive(self):
        self.assertEqual(self.asBool("FaLse"), False)
        self.assertEqual(self.asBool("tRuE"), True)

    def testWhitespaceIgnored(self):
        self.assertEqual(self.asBool("  on\t"), True)

    def testInvalidString(self):
        self.assertRaises(ValueError, self.asBool, "invalid")
