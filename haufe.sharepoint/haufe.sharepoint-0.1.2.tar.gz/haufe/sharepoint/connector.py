# -*- coding: iso-8859-15 -*-

################################################################
# haufe.sharepoint
################################################################

import re
import pprint
import logging
from ntlm import HTTPNtlmAuthHandler
from suds.client import Client
from suds.sax.element import Element
from suds.sax.attribute import Attribute
from suds.transport.https import WindowsHttpAuthenticated
from logger import logger as LOG

import patches

# Sharepoint field descriptors start with *one* underscore (hopefully)
field_regex = re.compile(r'^_[a-zA-Z0-9]') 
_marker = object


class OperationalError(Exception):
    """ Generic error """

class NotFound(Exception):
    """ List item not found """

class DictProxy(dict):
    """ Dict-Proxy for mapped objects providing attribute-style access.
    """

    def __getattribute__(self, name):
        if name in dict.keys(self):
            return self.get(name)
        return super(dict, self).__getattribute__(name) 

    def __getattr__(self, name, default=None):
        if name in dict.keys(self):
            return self.get(name, default)
        return super(dict, self).__getattr__(name, default) 


def Connector(url, username, password, list_id):
    """ Sharepoint SOAP connector factory """
    transport = WindowsHttpAuthenticated(username=username,
                                         password=password,
                                         timeout=50)
    client = Client(url, transport=transport)
    client.set_options(service='Lists', port='ListsSoap12')
    return ListEndpoint(client, list_id)


class ParsedSoapResult(object):
    """ Represent he result datastructure from sharepoint in a 
        mode Pythonic way. The ParsedSoapResult class exposes two attributes:
        ``ok`` - True if all operations completed successfully,
                  False otherwise
        ``result`` - a list of dicts containing the original SOAP
                  response ``code`` and ``text``
    """

    def __init__(self, results):
        self.ok = True
        self.result = list()
        # Stupid SOAP response are either returned as single 'Result'
        # instance or a list (depending on the number of list items touched
        # during one SOAP operation.
        if isinstance(results.Results.Result, (list, tuple)):
            results = [r for r in results.Results.Result]
        else:
            results = [results.Results.Result]
        for item_result in results:
            d = dict(code=item_result.ErrorCode,
                     success=item_result.ErrorCode=='0x00000000')
            for key in ('ErrorText', ):
                value = getattr(item_result, key, _marker)
                if value is not _marker:
                    d[key.lower()] = value

            row = getattr(item_result, 'row', _marker)
            if row is not _marker:
                # should be serialized
                d['row'] = item_result.row

            self.result.append(d)
            if item_result.ErrorCode != '0x00000000':
                self.ok = False

