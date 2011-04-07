from unittest import TestCase
from unittest import makeSuite
from unittest import TestSuite

from zope.interface import Interface
from zope.interface import implements
from zope.interface import providedBy

from archetypes.markerfield.utils import addMarkerInterface
from archetypes.markerfield.utils import removeMarkerInterface


class MarkerInterface(Interface):
    pass


class SecondMarkerInterface(Interface):
    pass


class BaseInterface(Interface):
    pass


class Mock(object):
    pass


class MockWithInterface(object):
    implements(BaseInterface)


class InterfaceTests(TestCase):

    def ifaces(self, obj):
        return [i.getName() for i in providedBy(obj)]

    def testAddNothing(self):
        obj=Mock()
        addMarkerInterface(obj)
        self.assertEqual(self.ifaces(obj), [])

    def testAddSingleInterface(self):
        obj=Mock()
        addMarkerInterface(obj, MarkerInterface)
        self.assertEqual(self.ifaces(obj), ["MarkerInterface"])

    def testAddMultipleInterfaces(self):
        obj=Mock()
        addMarkerInterface(obj, MarkerInterface, SecondMarkerInterface)
        self.assertEqual(self.ifaces(obj),
            ["MarkerInterface", "SecondMarkerInterface"])

    def testAddAdditionalInterface(self):
        obj=MockWithInterface()
        addMarkerInterface(obj, MarkerInterface)
        self.assertEqual(self.ifaces(obj),
            ["MarkerInterface", "BaseInterface"])

    def testRemoveNonPresentInterface(self):
        obj=Mock()
        removeMarkerInterface(obj, MarkerInterface)
        self.assertEqual(self.ifaces(obj), [])

    def testAddAndRemoveSingleInterface(self):
        obj=Mock()
        addMarkerInterface(obj, MarkerInterface)
        removeMarkerInterface(obj, MarkerInterface)
        self.assertEqual(self.ifaces(obj), [])

    def testAddTwoInterfacesAndRemoveOne(self):
        obj=Mock()
        addMarkerInterface(obj, MarkerInterface, SecondMarkerInterface)
        removeMarkerInterface(obj, MarkerInterface)
        self.assertEqual(self.ifaces(obj), ["SecondMarkerInterface"])


def test_suite():
    suite=TestSuite()
    suite.addTest(makeSuite(InterfaceTests))
    return suite
