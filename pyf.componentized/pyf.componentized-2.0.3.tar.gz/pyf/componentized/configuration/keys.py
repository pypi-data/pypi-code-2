from pyf.componentized import ET
from pyf.componentized.configuration.fields import InputField, TextAreaField,\
    ListField, MultipleFields, BooleanField
from tw.forms.fields import ListFieldSet

class ComponentConfiguration(object):
    pass

class ConfigurationKey(object):
    def __init__(self, key, default=None, field=None, label=None, help_text=None):
        self.key = key
        self.default = default

        self._label = label
        self.help_text = help_text

        if field is None:
            self.field = self.get_default_field()
        else:
            self.field = field

    @property
    def label(self):
        return self._label or self.key.capitalize()

    def get_default_field(self):
        return InputField(self.key,
                          default=self.default,
                          label=self.label,
                          help_text=self.help_text)

    def to_xml(self, value):
        raise NotImplementedError, "Method to_xml isn't implemented for %s" % self.key

    def from_xml(self, node, default=None):
        raise NotImplementedError, "Method from_xml isn't implemented for %s" % self.key
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Simple key/value",
                    help_text=self.help_text,
                    default=self.default)

class SimpleKey(ConfigurationKey):
    def to_xml(self, value):
        el = ET.Element(self.key)
        el.text = value
        return el

    def from_xml(self, node, default=None):
        if node is None or node.text is None:
            return default
 
        return node.text
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Simple key/value (text-based)",
                    help_text=self.help_text,
                    default=self.default)

class CDATAKey(SimpleKey):
    def get_default_field(self):
        return TextAreaField(self.key, default=self.default)

    def to_xml(self, value):
        el = ET.Element(self.key)
        if hasattr(ET, 'CDATA'):
            el.text = ET.CDATA(value)
        else:
            el.text = value
        return el
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="CDATA key",
                    help_text=self.help_text,
                    default=self.default)

class XMLKey(CDATAKey):
    def get_default_field(self):
        return TextAreaField(self.key, label=self.label, default=self.default, classname="xmlcode")
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="XML CDATA Key",
                    help_text=self.help_text)

class PythonKey(CDATAKey):
    def get_default_field(self):
        return TextAreaField(self.key, label=self.label, default=self.default, classname="pythoncode")
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Python CDATA Key",
                    help_text=self.help_text,
                    default=self.default)

class CompoundKey(ConfigurationKey):
    def __init__(self, key,
                 text_value=None,
                 text_as_cdata=False,
                 attributes=None,
                 fields=None,
                 **kwargs):
        super(CompoundKey, self).__init__(key, **kwargs)

        if text_value is None and attributes is None:
            raise ValueError, "No content definition for %s" % self.key

        self.text_value = text_value
        self.text_as_cdata = text_as_cdata
        self.attributes = attributes

        if not fields is None:
            self.field = self.get_group_field(fields)

    def get_default_field(self):
        # we return none here, we will set our default field witb content.
        return None

    def get_group_field(self, fields):
        return MultipleFields(self.key, fields=fields, default=self.default)

    def to_xml(self, value):
        el = ET.Element(self.key)

        if self.text_value is not None:
            if self.text_as_cdata and hasattr(ET, 'CDATA'):
                el.text = ET.CDATA(value.get(self.text_value))
            else:
                el.text = value.get(self.text_value)

        if self.attributes is not None:
            for xml_attribute, python_key in self.attributes.items():
                if value.get(python_key) is not None:
                    el.set(xml_attribute, value.get(python_key))

        return el

    def from_xml(self, node, default=None):
        value = dict()

        if node is None:
            return default

        if self.text_value is not None:
            value[self.text_value] = node.text

        if self.attributes is not None:
            for xml_attribute, python_key in self.attributes.items():
                value[python_key] = node.get(xml_attribute)

        return value
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Compound key (\"%s\" key is the text content of the node)" % self.text_value,
                    help_text=self.help_text,
                    sub_keys=[dict(key=v.name,
                                   label=v.label,
                                   help_text=v.help_text,
                                   type_info=v.type,
                                   default=v.default) for v in self.field.fields],
                    default=self.default)
        
