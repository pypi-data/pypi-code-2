from sqlalchemybwc import db

from rbacbwc_ta.model.entities import Bundle, Group, Permission, User
from rbacbwc_ta.model.schema import tbl_bpa, tbl_bua, tbl_bga
from rbacbwc_ta.tests.helpers import PermissionAssignmentBase, HasPermsBase, \
    Many2ManyBase

class TestBundle(HasPermsBase):
    perms_table = tbl_bpa
    myentity = Bundle
    assigned_entity1 = User
    assigned_entity1_type = 'users'
    assigned_entity2 = Group
    assigned_entity2_type = 'groups'

    def test_dynamic_method_names(self):
        assert hasattr(Bundle, 'replace_users')
        assert hasattr(Bundle, 'count_users')
        assert hasattr(Bundle, 'assigned_users')
        assert hasattr(Bundle, 'replace_groups')
        assert hasattr(Bundle, 'count_groups')
        assert hasattr(Bundle, 'assigned_groups')
        assert hasattr(Bundle, 'replace_permissions')

class TestBundlePermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_bpa
    entity1 = Bundle
    entity1_field = 'bundle_id'
    entity2 = Permission
    entity2_field = 'permission_id'

class TestBundleUserAssignmentTable(Many2ManyBase):
    target_tbl = tbl_bua
    entity1 = User
    entity1_field = 'user_id'
    entity2 = Bundle
    entity2_field = 'bundle_id'

class TestBundleGroupAssignmentTable(Many2ManyBase):
    target_tbl = tbl_bga
    entity1 = Bundle
    entity1_field = 'bundle_id'
    entity2 = Group
    entity2_field = 'group_id'
