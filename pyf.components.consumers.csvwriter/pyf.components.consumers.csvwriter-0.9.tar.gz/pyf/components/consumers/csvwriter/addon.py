"""CSVAddon is used to extend a adapted object, it appends keys and get method (dictionnary method)
csv.DictWriter instance need a dictionnary to work
"""
import logging

log = logging.getLogger()

class RendererError(ValueError):
    pass

class CSVAddon(object):

    def __init__(self, obj, column_definitions, renderers, encoding):
        """Initialize a CSVAddon
        @param obj: The adapted object, example for asset, the obj is SQLSunAssetAdapter(<SunAsset instance>)
        @type obj: ObjectAdapter instance

        @param column_definitions: dictionnary that contain {<Column name>:<Column attribute>},
        the column attribute is a adapted object field
        @type column_definitions: dictionnary

        @param renderers: dictionnary that contain {<Column attribute>:<renderer_code>}
        @type renderers: dictionnary

        @param encoding: Encoding to use to encode all string value before serialize
        @type encoding: String
        """
        self.obj = obj
        self.column_definitions = column_definitions
        self.renderers = renderers
        self.encoding = encoding
        self.__init_column_maps()

    def __init_column_maps(self):
        self.column_maps = dict()
        for value, key in self.column_definitions:
            self.column_maps[key] = value

    def keys(self):
        """Dictionnary method needed by the DictWriter
        """
        return self.column_maps.keys()

    def __iter__(self):
        """Dictinnary method needed by the DictWriter from 2.6
        """
        return self.column_maps.iterkeys()

    def get(self, column_name, default_value):
        """Dictionnary method needed by the DictWriter
        """
        attr_name = self.column_maps.get(column_name, None)
        data = getattr(self.obj, attr_name, default_value)

        renderer_code = self.renderers.get(attr_name, None)

        if isinstance(data, unicode):
            encoded_data = data.encode(self.encoding)
        else:
            encoded_data = data

        if not renderer_code is None:
            encoded_data = self.__do_renderer(encoded_data, renderer_code)

        return encoded_data

    def __do_renderer(self, value, renderer_code):
        import decimal
        import datetime
        #log.debug('rendering %s with %s' % (value, renderer_code))
        try:
            return eval(renderer_code)
        except Exception, e:
            return value