class ComplexCompoundKey(ConfigurationKey):
    def __init__(self, key,
                 content=None,
                 collapsible=False,
                 collapsed=False,
                 **kwargs):
        super(ComplexCompoundKey, self).__init__(key, **kwargs)

        if content is None:
            raise ValueError, "No content definition for %s" % self.key
        
        self.collapsible = collapsible
        self.collapsed = collapsed
        
        self.content = content
        self.content_dict = dict([(key.key, key) for key in self.content])
        
        self.field = self.get_group_field()

    def get_default_field(self):
        # we return none here, we will set our default field witb content.
        return None

    def get_group_field(self):
        return MultipleFields(self.key,
                              fields=[key.field for key in self.content],
                              default=self.default,
                              collapsible=self.collapsible,
                              collapsed=self.collapsed,
                              label=self.label)

    def to_xml(self, value):
        el = ET.Element(self.key)

#        if self.text_value is not None:
#            if self.text_as_cdata and hasattr(ET, 'CDATA'):
#                el.text = ET.CDATA(value.get(self.text_value))
#            else:
#                el.text = value.get(self.text_value)
#
#        if self.attributes is not None:
#            for xml_attribute, python_key in self.attributes.items():
#                el.set(xml_attribute, value.get(python_key))

        for key, item in value.iteritems():
            if key in self.content_dict:
                sel = self.content_dict[key].to_xml(item)
                if getattr(self.content_dict[key], 'gets_node_list', False):
                    for ssel in sel:
                        el.append(ssel)
                else:
                    el.append(sel)

        return el

    def from_xml(self, node, default=None):
        value = dict()

        if node is None:
            return default
        
        for tag_name, key_obj in self.content_dict.items():
            if getattr(key_obj, 'gets_node_list', False):
                value[tag_name] = key_obj.from_xml(node.findall(tag_name))
            else:
                value[tag_name] = key_obj.from_xml(node.find(tag_name))
                
        return value
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Compound key (each sub key is an individual tag)",
                    help_text=self.help_text,
                    sub_keys=[dict(key=v.key,
                                   label=v.label,
                                   help_text=v.help_text,
                                   type_info=v.field.type,
                                   default=v.default) for v in self.content],
                    default=self.default)

class RepeatedKey(ConfigurationKey):
    def __init__(self, key,
                 each_key=None,
                 content=None,
                 collapsible=False,
                 first_level_list=False,
                 **kwargs):
        super(RepeatedKey, self).__init__(key, **kwargs)
        self.each_key = each_key
        
        self.first_level_list = first_level_list
        
        if not self.first_level_list:
            self.each_key = each_key
            self.gets_node_list = False
            
        else:
            self.each_key = key
            self.gets_node_list = True

        if content is not None:
            self.content = content
            self.field = self.get_repeated_field(content, collapsible=collapsible)

    def get_default_field(self):
        # we return none here, we will set our default field witb content.
        return None

    def get_repeated_field(self, content, collapsible=False):
        return ListField(self.key, content=content.field, default=self.default,
                         collapsible=collapsible, label=self._label)

    def to_xml(self, value):
        if self.first_level_list:
            elements = list()
            for item in value:
                sel = self.content.to_xml(item)
                elements.append(sel)
            return elements
        else:
            el = ET.Element(self.key)
    
            for item in value:
                sel = self.content.to_xml(item)
                el.append(sel)
    
            return el

    def from_xml(self, node, default=None):
        if self.first_level_list:
            if node is None or len(node) == 0:
                return default
            
            nodes = node
        else:
            if node is None or len(node.findall(self.content.key)) == 0:
                return default
                
            nodes = node.findall(self.content.key)
            
        values = list()

        for item in nodes:
            values.append(self.content.from_xml(item))

        return values
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info=(self.first_level_list and "Repeated Key."
                               or "Key with repeated %s content" % self.content.key),
                    help_text=self.help_text,
                    content_title=(self.first_level_list
                                   and "Key can be repeated, content:"
                                   or "Key contains repeated items \"%s\":" % self.content.key),
                    content=self.content.document(),
                    default=self.default)

class BooleanKey(ConfigurationKey):
    def get_default_field(self):
        return BooleanField(self.key,
                          default=(self.default is not None and self.default or False),
                          label=self.label,
                          help_text=self.help_text)

    def to_xml(self, value):
        el = ET.Element(self.key)
        el.text = str(bool(value))

        return el

    def from_xml(self, node, default=None):
        if node is None or node.text is None:
            return default

        return node.text.strip().lower() in ['on', 'true', 'yes']
    
    def document(self):
        return dict(key=self.key,
                    label=self._label,
                    type_info="Boolean Key ('on', 'true' and 'yes', case insensitive are True)",
                    help_text=self.help_text,
                    default=self.default)
