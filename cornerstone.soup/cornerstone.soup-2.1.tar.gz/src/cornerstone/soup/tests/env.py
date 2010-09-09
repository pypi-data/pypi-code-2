# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com
from zope.interface import implements
from zope.catalog.catalog import Catalog
from zope.catalog.field import FieldIndex
from zope.catalog.text import TextIndex
from zope.catalog.keyword import KeywordIndex
from cornerstone.soup.interfaces import ICatalogFactory

class MyCatalogFactory(object):
    """ICatalogFactory implementation used for testing.
    """

    implements(ICatalogFactory)
    
    catalog = Catalog()
    catalog[u'user'] = FieldIndex(field_name='user',
                                  field_callable=False)
    catalog[u'text'] = TextIndex(field_name='text',
                                 field_callable=False)
    catalog[u'keywords'] = KeywordIndex(field_name='keywords',
                                        field_callable=False)

    def __call__(self):
        return self.catalog