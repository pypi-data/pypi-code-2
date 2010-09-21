from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.interface import Interface

class ITransformSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the transform menu.
    """

class ITransformMenu(IBrowserMenu):
    """The transform menu.
    This gets its menu items from image transformations.
    """


class ITransformMenuLayer(Interface):
    """
    A layer specific to this product. Is registered using browserlayer.xml
    """

