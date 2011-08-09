from plone.indexer.decorator import indexer
from Products.ATContentTypes.interface import IATContentType


@indexer(IATContentType)
def responsibleperson_indexer(obj):
    """A method for indexing 'responsible person' field of content
    """
    field = obj.Schema().getField('responsibleperson')
    if field is not None:
        return field.get(obj)
    else:
        raise AttributeError
