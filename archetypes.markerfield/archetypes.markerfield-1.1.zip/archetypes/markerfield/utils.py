from zope.interface import alsoProvides
from zope.interface import noLongerProvides


def addMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if not iface.providedBy(obj):
            alsoProvides(obj, iface)


def removeMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if iface.providedBy(obj):
            noLongerProvides(obj, iface)
