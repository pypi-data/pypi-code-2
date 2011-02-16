from mongoengine import (Document, ListField, GenericReferenceField,
    IntField, StringField)
from bson.code import Code


def reverse_dict(d):
    """
    :param d: A dict.
    :returns: A dict with values mapped to the keys.

    >>> reverse_dict({'a': 1, 'b': 2}) == {1: 'a', 2: 'b'}
    True
    """
    return dict([(v, k) for k, v in d.items()])


class Entity(Document):

    def __hash__(self):
        return self.id.__hash__()

    def __cmp__(self, other):
        return self.id.__cmp__(other.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class EntityCollection(Entity):
    # The entities contained in this entity.
    # Their access levels are the same as the containing object (self),
    # when the containing object is granted access.
    owner = GenericReferenceField(required=True)
    entities = ListField(GenericReferenceField(), default=[])

    ENTITY_NAMESPACE = ''
    VALID_ACCESS_MAP = {'admin': 100}

    def get_numeric_access(self, entity):
        """
        :param entity: An :class:`Entity`\.
        :returns: A number.
        """
        if entity in self.owner:
            return self.VALID_ACCESS_MAP['admin']
        return EntityAccess.get_access(self.ENTITY_NAMESPACE, entity, self)

    def has_admin_access(self, entity):
        """
        :param entity: An :class:`Entity`\.
        :returns: True if the given entity is an administrator of this
            collection.
        """
        if entity in self.owner:
            return True
        access = self.get_numeric_access(entity)
        return access == self.VALID_ACCESS_MAP['admin']

    def add_access(self, entity, access):
        """
        :param entity: An :class:`Entity`\.
        :param access: The access level as a string. See VALID_ACCESS_MAP.
        :returns: The access object.
        :rtype: :class:`EntityAccess`
        """
        if not self.is_valid_access(access):
            raise Exception('Unrecognized access level: %s' % access)
        level = self.get_access_value(access)
        return EntityAccess.objects.get_or_create(ns=self.ENTITY_NAMESPACE,
            entity=entity, provider=self, defaults={'access': level})

    def remove_access(self, entity):
        """
        Removes access from the given entity.
        :param entity: An :class:`Entity`\.
        """
        EntityAccess.remove_access(self.ENTITY_NAMESPACE, entity, self)

    def get_access(self, entity):
        """
        :param entity: An `Entity`\.
        :returns: The access of the Entity as a number.
        :rtype: int
        """
        return EntityAccess.get_access(self.ENTITY_NAMESPACE, entity, self)

    @classmethod
    def reverse_access_map(cls):
        """
        :returns: The mapping from the access level (number) to its name
            (string).
        """
        return reverse_dict(cls.VALID_ACCESS_MAP)

    @classmethod
    def levels(cls):
        """
        :returns: The list of access level names.
        """
        return cls.VALID_ACCESS_MAP.keys()

    @classmethod
    def get_access_name(cls, level):
        """
        :param level: A number.
        :returns: The name of the given access level.
        :raises: :exc:`KeyError` when the level is not found.
        """
        return cls.reverse_access_map()[level]

    @classmethod
    def get_access_value(cls, level_name):
        """
        :param level_name: The name of the access level.
        :returns: The numeric access level.
        :raises: :exc:`KeyError` when the level_name is not found.
        """
        return cls.VALID_ACCESS_MAP[level_name]

    @classmethod
    def is_valid_access(cls, access):
        """
        :param access: The access level name.
        :returns: True if the level name is valid.
        """
        return access in cls.VALID_ACCESS_MAP.keys()


class EntityAccess(Document):
    # The namespace in which this access is being applied.
    ns = StringField(min_length=1, max_length=50, required=True,
        unique_with=('entity', 'provider'))
    # subject
    entity = GenericReferenceField(required=True)
    # role
    provider = GenericReferenceField(required=True)
    access = IntField(min_value=1, required=True)

    # Pre-compiled map and reduce functions.
    _MAP_CODE = Code("""
        function() {
            // The inner loop.
            function inner(entity, access) {
                // Generic references are structured differently.
                entity = entity._ref;
                // Check if self is the target.
                if (entity.$id.equals(target)) {
                    emit(null, access);
                }
                // Check others.
                var obj = entity.fetch();
                for (var i in obj.entities) {
                    inner(obj.entities[i], access);
                }
            }
            inner(this.entity, this.access);
        }
    """)
    _REDUCE_CODE = Code("""
        function(key, value_array) {
            return Math.max.apply(null, value_array);
        }
    """)

    @classmethod
    def get_access(cls, ns, entity, provider):
        """
        :param string ns: The namespace of the access domain.
        :param Entity entity: The entity.
        :param mongoengine.Document provider: The provider of the access.
        :returns: The access level of the given entity to the given provider.
        :rtype: int
        """
        accesses = cls.objects(ns=ns, provider=provider).map_reduce(
            cls._MAP_CODE, cls._REDUCE_CODE, scope={'target': entity.id})
        # unpack the values
        accesses = [x.value for x in accesses]
        if not accesses:
            return 0
        return int(max(accesses))

    # TODO TEST ME
    @classmethod
    def get_providers(cls, ns, entity):
        """
        :param string ns: The namespace of the access domain.
        :param Entity entity: An entity.
        :returns: A generator returning all providers for the given entity
            in the namespace.
        """
        for a in cls.objects(ns=ns, entity=entity):
            yield a.provider

    # TODO TEST ME
    @classmethod
    def remove_access(cls, ns, entity, provider):
        """
        Removes the access for the given entity to the provider in the
        access namespace.
        :param string ns: The namespace of the access domain.
        :param Entity entity: An entity.
        :param mongoengine.Document provider: The provider of the access.
        """
        cls.objects(ns=ns, entity=entity, provider=provider).delete(safe=True)

    @classmethod
    def create(cls, ns, entity, provider, access):
        """
        :param string ns: The namespace of the access domain.
        :param Entity entity: An entity.
        :param mongoengine.Document provider: The provider of the access.
        :returns: An access object.
        :rtype: :class:`EntityAccess`
        """
        return cls(ns=ns, entity=entity, provider=provider, access=access)
