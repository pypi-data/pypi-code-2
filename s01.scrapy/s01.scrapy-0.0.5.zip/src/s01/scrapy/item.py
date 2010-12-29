###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Scrapy items for xspider.foo project

"""

import zope.schema

import scrapy.item

_marker = object()


class ScrapyItemBase(scrapy.item.BaseItem):
    """Scrapy item based on zope.schema
    
    This scrapy item does not provide a dict API.
    
    The ScrapyItemBase class should use the ScrapyFieldProperty for define 
    the fields which offers validation and supports optional converter and
    serializer methods.

    Note: your custom scrap item must implement an interface. This interface
    is used as the field schema.

    """

    def dump(self):
        """Dump the item field values based on the implemented interfaces to
        json data dict.
        """
        # Note, our data dict is not ordered. Take care if you use this data
        # if order matters, e.g. if you write to a CSV file. If you need to
        # order your export data use zope.schema.getFieldNamesInOrder(iface)
        # in your exporter for get the field ordered names. See zope.schema
        # for more info about field and schema
        data = {}
        for iface in zope.interface.providedBy(self):
            for name in zope.schema.getFieldNames(iface):
                data[name] = getattr(self, name, None)
        return data
