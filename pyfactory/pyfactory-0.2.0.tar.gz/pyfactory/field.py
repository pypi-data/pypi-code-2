"""
Contains the special field types for PyFactory.
"""

from error import InvalidModelBuilderError

class Field(object):
    """
    If you wish to implement a custom field value which has
    special behavior, you must inherit and implement the methods
    in this class.
    """

    def resolve(self, scope):
        """
        This method is called by PyFactory to resolve the value of a
        special field. The ``scope`` argument will be one of ``attributes``,
        ``build``, or ``create`` depending on what method was called
        on the factory.

        The return value of this method is what is put into the actual
        attributes dict for the model.
        """
        raise NotImplementedError

class AssociationField(Field):
    """
    This field represents an association with another factory model.
    """

    def __init__(self, factory, schema, attr=None):
        """
        This marks the field value as the result of creating another model
        from another factory.

        If ``attr`` is specified, then that attribute value will be the value
        of the association. This requires that the model builder understand
        the ``getattr`` class method, otherwise an exception will be raised.

        :Parameters:
          - `factory`: An instance of a :class:`Factory` to get the model from.
          - `schema`: The name of the schema to load.
          - `attr` (optional): The name of the attribute to read from the
             resulting model to place as the value of this field. If not
             given, the entire model becomes the value of the field.
        """
        self.factory = factory
        self.schema = schema
        self.attr = attr

    def resolve(self, scope):
        result = getattr(self.factory, scope)(self.schema)

        if self.attr is not None:
            if scope == "attributes":
                # Attributes return dictionaries, so we just use the
                # dictionary syntax to get it...
                result = result[self.attr]
            else:
                # Otherwise we have a model, and we have to use the
                # getattr method on the model builder.
                builder = self.factory._model_builder
                if not hasattr(builder, "getattr") or not callable(builder.getattr):
                    raise InvalidModelBuilderError, \
                        "Model builder must implement `getattr` for associations"

                result = self.factory._model_builder.getattr(result, self.attr)

        return result

class SequenceField(Field):
    """
    This field allows for easily creating values which have a single
    sequential piece in it.
    """

    COUNTS = {}

    def __init__(self, string, interpolation_variable="n", unique_key="_default"):
        """
        This causes the value of a field to be interpolated with
        a sequential value. The ``interpolation_variable`` will be
        the variable name used for interpolation in the string.

        :Parameters:
          - `string`: The string to perform the sequence interpolation on.
          - `interpolation_variable` (optional): The name of the variable to use
            for interpolation in the ``string``.
          - `unique_key` (optional): The unique key to base the sequence creation
            on. By default, every time you call sequence, no matter what model
            factory or schema you're in, the sequence will increase. By specifying
            a unique ``unique_key``, it isolates the increment to that key.
        """
        self.string = string
        self.interpolation_variable = interpolation_variable
        self.unique_key = unique_key

    def resolve(self, scope):
        SequenceField.COUNTS.setdefault(self.unique_key, 0)
        SequenceField.COUNTS[self.unique_key] += 1
        return self.string % \
            { self.interpolation_variable: SequenceField.COUNTS[self.unique_key] }

def association(*args, **kwargs):
    """
    Shortcut method for enabling an association field. See documentation
    of :py:class:`AssociationField`.
    """
    return AssociationField(*args, **kwargs)

def sequence(*args, **kwargs):
    """
    Shortcut method for enabling a sequence field. See documentation of
    :py:class:`SequenceField`.
    """
    return SequenceField(*args, **kwargs)
