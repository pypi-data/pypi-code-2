from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from OFS.SimpleItem import SimpleItem
from persistent import Persistent

from slc.clicksearch.interfaces import IClickSearchConfiguration

BLACKLIST = 'Blacklist'
WHITELIST = 'Whitelist'
SAFE_INDEXES = ['Subject']

class ClickSearchConfiguration(Persistent):
    implements(IClickSearchConfiguration)
    search_metadata = FieldProperty(IClickSearchConfiguration['search_metadata'])
    sort_indexes = FieldProperty(IClickSearchConfiguration['sort_indexes'])

def form_adapter(context):
    return getUtility(IClickSearchConfiguration, 
                      name='clicksearch_config', 
                      context=context)

