from zope.schema import Tuple
from zope.interface import implements

from collective.properties.interfaces import IBytesLineTuple


class BytesLineTuple(Tuple):
    """See interface"""
    implements(IBytesLineTuple)
