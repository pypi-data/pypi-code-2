# -*- coding: utf-8 -*-
import re
from zope.interface import implements
from zope.interface import Interface
from zope import schema

from zope.schema.interfaces import ISource, IContextSourceBinder

from sc.contentrules.movebyattribute.vocabulary import RelPathSearchableTextSource as SearchableTextSource

from sc.contentrules.movebyattribute import MessageFactory as _

ATTRPATTERN = '^[A-Za-z][A-Za-z_0-9]*$'

class InvalidAttribute(schema.ValidationError):
    "Invalid attribute name"

def validate_attribute(value):
    if not re.match(ATTRPATTERN,value):
        raise InvalidAttribute(value)
    return True

class SearchableTS(object):
    implements(IContextSourceBinder)
    
    def __init__(self, query, default_query=None):
        self.query = query
        self.default_query = default_query
    
    def __call__(self, context):
        context = getattr(context, 'context', context)
        results = SearchableTextSource(context, base_query=self.query.copy(),
                                       default_query=self.default_query)
        return results


class IMoveByAttributeAction(Interface):
    """An action used to move an object into an existing folder with the same
       id from the inspected attribute
    """
    
    attribute = schema.TextLine(title=_(u"Attribute"),
                      description=_(u"Please inform the attribute name that \
                                      will provide the value -- must be a \
                                      string -- for this action \
                                      e.g.: Creator"),
                      required=True,
                      constraint=validate_attribute,
                      default=u'Creator',
                )
        
    base_folder = schema.Choice(title=_(u"Base folder"),
                                description=_(u"Choose the base folder to be \
                                                searched for the folderish \
                                                content with the id provided \
                                                by the attribute above ."),
                                required=True,
                                source=SearchableTS({'is_folderish' : True},
                                                      default_query='path:')
                        )
    
    
