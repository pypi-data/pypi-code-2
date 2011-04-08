from zope import interface
import zope.component.interfaces

class FrozenError(Exception):
    """The object is already frozen and cannot be changed."""

class FreezeError(Exception):
    """The object is unable to be frozen at this time."""

class IObjectFrozenEvent(zope.component.interfaces.IObjectEvent):
    """The object is being frozen"""

class ObjectFrozenEvent(zope.component.interfaces.ObjectEvent):
    """Object was frozen"""

    interface.implements(IObjectFrozenEvent)

class IFreezable(interface.Interface):
    """Marker interface specifying that it is desirable to adapt the object to
    IFreezing"""

class IFreezing(IFreezable):
    _z_frozen = interface.Attribute(
        """Boolean, whether the object is frozen.  Readonly""")

    _z_freeze_timestamp = interface.Attribute(
        "datetime.datetime in pytz.utc of when frozen, or None.  Readonly.")

    def _z_freeze():
        """sets _z_frozen to True, sets _z_freeze_timestamp, and fires
        ObjectFrozenEvent.  Raises FrozenError if _z_frozen is already True."""

class ITokenEnforced(interface.Interface):
    """A marker interface indicating that the instance wants to have its
    freezing enforced by zope.locking tokens (see the subscribers module).
    """

class IData(interface.Interface):
    """An object used to store freezing data for another object.  Useful for
    the copy hook.  Only of internal interest."""

    _z_freeze_timestamp = interface.Attribute(
        "datetime.datetime in pytz.utc of when frozen, or None.")
