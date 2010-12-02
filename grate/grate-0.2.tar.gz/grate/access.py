from mongoengine import (Document, ListField, GenericReferenceField,
    IntField, StringField)
from bson.code import Code


def reverse_dict(d):
    """
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

    def get_numeric_access(self, user):
        if user in self.owner:
            return self.VALID_ACCESS_MAP['admin']
        return EntityAccess.get_access(self.ENTITY_NAMESPACE, user, self)

    def has_admin_access(self, user):
        if user in self.owner:
            return True
        return self.get_numeric_access(user) == self.VALID_ACCESS_MAP['admin']

    def add_access(self, entity, access):
        if not self.is_valid_access(access):
            raise Exception('Unrecognized access level: %s' % access)
        level = self.get_access_value(access)
        return EntityAccess.objects.get_or_create(ns=self.ENTITY_NAMESPACE,
            entity=entity, provider=self, defaults={'access': level})

    def remove_access(self, entity):
        EntityAccess.remove_access(self.ENTITY_NAMESPACE, entity, self)

    def get_access(self, entity):
        return EntityAccess.get_access(self.ENTITY_NAMESPACE, entity, self)

    @classmethod
    def reverse_access_map(cls):
        return reverse_dict(cls.VALID_ACCESS_MAP)

    @classmethod
    def levels(cls):
        return cls.VALID_ACCESS_MAP.keys()

    @classmethod
    def get_access_name(cls, level):
        return cls.reverse_access_map()[level]

    @classmethod
    def get_access_value(cls, level_name):
        return cls.VALID_ACCESS_MAP[level_name]

    @classmethod
    def is_valid_access(cls, access):
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
                if (entity.$id.toString() == target) {
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
        accesses = cls.objects(provider=provider).map_reduce(cls._MAP_CODE,
            cls._REDUCE_CODE, scope={'target': str(entity.id)})
        # unpack the values
        accesses = [x.value for x in accesses]
        if not accesses:
            return 0
        return int(max(accesses))

    # TODO TEST ME
    @classmethod
    def get_providers(cls, ns, entity):
        for a in cls.objects(ns=ns, entity=entity):
            yield a.provider

    # TODO TEST ME
    @classmethod
    def remove_access(cls, ns, entity, provider):
        cls.objects(ns=ns, entity=entity, provider=provider).delete(safe=True)

    @classmethod
    def create(cls, ns, entity, provider, access):
        return cls(ns=ns, entity=entity, provider=provider, access=access)
