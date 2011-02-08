from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plone')

class IAlertsConfiguration(Interface):
    """ Interface for the collective.alerts configlet
    """

    verticalOffset = schema.Int(
                        title=_(u"Horizontal Offset"),
                        description=_(u"The alert dialog's horizontal offset \
                        from the center of the screen, in pixels."),
                        default = 0,
                        required = True,
                        )

    horizontalOffset = schema.Int( 
                            title=_(u"Vertical Offset"),
                            description=_(u"The alert dialog's vertical offset \
                            from the center of the screen, in pixels."),
                            default = 0,
                            required = True,
                            )

    repositionOnResize = schema.Bool(
                            title=_(u"Reposition on resize"),
                            description=_(u"Re-centers the dialog on window \
                            resize."),
                            default = True,
                            required = True,
                            )

    overlayOpacity = schema.Float(
                            title=_(u"Overlay Opacity"),
                            description=_(u"Opacity/Transparency level of the \
                            overlay"),
                            default = 0.3,
                            required = True,
                            )

    overlayColor = schema.TextLine( 
                            title=_(u"Overlay Color"),
                            description=_(u"Base color of the overlay, in \
                            Hexadecimal notation"),
                            default = u'#FFF',
                            required = True,
                            )

    draggable = schema.Bool(
                            title=_(u"Is the alert draggable?"),
                            default = True,
                            required = True,
                            )

    dialogClass = schema.TextLine(      
                        title=_(u"Dialog CSS class"),
                        description=_(u"CSS class that will be applied to all \
                        dialogs"),
                        required = False,
                        )

