import operator
import os
import unittest
import StringIO
from z3c.appconfig.config import AppConfig

class AppConfigTests(unittest.TestCase):
    def setUp(self):
        self.environ=os.environ.get("APPCONFIG")
        if self.environ is not None:
            del os.environ["APPCONFIG"]

    def tearDown(self):
        if self.environ is not None:
            os.environ["APPCONFIG"]=self.environ

    def testConfigIsReadOnly(self):
        cfg=AppConfig()
        self.assertRaises(NotImplementedError, operator.setitem, cfg, "key", "value")
        self.assertRaises(NotImplementedError, operator.delitem, cfg, "key")
        self.assertRaises(NotImplementedError, cfg.clear)
        self.assertRaises(NotImplementedError, cfg.pop)
        self.assertRaises(NotImplementedError, cfg.popitem)
        self.assertRaises(NotImplementedError, cfg.setdefault, "key", "value")
        self.assertRaises(NotImplementedError, cfg.update, {})

    def testLoadConfig_WithoutClearData(self):
        cfg=AppConfig(key="value")
        cfg.loadConfig(StringIO.StringIO(""))
        self.assertEqual(cfg.items(), [("key", "value")])

    def testLoadConfig_WithClearData(self):
        cfg=AppConfig(key="value")
        cfg.loadConfig(StringIO.StringIO(""), True)
        self.assertEqual(len(cfg), 0)

    def testLoadConfig_ReplaceExistingData(self):
        cfg=AppConfig(section=dict(key="value"))
        cfg.loadConfig(StringIO.StringIO("[section]\nkey=newvalue"))
        self.assertEqual(cfg["section"]["key"], "newvalue")

    def testAutoloadConfig(self):
        import os.path
        cfg=AppConfig()
        os.environ["APPCONFIG"]=os.path.join(os.path.dirname(__file__), "sample.cfg")
        self.assertEqual(cfg.keys(), ["section"])

