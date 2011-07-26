from sqlalchemy import *
from sqlalchemy.types import *
from sqlalchemy.orm import relation, backref, class_mapper, object_session,\
                            synonym
from sqlalchemy.orm import mapper
from sqlalchemy.exceptions import InvalidRequestError, SQLError

metadata = MetaData()

# tables
country_t = Table("country", metadata,
    # Here we test non autoincrement keys
    Column("code", String(2), primary_key=True),
    Column("name", String),
    )

group_t = Table("group", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    )

user_t = Table("user", metadata,
    Column("id", Integer, Sequence('user_id_seq'), primary_key=True),
    Column("type", String(20)),
    Column("name", Unicode(15), nullable=False),
    Column("born_on", DateTime),
    )

group_user_t = Table("group_user_xref", metadata,
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("group_id", Integer, ForeignKey("group.id"), nullable=False),
    PrimaryKeyConstraint("user_id", "group_id")
    )

address_t = Table("address", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("street", Unicode),
    Column("country_code", String(2), ForeignKey('country.code'), nullable=False),
    Column("post_code", Unicode),
    )

power_user_t = Table("power_user", metadata,
    Column("id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("description", Unicode, info={'rum': {'field':'HTMLText'}})
    )

with_composite_key = Table("with_composite_key", metadata,
    Column("id1", String(10), nullable=False),
    Column("id2", String(10), nullable=False),
    PrimaryKeyConstraint("id1", "id2")
    )
    
# classes and mappers

class Country(object):
    def _get_code(self):
        return self._code
    def _set_code(self, value):
        if value:
            value = value.upper()
        self._code = value
    code = property(_get_code, _set_code)

mapper(Country, country_t, properties={
    'code': synonym('_code', map_column=True),
    }
)

class CountryModified(object):
    pass

mapper(CountryModified, country_t, {'label': country_t.c.name})

class Group(object):
    pass

mapper(Group, group_t)


class User(object):
    def __unicode__(self):
        return self.name or 'No name(%d)'%self.id

mapper(User, user_t, properties = {
    'groups': relation(Group, secondary=group_user_t, backref="users"),
    },
    polymorphic_on = user_t.c.type,
    polymorphic_identity = 'User',
    )
    
class PowerUser(User):
    pass

mapper(PowerUser, power_user_t, inherits=User, polymorphic_identity='PowerUser')


class Address(object):
    pass

mapper(Address, address_t, properties = {
    'user': relation(User, backref="addresses"),
    'country': relation(Country, backref="addresses"),
    })

class WithCompositeKey(object):
    pass

mapper(WithCompositeKey, with_composite_key)
