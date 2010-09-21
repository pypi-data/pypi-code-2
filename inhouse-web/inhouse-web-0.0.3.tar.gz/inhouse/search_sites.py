# -*- coding: utf-8 -*-

import haystack
from haystack import indexes
from haystack.indexes import SearchIndex

# Import loop beim syncen?
#from inhouse.models import Booking


haystack.autodiscover()

#class BookingIndex(SearchIndex):

    #text = indexes.CharField(document=True, use_template=True)
    #title = indexes.CharField(model_attr='title')


#haystack.site.register(Booking, BookingIndex)

