from rbacbwc_ta.model.entities import Permission, Application, User, Group, Bundle

from rbacbwc_ta.tests.helpers import PermissionBase

class TestBasics(PermissionBase):
    perm_entity = Permission
    app_entity = Application
    UserEnt = User
    GroupEnt = Group
    BundleEnt = Bundle
