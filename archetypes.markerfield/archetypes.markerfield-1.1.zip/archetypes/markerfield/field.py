from Products.Archetypes.atapi import BooleanField

from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield.utils import addMarkerInterface
from archetypes.markerfield.utils import removeMarkerInterface


class BaseInterfaceMarkerField(BooleanField):
    """Archetypes field to manage marker interface.

    This is a boolean field which will set or unset one or more marker
    interfaces on an object.
    """

    def get(self, instance, **kwargs):
        for iface in self.interfaces:
            if not iface.providedBy(instance):
                return False
        return True

    def getRaw(self, instance, **kwargs):
        return self.get(instance)

    def set(self, instance, value, **kwargs):
        if value:
            addMarkerInterface(instance, *self.interfaces)
        else:
            removeMarkerInterface(instance, *self.interfaces)


class InterfaceMarkerField(ExtensionField, BaseInterfaceMarkerField):
    """This field can be used with archetypes.schemaextender. It is commonly
    used to manage optional behaviour for existing content types.
    """
