# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
from zope.schema import TextLine, Text
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.interfaces import IDCDescriptiveProperties

_ = MessageFactory('zope')


class IDescriptiveSchema(IAttributeAnnotatable, IDCDescriptiveProperties):
    """Marker interface for a Dolmen content.
    """
    title = TextLine(
        title=_(u"Title"),
        required=True)

    description = Text(
        title=_(u'Description'),
        required=False,
        default=u"")
