from zope import interface
from zope import schema

from zope.dublincore.interfaces import IDCDescriptiveProperties

from collective.formlib.link import MessageFactory as _

class ILink(interface.Interface):
    def pretty_title_or_uri():
        pass

class IExternalLink(ILink, IDCDescriptiveProperties):
    uri = schema.TextLine(
        title=_(u"URI"),
        required=True)

class IInternalLink(ILink, IDCDescriptiveProperties):
    reference = schema.TextLine(
        title=_(u"Weak reference to an internal object."),
        required=True)
