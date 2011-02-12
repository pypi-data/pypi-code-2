from blazeutils.strings import randchars
from savalidation import validators as val
import sqlalchemy as sa

from compstack.rbac.lib import create_permission_mixin, create_user_mixin, \
    create_group_mixin, create_bundle_mixin
from compstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin
from compstack.sqlalchemy.lib.validators import validates_unique

Base = declarative_base()
PermissionMixin = create_permission_mixin('Application', 'applications.id', 'application_id')
UserMixin = create_user_mixin()
GroupMixin = create_group_mixin()
BundleMixin = create_bundle_mixin()

class Application(Base, DefaultMixin):
    __tablename__ = 'applications'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class Permission(Base, PermissionMixin):
    __tablename__ = 'permissions'

    @classmethod
    def testing_create(cls, aid=None):
        aid = aid or Application.testing_create().id
        return cls.add(name=randchars(), application_id=aid)

class User(Base, UserMixin):
    __tablename__ = 'users'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class Group(Base, GroupMixin):
    __tablename__ = 'groups'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class Bundle(Base, BundleMixin):
    __tablename__ = 'bundles'

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

# now try with a prefix
AuthPermissionMixin = create_permission_mixin('AuthApplication', 'auth_applications.id', 'application_id', tbl_prefix='auth_')
AuthUserMixin = create_user_mixin(tbl_prefix='auth_')
AuthGroupMixin = create_group_mixin(tbl_prefix='auth_')
AuthBundleMixin = create_bundle_mixin(tbl_prefix='auth_')

class AuthApplication(Base, DefaultMixin):
    __tablename__ = 'auth_applications'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class AuthPermission(Base, AuthPermissionMixin):
    __tablename__ = 'auth_permissions'

    @classmethod
    def testing_create(cls, aid=None):
        aid = aid or AuthApplication.testing_create().id
        print aid
        return cls.add(name=randchars(), application_id=aid)

class AuthUser(Base, AuthUserMixin):
    __tablename__ = 'auth_users'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class AuthGroup(Base, AuthGroupMixin):
    __tablename__ = 'auth_groups'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())

class AuthBundle(Base, AuthBundleMixin):
    __tablename__ = 'auth_bundles'

    @classmethod
    def testing_create(cls):
        return cls.add(name=randchars())
