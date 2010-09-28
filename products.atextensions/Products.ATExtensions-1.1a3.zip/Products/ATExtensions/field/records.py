from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.standard import html_quote
from Products.Archetypes.Registry import registerField, registerPropertyType
from Products.ATExtensions.config import HAS_VALIDATION_CHAIN
from Products.ATExtensions.field import RecordField
from Products.ATExtensions.widget import RecordsWidget


class RecordsField(RecordField):
    """A field that stores a 'record' (dictionary-like) construct"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'records',
        'default' : [],
        'fixedSize': 0,
        'minimalSize': 0,
        'maximalSize': 9999,
        'innerJoin' : ' ',
        'outerJoin' : ', ',
        'widget' : RecordsWidget,
        })

    security = ClassSecurityInfo()

    def getSize(self, instance):
        """number of records to store"""
        return len(self.getRaw(instance))

    def isSizeFixed(self):
        """do we need an additional line of entry?"""
        return self.fixedSize

    def showMore(self, values):
        """
        return True if the 'More' button should be shown
        False otherwise
        """
        data_length = len(values)
        if data_length < self.maximalSize and not self.fixedSize:
            return True
        else:
            return False

    def getEditSize(self, instance):
        """
        number of record entries to offer in the form
        at least 'minimalSize' or length of the current
        list of records (+1 if 'more' is enabled)
        """
        data_length = len(self.getRaw(instance))
        minimum = max(self.minimalSize, data_length)
        if minimum >= self.maximalSize:
            return minimum  # not to lose data if uploads had added more
        if not self.fixedSize:
            return minimum + 1
        return minimum

    def getSubfieldValue(self, values, idx, subfield, default=None):
        """
        return values[idx].get(key) if existing
        'default' otherwise
        """
        try:
            return values[idx].get(subfield, default)
        except IndexError:
            return default

    def getViewFor(self, instance, idx, subfield, joinWith=', '):
        """
        formatted value of the subfield for display
        """
        raw = self.getRaw(instance)[idx].get(subfield,'')
        if type(raw) in (type(()), type([])):
            raw = joinWith.join(raw)
        # Prevent XSS attacks by quoting all user input
        raw = html_quote(str(raw))
        # this is now very specific
        if subfield == 'email':
            return self.hideEmail(raw,instance)
        if subfield == 'homepage':
            return '<a href="%s">%s</a>' % (raw, raw)
        return raw.strip()

    # store string type subfield values as unicode
    
    def _encode_strings(self, value, instance, **kwargs):
        new_value = []
        for entry in value:
            new_value.append(
                RecordField._encode_strings(self, entry, instance, **kwargs)
                )
        return new_value

    def _decode_strings(self, value, instance, **kwargs):
        new_value = []
        for entry in value:
            new_value.append(
                RecordField._decode_strings(self, entry, instance, **kwargs)
                )
        return new_value

    # convert the records to persistent dictionaries
    def _to_dict(self, value):
        if type(value)!= list or type(value)!=tuple:
            if type(value) == dict:
                value = [value]
            elif type(value) == str:
                try:
                    value = eval(value.replace('}\n', '},'))
                except:
                    pass
        return [RecordField._to_dict(self, entry) for entry in value]

    if HAS_VALIDATION_CHAIN:
        security.declarePublic('validate')
        def validate(self, value, instance, errors={}, **kwargs):
            """
            Validate passed-in value using all subfield validators.
            Return None if all validations pass; otherwise, return failed
            result returned by validator
            """
            name = self.getName()
            if errors and errors.has_key(name):
                return True

            result = None
            for record in value:
                result = RecordField.validate(self,
                                              record,
                                              instance,
                                              errors={},
                                              **kwargs
                                              )
                if result: return result
            return result

InitializeClass(RecordsField)

registerField(RecordsField,
              title="Records",
              description="Used for storing a list of records",
              )

registerPropertyType('subfields', 'lines', RecordsField)
registerPropertyType('required_subfields', 'lines', RecordField)
registerPropertyType('subfield_validators', 'mapping', RecordField)
registerPropertyType('subfield_types', 'mapping', RecordsField)
registerPropertyType('subfield_vocabularies', 'mapping', RecordsField)
registerPropertyType('subfield_labels', 'mapping', RecordsField)
registerPropertyType('subfield_sizes', 'mapping', RecordsField)
registerPropertyType('subfield_maxlength', 'mapping', RecordsField)
registerPropertyType('innerJoin', 'string', RecordsField)
registerPropertyType('fixedSize', 'boolean', RecordsField)
registerPropertyType('minimalSize', 'int', RecordsField)
registerPropertyType('maximalSize', 'int', RecordsField)
