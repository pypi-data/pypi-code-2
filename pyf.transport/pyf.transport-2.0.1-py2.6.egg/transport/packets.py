from simplejson.encoder import JSONEncoder
from simplejson import loads
import operator
import datetime
import decimal
#from dateutil import parser as dateparser
from itertools import imap, izip

from pyf.splitter.inputsplitter import input_item_separator, tokenize,\
    EndOfFileError
import re

class Packet(object):
    """ A packet is a dictionnary-like object that is easily serializable to
    simple dictionnaries with base data types.
    
    Its members can be accessed either with attributes or items::
    
        >>> my_packet.foo = 'bar'
        >>> my_packet.foo == my_packet['foo']
        True
        
        >>> my_packet['foo'] == 'bar'
        True
    
    It takes an optionnal dictionnary as argument for initialization, to have its
    data set as the initialization data for the packet (if data_type is set to "simple")::
        
        >>> my_packet = Packet(dict(foo="bar"))
        >>> my_packet['foo'] == 'bar'
        True
    
    To serialize, deserialize it, just access the serialized argument::
        
        >>> my_packet.serialized
        {'foo': {'metadata': {'compound': False,
                      'multi_values': False,
                      'type': 'string'},
         'value': 'bar'}}
        
        >>> import datetime
        >>> my_complex_packet = Packet(dict(now=datetime.datetime.now(),
        ...                                 test='bar'))
        
        >>> my_complex_packet
        {'test': 'bar', 'now': datetime.datetime(2010, 12, 16, 12, 23, 47, 259568)}
        
        >>> my_complex_packet.serialized
        {'now': {'metadata': {'compound': False,
                              'multi_values': False,
                              'type': 'datetime'},
                 'value': '2010-12-16T12:23:47.259568'},
         'test': {'metadata': {'compound': False,
                               'multi_values': False,
                               'type': 'string'},
                  'value': 'bar'}}
        >>> my_new_packet = Packet(data=my_complex_packet.serialized, data_type="serialized")
        >>> my_new_packet.now
        datetime.datetime(2010, 12, 16, 12, 23, 47)
        >>> my_complex_packet.test
        'bar'
    """
    
    def __init__(self, data=None, data_type="simple"):
        super(Packet, self).__init__()
        
        if data is None:
            self.__data = dict()
        else:
            if data_type == "simple":
                self.__data = self.prepare_data_dict(data)
            elif data_type == "serialized":
                self.__data = self.unserialize_data_dict(data)
            elif data_type == "prepared":
                self.__data = data
            
        self.__initialised = True
        
    def itervalues(self):
        return imap(operator.itemgetter('value'), self.__data.itervalues())
    
    def iterkeys(self):
        return self.__data.iterkeys()
    __iter__ = iterkeys
            
    def iteritems(self):
        return izip(self.iterkeys(), self.itervalues())
    
    def items(self):
        return list(self.iteritems())
    
    def keys(self):
        return list(self.iterkeys())
    
    properties = property(keys)
    
    def values(self):
        return list(self.itervalues())
    
    def prepare_data_dict(self, data):
        data_dict = dict()
        for key, value in data.iteritems():
            value, metas = self.__get_bare_metadata(value)
            
            data_dict[key] = dict(value = value,
                                  metadata = metas)
        return data_dict
    
    def unserialize_data_dict(self, data):
