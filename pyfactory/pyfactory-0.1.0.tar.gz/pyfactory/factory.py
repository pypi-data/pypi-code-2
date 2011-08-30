"""
Contains the Factory base class and metaclass for all the
factories created by PyFactory.
"""

from field import Field

class FactoryMetaclass(type):
    """
    The metaclass for all factories which inspects the defined
    factory methods and creates the proper special methods.
    """
    def __new__(self, cls, bases, attrs):
        schemas   = {}
        new_attrs = { '_pyfactory_schemas': schemas }

        # Inherit the schemas from the base classes, if any.
        for base in bases:
            if hasattr(base, '_pyfactory_schemas'):
                schemas.update(base._pyfactory_schemas)

        # Find the schemas from the current class. Since we're doing this
        # after we inherit from the base classes, any new schemas will override
        # the base classes, which is expected behavior.
        for key,val in attrs.iteritems():
            # We're only interested in callable things which are marked
            # as pyfactory
            if not hasattr(val, '_pyfactory') or not callable(val):
                new_attrs[key] = val
                continue

            # We have a pyfactory method, add it to the list of available
            # builders...
            schemas[key] = val

        return super(FactoryMetaclass, self).__new__(self, cls, bases, new_attrs)

class Factory(object):
    """
    Base class for all created factories.
    """
    __metaclass__ = FactoryMetaclass

    def attributes(self, schema, _pyfactory_scope="attributes", **kwargs):
        """
        This returns the attributes for a particular schema. The attributes
        are returned as a dict instead of the model.
        """
        if not schema in self._pyfactory_schemas:
            raise NameError, "Schema %s doesn't exist!" % schema

        # Get the raw result and update it with any overrides from kwargs
        result = self._pyfactory_schemas[schema](self)
        result.update(kwargs)

        # Iterate through the result, replacing any special fields as
        # needed...
        for key,val in result.iteritems():
            if isinstance(val, Field):
                result[key] = val.resolve(_pyfactory_scope)

        return result

    def build(self, schema, **kwargs):
        """
        This builds a model but does not save it.
        """
        attributes = self.attributes(schema, _pyfactory_scope="build", **kwargs)
        return self._model_builder.build(self._model, attributes)

    def create(self, schema, **kwargs):
        """
        This builds a model based on the schema with the givne name
        and saves it, returning the new model.
        """
        attributes = self.attributes(schema, _pyfactory_scope="create", **kwargs)
        return self._model_builder.create(self._model, attributes)
