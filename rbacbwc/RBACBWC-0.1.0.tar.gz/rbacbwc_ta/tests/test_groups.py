from sqlalchemybwc import db

from rbacbwc_ta.model.entities import Group, Permission, User, Bundle
from rbacbwc_ta.model.schema import tbl_gpa, tbl_gua
from rbacbwc_ta.tests.helpers import PermissionAssignmentBase, HasPermsBase, \
    Many2ManyBase

class TestGroup(HasPermsBase):
    perms_table = tbl_gpa
    myentity = Group
    assigned_entity1 = User
    assigned_entity1_type = 'users'
    assigned_entity2 = Bundle
    assigned_entity2_type = 'bundles'

    def test_dynamic_method_names(self):
        assert hasattr(Group, 'replace_users')
        assert hasattr(Group, 'count_users')
        assert hasattr(Group, 'assigned_users')
        assert hasattr(Group, 'replace_bundles')
        assert hasattr(Group, 'count_bundles')
        assert hasattr(Group, 'assigned_bundles')
        assert hasattr(Group, 'replace_permissions')

class TestGroupPermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_gpa
    entity1 = Group
    entity1_field = 'group_id'
    entity2 = Permission
    entity2_field = 'permission_id'

class TestGroupUserAssignmentTable(Many2ManyBase):
    target_tbl = tbl_gua
    entity1 = User
    entity1_field = 'user_id'
    entity2 = Group
    entity2_field = 'group_id'
