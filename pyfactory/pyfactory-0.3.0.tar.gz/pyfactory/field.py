"""
Contains the special field types for PyFactory.
"""

from error import InvalidModelBuilderError

class Field(object):
    """
    If you wish to implement a custom field which has special
    behavior, you must inherit and implement the methods in this
    class. Fields are how things such as :py:func:`association` and
    :py:func:`sequence` are implemented.
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
        self.loaded_schema = None

    def _load_schema(self, scope):
        """
        This loads the schema for the given scope. This method exists so
        that the schema is only loaded once.
        """
        if self.loaded_schema is None:
            self.loaded_schema = getattr(self.factory, scope)(self.schema)

        return self.loaded_schema

    def _read_attribute(self, scope, attr):
        """
        This reads the attribute out of the loaded schema based on the
        scope. This function is built as a utility to "do the right thing."
        For example, when loading attributes, this does a simple dictionary
        lookup. But when building or creating, this invokes the model
        builder to read the attribute, since it knows best.
        """
        loaded_schema = self._load_schema(scope)

        if scope == "attributes":
            # Attributes return dictionaries, so we just use the
            # dictionary syntax to get it...
            return loaded_schema[attr]
        else:
            # Otherwise we have a model, and we have to use the
            # getattr method on the model builder.
            builder = self.factory._model_builder
            if not hasattr(builder, "getattr") or not callable(builder.getattr):
                raise InvalidModelBuilderError, \
                    "Model builder must implement `getattr` for associations"

            return self.factory._model_builder.getattr(loaded_schema, attr)

    def resolve(self, scope):
        result = self._load_schema(scope)

        if self.attr is not None:
            result = self._read_attribute(scope, self.attr)

        return result

    def attribute(self, attr):
        """
        :Parameters:
          - `attr`: The name of the attribute to resolve to.

        This will return a new :py:class:`Field` instance which resolves to
        the value of the given ``attr`` of this association. This method is
        useful to re-use a single association multiple times for different
        values. For example, say you have a schema which uses the ``id`` and
        the ``name`` field of a user. You could then define the schema
        like so::

            @schema()
            def example(self):
                user = association(UserFactory(), "basic")

                return {
                    "remote_id": user.attribute("id"),
                    "remote_name": user.attribute("name")
                }

        The benefit of the above, instead of using two separate
        ``associations``, is that the association in this case will resolve
        to the exact same model, whereas two ``associations`` will always
        resolve to two different models.
        """
        return _AssociationFieldAttribute(self, attr)

    def callback(self, callback):
        """
        :Parameters:
          - `callback`: Callback to be called, with the association
            as a parameter.

        This will return a new :py:class:`Field` instance which when
        resolved will call the given callback, passing the association
        as a parameter. To read an attribute from the association, use
        the dictionary syntax of ``association[key]``. This will do the
        right thing depending on whether you're resolving attributes
        or a model build.

        As an example, let's say you want to create a schema which
        depends on the concatenated first and last name of a user.
        Here is an example::

            @schema()
            def example(self):
                def get_name(association):
                    return "%s %s" % \\
                        (association["first_name"], association["last_name"])

                user = association(UserFactory(), "basic")

                return {
                    "name": user.callback(get_name)
                }
        """
        return _AssociationFieldCallback(self, callback)

class _AssociationFieldAttribute(Field):
    """
    Internal class used to grab an attribute from another
    :py:class:`AssociationField`.
    """

    def __init__(self, association, attr):
        self.association = association
        self.attr = attr

    def resolve(self, scope):
        return self.association._read_attribute(scope, self.attr)

class _AssociationFieldCallback(Field):
    """
    Internal class used to call a callback to determine the resolution
    value.
    """

    def __init__(self, association, callback):
        self.association = association
        self.callback = callback

    def resolve(self, scope):
        self._scope = scope
        self.association._load_schema(scope)
        return self.callback(self)

    def __getitem__(self, key):
        # We pass "None" as the scope since by the time this is called,
        # it will be from the callback, which is after we load the schema,
        # so we can be sure it is loaded.
        return self.association._read_attribute(self._scope, key)

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