class ListEndpoint(object):

    def __init__(self, client, list_id):
        self.client = client
        self.service = client.service
        self.list_id = list_id
        # perform some introspection on the list
        self.model = self._getFields()       
        self.required_fields = self._required_fields()
        self.all_fields = self.model.keys()
        self.primary_key = self._find_primary_key()

    def _getFields(self):
        """ extract field list """
        list_ = self.service.GetList(self.list_id)
        fields = dict()
        for row in list_.List.Fields.Field:
            if row._Name.startswith('_'):
                continue
            # dictify field description (chop of leading underscore)
            d = dict()
            for k, v in row.__dict__.items():
                if field_regex.match(k):
                    # chop of leading underscore
                    d[unicode(k[1:])] = v
            fields[row._Name] = d
        return fields

    def _find_primary_key(self):
        """ Return the name of the primary key field of the list """
        for k, field_d in self.model.items():
            if field_d.get('PrimaryKey') == u'TRUE':
                return k
        raise OperationalError('No primary key found in sharepoint list description')

    def _required_fields(self):
        """ Return the list of required field names in Sharepoint """
        return [d['Name'] for d in self.model.values() if d.get('Required') == 'TRUE']

    def _serializeListItem(self, item):
        """ Serialize a list item as dict """
        d = DictProxy()
        for fieldname in self.model:
            v = getattr(item, '_ows_' + fieldname, _marker)
            if v is _marker:
                v = None
            d[fieldname] = v 
        return d

    def _preflight(self, data, primary_key_check=True):
        """ Perform some sanity checks on data """

        # data must include the value of the primary key field            
        value_primary_key = data.get(self.primary_key)
        if primary_key_check and value_primary_key is None:
            raise ValueError('No value for primary key "%s" found in update dict (%s)' % (self.primary_key, d))

        data_keys = set(data.keys())
        all_fields = set(self.all_fields)
        if not data_keys.issubset(all_fields):
            disallowed = ', '.join(list(data_keys - all_fields))
            raise ValueError('Data dictionary contains fieldnames unknown to the Sharepoint list model (Disallowed field names: %s)' % disallowed)

    def getItems(self, rowLimit=999999999):
        """ Return all list items without further filtering """
        items = self.service.GetListItems(self.list_id, rowLimit=rowLimit)
        return [self._serializeListItem(item) for item in items.listitems.data.row]

    def getItem(self, item_id):
        """ Return all list items without further filtering """
        query0= Element('ns1:query')
        query = Element('Query')
        query0.append(query)
        where = Element('Where')
        query.append(where)
        eq = Element('Eq')
        where.append(eq)
        fieldref = Element('FieldRef').append(Attribute('Name', self.primary_key))
        value = Element('Value').append(Attribute('Type', 'Number')).setText(item_id)
        eq.append(fieldref)
        eq.append(value)
        viewfields = Element('ViewFields')
        viewfields.append(Element('FieldRef').append(Attribute('Name', self.primary_key)))
        viewName = Element('viewName')
        queryOptions = Element('queryOptions')
        result = self.service.GetListItems(self.list_id, 
                                          viewName=viewName, 
                                          query=query0,  
                                          viewFields=viewfields, 
                                          queryOptions=queryOptions, 
                                          rowLimit=1)

        if int(result.listitems.data._ItemCount) > 0:
            return self._serializeListItem(result.listitems.data.row[0])
        return []

    def deleteItems(self, *item_ids):
        """ Remove list items given by value of their primary key """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Continue')).append(Attribute('ListVersion','1'))
        for i, item_id in enumerate(item_ids):
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'Delete'))
            method.append(Element('Field').append(Attribute('Name', self.primary_key)).setText(item_id))
            batch.append(method)
        updates = Element('ns0:updates')
        updates.append(batch)
        result = self.service.UpdateListItems(self.list_id, updates)
        return ParsedSoapResult(result)

    def updateItems(self, *update_items):
        """ Update list items as given through a list of update_item dicts
            holding the data to be updated. The list items are identified
            through the value of the primary key inside the update dict.
        """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Continue')).append(Attribute('ListVersion','1'))
        for i, d in enumerate(update_items):
            self._preflight(d)
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'Update'))
            for k,v in d.items():
                method.append(Element('Field').append(Attribute('Name', k)).setText(v))
            batch.append(method)
        updates = Element('ns0:updates')
        updates.append(batch)
        result = self.service.UpdateListItems(self.list_id, updates)
        return ParsedSoapResult(result)

    def addItems(self, *addable_items):
        """ Add a sequence of items to the list. All items must be passed as dict.
            The list of assigned primary key values should from the 'row' values of 
            the result object.
        """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Continue')).append(Attribute('ListVersion','1'))
        for i, d in enumerate(addable_items):
            self._preflight(d, primary_key_check=False)
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'New'))
            for k,v in d.items():
                method.append(Element('Field').append(Attribute('Name', k)).setText(v))
            batch.append(method)
        updates = Element('ns0:updates')
        updates.append(batch)
        result = self.service.UpdateListItems(self.list_id, updates)
        return ParsedSoapResult(result)