#        return dict([(key, dict(value=self.unserialize_value(vd['value'], vd['metadata']),
#                                metadata=vd['metadata']))
#                     for key, vd in data.items()])

        for vd in data.values():
            vd['value'] = self.unserialize_value(vd['value'], vd['metadata'])
        return data
                
    def __setitem__(self, attribute, value):
        self.__data[attribute] = dict()
        self.__data[attribute]['metadata'] = dict()
        self.__data[attribute]['value'] = value
        
        self.__generate_bare_metadata(attribute)
                
    def __setattr__(self, attribute, value):
        if not self.__dict__.has_key('_Packet__initialised'):
            return object.__setattr__(self, attribute, value)
        elif self.__dict__.has_key(attribute):
            object.__setattr__(self, attribute, value)
        else:
            self.__setitem__(attribute, value)
    
    def __generate_bare_metadata(self, field):
        value = self.__data[field]['value']
        value, metas = self.__get_bare_metadata(value)
        self.__data[field]['value'] = value
        for key, value in metas.iteritems():
            self.set_metadata(field, key, value)
        
    def __get_bare_metadata(self, value):
        metas = dict()
        
        metas['multi_values'] = False
        metas['compound'] = False
        
        if isinstance(value, str) or isinstance(value, unicode):
            metas['type'] = 'string'
        elif isinstance(value, int):
            metas['type'] = 'int'
        elif isinstance(value, datetime.datetime):
            metas['type'] = 'datetime'
        elif isinstance(value, decimal.Decimal):
            metas['type'] = 'decimal'
        elif isinstance(value, datetime.date):
            metas['type'] = 'date'
        elif isinstance(value, list):
            metas['multi_values'] = True
            metas['type'] = 'unknown'
            
        elif isinstance(value, dict):
            metas['multi_values'] = True
            metas['compound'] = True
            metas['type'] = 'packet'
            value = Packet(value, data_type="simple")
            
        elif isinstance(value, Packet):
            metas['multi_values'] = True
            metas['compound'] = True
            metas['type'] = 'packet'
        
        else:
            metas['type'] = 'unknown'
            
        return value, metas
    
    def __hasattr__(self, attribute):
        return bool(attribute in self.__data) or bool(attribute in self.__dict__)
    __contains__ = has_key = __hasattr__
    
    def __getitem__(self, attribute):
        return self.__getattr__(attribute)
    
    def get(self, key, default=None):
        return self.__data.get(key, dict()).get('value', default)
    
    def __getattr__(self, attribute):
        if not attribute in self.__data:
            raise AttributeError, "'packet' object has no attribute '%s'" % attribute
        
        return self.__data[attribute].get('value')
    
    def __delitem__(self, key):
        del self.__data['key']
        
    def __getstate__(self):
        return self.serialized
    
    def __setstate__(self, dictobj):
        self.__data = self.unserialize_data_dict(dictobj)
        
    def set_metadata(self, field, key, value):
        self.__data[field]['metadata'][key] = value
        
    def get_metadata(self, field, key=None):
        if key is not None:
            return self.__data[field].get('metadata', dict()).get(key)
        else:
            return self.__data[field].get('metadata', dict())
    
    def serialize_value(self, value, metadata):
        metatype = metadata['type']
        if metatype == 'unknown':
            if isinstance(value, int):
                metadata['type'] = metatype = 'int'
            if isinstance(value, datetime.date):
                metadata['type'] = metatype = 'date'
            elif isinstance(value, datetime.datetime):
                metadata['type'] = metatype = 'datetime'
                
        if metatype == 'string' or metatype == 'int':
            pass
        elif metatype == 'date':
            value = value.isoformat()
        elif metatype == 'datetime':
            value = value.isoformat('T')
        elif metatype == 'decimal':
            value = str(value)
        elif metatype == 'packet':
            value = value.serialized
        elif metadata['multi_values']:
            md = metadata.copy()
            md['multi_values'] = False
            value = [self.serialize_value(oneval, md) for oneval in value]
        
        return dict(value=value, metadata=metadata)
    
    def unserialize_value(self, value, metadata):
        metatype = metadata['type']        
        if metatype == 'int' or metatype == 'string':
            pass
        elif metatype == 'date':
            value = datetime.date(*map(int, value.split('-')))
        elif metatype == 'datetime':
            value = datetime.datetime(*map(int, re.split('[^\d]', value)[:-1]))
        elif metatype == 'decimal':
            value = decimal.Decimal(value)
        elif metatype == 'packet':
            value = Packet(value, data_type="serialized")
        elif metadata.get('multi_values', False):
            value = [self.unserialize_value(val.get('value'),
                                            val.get('metadata'))
                     for val in value]
            
        return value
    
    @property
    def serialized(self):
        output_dict = dict()
        for key, key_dict in self.__data.iteritems():
            value = key_dict['value']
            metadata = key_dict['metadata']
            value = self.serialize_value(value, metadata)
            output_dict[key] = value
        
        return output_dict
    
    def __str__(self):
        return str(dict(self.iteritems()))
    
    def __repr__(self):
        return repr(dict(self.iteritems()))
    
    def __contains(self, key):
        return bool(key in self.__data)
    
    def pop(self, key, d=Ellipsis):
        try:
            dict_val = self.__data.pop(key)
            return dict_val['value']
        except KeyError:
            if d == Ellipsis:
                raise KeyError, key
            else:
                return d
    
    @classmethod
    def deserialize(cls, value_dict):
        return cls(value_dict, data_type="serialized")
    
class PacketEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Packet) or hasattr(o, 'serialized'):
            return o.serialized
            
        return JSONEncoder.default(self, o)
    
def encode_packet_flow(object_flow,
                       separator=input_item_separator,
                       iterencode=False,
                       compress=False):
    """ Encodes a packet flow to a bytestring flow of json serialized packets.
    """
    encoder = PacketEncoder()
    for obj in object_flow:
        if iterencode:
            if compress:
                raise NotImplementedError,\
                      "Can't use iterencode with compress in encode_packet_flow"
            
            for chars in encoder.iterencode(obj):
                yield chars
                
        else:
            val = encoder.encode(obj)
            if compress:
                import zlib
                val = zlib.compress(val)
            
            yield val
        
        yield separator

def decode_packet_flow(source, buffersize=16384,
                       separator=input_item_separator,
                       decompress=False,
                       pure_flow=False):
    """Decodes a packet flow from a source.
    
    If pure_flow is set to False (default), the source is either a file-like of a iterator over strings containing the sepator.
    If pure_flow is True, the source is a generator containing strings without the separator.
    
    If decompress is set to True, the data is decompressed using zlib.
    """
    buffer = ""
    
    newdata = "dummy"
    read = hasattr(source, 'read')
    
    while newdata:
        if read:
            newdata = source.read(buffersize)
        else:
            try:
                newdata = source.next()
            except StopIteration:
                newdata = ""
                
        if pure_flow:
            if not newdata:
                raise StopIteration
            
            items = [newdata]
        else:
            items, buffer = tokenize(buffer, separator)
            buffer += newdata
        
        for item in items:
            if decompress:
                import zlib
                item = zlib.decompress(item)
            yield Packet(data=loads(item), data_type="serialized")

    if buffer:
        raise EndOfFileError(
                'Bad file content: EOF reached but buffer not empty')