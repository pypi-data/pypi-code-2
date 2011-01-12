from model.fieldproperties import FieldProperties
from model.converters import *


class FormModel:

    """ Hold properties for form """

    def __init__(self):

        self._props = {}
        self._bindings= {}


    def addFieldProperties(self, prop):

        self._props[prop.id] = prop
        for binding in prop.bind:

            if not self._bindings.has_key(binding):
                self._bindings[binding] = []
                
            self._bindings[binding].append(prop)
        

    def getAllFieldProperties(self):

        return self._props.values()


    def getFieldProperties(self, binding):

        """ Get the properties for the given id, or return default
        properties
        """
      
        return self._bindings.get(binding, [FieldProperties("default", [])])
        

    def isRelevant(self, field_id, data):

        """ Check whether the field id is relevant. This checks all
        relevance rules of all bound properties. If one says 'not relevant',
        this is leading. Defaults to True.
        """

        for props in self.getFieldProperties(field_id):

            try:
                if not eval(props.getRelevant(), {"data": data}):

                    return False
            except:
                return True

        return True


    def isRequired(self, field_id, data):

        for props in self.getFieldProperties(field_id):

            try:
                if eval(props.getRequired(), {"data": data}):

                    return True
            except:
                return False

        return False


    def isReadonly(self, field_id, data):

        for props in self.getFieldProperties(field_id):

            try:
                if eval(props.getReadonly(), {"data": data}):

                    return True
            except:
                return False

        return False


    def meetsConstraint(self, field_id, data):

        meets = True

        for props in self.getFieldProperties(field_id):

            try:
                if not eval(props.getConstraint(), {"data": data}):

                    meets = False
            except:
                pass

        return meets


    def checkDatatype(self, field_id, value):

        """ Check data type of value. Lists (multiple) is also ok. """

        for props in self.getFieldProperties(field_id):

            datatype = props.getDatatype()

            if datatype:

                if hasattr(value, "__iter__"):

                    newvalue = []
                    
                    for val in value:

                        newvalue.append(eval("%s('%s')" % (datatype, val)))

                    return newvalue

                else:

                    return eval("%s('%s')" % (datatype, value))

        return value


    def convert(self, field_id, value):

        """ Convert field tp type given in constraint """

        for props in self.getFieldProperties(field_id):

            datatype = props.getDatatype()

            if datatype:

                try:
                    return eval("%s('%s')" % (datatype, value))
                except:
                    return value

        return value
