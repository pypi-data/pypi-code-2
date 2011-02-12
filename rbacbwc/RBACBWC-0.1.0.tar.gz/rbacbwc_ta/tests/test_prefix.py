from nose.tools import eq_
from sqlalchemybwc import db

from rbacbwc_ta.model.entities import AuthApplication, AuthPermission, \
    AuthBundle, AuthUser, AuthGroup
from rbacbwc_ta.model.schema import tbl_auth_bpa, tbl_auth_bua, tbl_auth_bga,\
    tbl_auth_gua, tbl_auth_gpa, tbl_auth_upa
from rbacbwc_ta.tests.helpers import PermissionAssignmentBase, HasPermsBase, \
    Many2ManyBase, PermissionBase

class TestAuthApplication(object):

    def setUp(self):
        AuthApplication.delete_all()
        AuthPermission.delete_all()

    def test_add(self):
        a = AuthApplication.add(name=u'foo')
        assert a.id > 0
        assert a.createdts

    def test_permissions_property(self):
        a = AuthApplication(name=u'foo')
        p1 = AuthPermission(name=u'p1')
        p2 = AuthPermission(name=u'p2')
        a.permissions.extend((p1, p2))
        db.sess.add(a)
        db.sess.commit()
        db.sess.remove()
        a = AuthApplication.first()
        eq_(len(a.permissions), 2)

class TestBundle(HasPermsBase):
    perms_entity = AuthPermission
    myentity = AuthBundle
    assigned_entity1 = AuthUser
    assigned_entity1_type = 'users'
    assigned_entity2 = AuthGroup
    assigned_entity2_type = 'groups'

    def test_dynamic_method_names(self):
        assert hasattr(AuthBundle, 'replace_users')
        assert hasattr(AuthBundle, 'count_users')
        assert hasattr(AuthBundle, 'assigned_users')
        assert hasattr(AuthBundle, 'replace_groups')
        assert hasattr(AuthBundle, 'count_groups')
        assert hasattr(AuthBundle, 'assigned_groups')
        assert hasattr(AuthBundle, 'replace_permissions')

class TestBundlePermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_auth_bpa
    entity1 = AuthBundle
    entity1_field = 'bundle_id'
    entity2 = AuthPermission
    entity2_field = 'permission_id'

class TestBundleUserAssignmentTable(Many2ManyBase):
    target_tbl = tbl_auth_bua
    entity1 = AuthUser
    entity1_field = 'user_id'
    entity2 = AuthBundle
    entity2_field = 'bundle_id'

class TestBundleGroupAssignmentTable(Many2ManyBase):
    target_tbl = tbl_auth_bga
    entity1 = AuthBundle
    entity1_field = 'bundle_id'
    entity2 = AuthGroup
    entity2_field = 'group_id'

class TestGroup(HasPermsBase):
    perms_entity = AuthPermission
    myentity = AuthGroup
    assigned_entity1 = AuthUser
    assigned_entity1_type = 'users'
    assigned_entity2 = AuthBundle
    assigned_entity2_type = 'bundles'

    def test_dynamic_method_names(self):
        assert hasattr(AuthGroup, 'replace_users')
        assert hasattr(AuthGroup, 'count_users')
        assert hasattr(AuthGroup, 'assigned_users')
        assert hasattr(AuthGroup, 'replace_bundles')
        assert hasattr(AuthGroup, 'count_bundles')
        assert hasattr(AuthGroup, 'assigned_bundles')
        assert hasattr(AuthGroup, 'replace_permissions')

class TestGroupPermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_auth_gpa
    entity1 = AuthGroup
    entity1_field = 'group_id'
    entity2 = AuthPermission
    entity2_field = 'permission_id'

class TestGroupUserAssignmentTable(Many2ManyBase):
    target_tbl = tbl_auth_gua
    entity1 = AuthUser
    entity1_field = 'user_id'
    entity2 = AuthGroup
    entity2_field = 'group_id'

class TestPermissions(PermissionBase):
    perm_entity = AuthPermission
    app_entity = AuthApplication
    UserEnt = AuthUser
    GroupEnt = AuthGroup
    BundleEnt = AuthBundle

class TestUser(HasPermsBase):
    perms_entity = AuthPermission
    myentity = AuthUser
    assigned_entity1 = AuthGroup
    assigned_entity1_type = 'groups'
    assigned_entity2 = AuthBundle
    assigned_entity2_type = 'bundles'

    def test_has_permissions(self):
        u = AuthUser.testing_create()
        p = AuthPermission.testing_create()
        p2 = AuthPermission.testing_create(aid=p.application_id)
        AuthUser.replace_permissions(u.id, [p2.id], [])
        result = AuthUser.has_permissions(u.id, p.application_id, (p.name, p2.name))
        eq_(result, {p.name: False, p2.name: True})

class TestUserPermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_auth_upa
    entity1 = AuthUser
    entity1_field = 'user_id'
    entity2 = AuthPermission
    entity2_field = 'permission_id'
