from unittest import TestCase, defaultTestLoader, main
from Testing import ZopeTestCase as ztc
import zope.component
from StringIO import StringIO
import plone.i18n.normalizer
from Products.Five import zcml

from collective.amberjack.core import utils
from collective.amberjack.core.tour import Tour

class ConfigTests(ztc.ZopeTestCase):

    def setUp(self):
        zcml.load_config('meta.zcml', zope.component)
        zcml.load_config('configure.zcml', plone.i18n.normalizer)
        zcml.load_string('''<configure
        xmlns="http://namespaces.zope.org/zope">
        <utility component="collective.amberjack.core.blueprints.Step"
                 name="collective.amberjack.blueprints.step" />
        </configure>''')

        zcml.load_string('''<configure
        xmlns="http://namespaces.zope.org/zope">
        <utility component="collective.amberjack.core.blueprints.MicroStep"
                 name="collective.amberjack.blueprints.microstep" />
        </configure>''')

    def test_load_config(self):
        conf = StringIO()
        conf.write("""[amberjack]
title = "Add and publish a Folder"
steps =
""")
        conf.seek(0)
        self.assertEqual(utils._load_config(conf)['amberjack']['title'], '"Add and publish a Folder"')

    def test_create_tour(self):
        conf = StringIO()
        conf.write("""[amberjack]
title = "Add and publish a Folder"
steps =
  mystep1
[mystep1]
blueprint = collective.amberjack.blueprints.step
url = "/"
title = "Create a new folder"
text = "Descritpion of the step"
microsteps =
""")
        conf.seek(0)
        tour1 = Tour(conf, 'collective.amberjack.tests')
        self.assertEqual(len(tour1.steps), 1)

class UnitTests(TestCase):

    def testSimple(self):
        print 1

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
