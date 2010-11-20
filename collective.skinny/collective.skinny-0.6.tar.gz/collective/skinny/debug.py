from zope import interface

import collective.skinny.interfaces

def activate_public_layer(context, event):
    """Activate the public layer, which might be useful for local
    development.
    """
    interface.directlyProvides(
        event.request, collective.skinny.interfaces.IPublicLayer)
