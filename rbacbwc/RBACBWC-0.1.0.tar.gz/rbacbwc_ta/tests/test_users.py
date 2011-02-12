import itertools

from blazeutils.datastructures import OrderedDict
from nose.tools import eq_
from sqlalchemybwc import db

from rbacbwc_ta.model.entities import User, Permission, Group, Bundle, Application
from rbacbwc_ta.model.schema import tbl_upa
from rbacbwc_ta.tests.helpers import PermissionAssignmentBase, HasPermsBase, \
    delete_all

class TestUser(HasPermsBase):
    perms_table = tbl_upa
    myentity = User
    assigned_entity1 = Group
    assigned_entity1_type = 'groups'
    assigned_entity2 = Bundle
    assigned_entity2_type = 'bundles'

    def test_dynamic_method_names(self):
        assert hasattr(User, 'replace_groups')
        assert hasattr(User, 'count_groups')
        assert hasattr(User, 'assigned_groups')
        assert hasattr(User, 'replace_bundles')
        assert hasattr(User, 'count_bundles')
        assert hasattr(User, 'assigned_bundles')
        assert hasattr(User, 'replace_permissions')

class TestHasPermission(object):
    approval_hierarchy = OrderedDict()
    # the order here matters, the key that comes first is considered higher
    # precedence when determining what the result of a permutation should be.
    # So, for example, if the permutation is ('ud', 'uba'), 'ud' has precedence
    # and the resulting approval should be False.  If the permutation is ('uba',
    # 'gd') then 'uba' has precedence and the resulting approval should be True.
    approval_hierarchy['ud'] = False
    approval_hierarchy['ubd'] = False
    approval_hierarchy['ua'] = True
    approval_hierarchy['uba'] = True
    approval_hierarchy['gd'] = False
    approval_hierarchy['gbd'] = False
    approval_hierarchy['ga'] = True
    approval_hierarchy['gba'] = True

    def setUp(self):
        delete_all()

    def test_non_existant_permission(self):
        u = User.testing_create()
        a = Application.testing_create()
        result = User.has_permissions(u.id, a.id, [u'foobar'])
        eq_(result, {u'foobar':None})

    def test_not_assigned_permission(self):
        u = User.testing_create()
        p = Permission.testing_create()
        result = User.has_permissions(u.id, p.application_id, [p.name])
        eq_(result, {p.name: False})

    def check_permutation(self, permutation):

        # calculate what the most significant permutation is going to be
        ah_keys = self.approval_hierarchy.keys()
        def permutation_position(p):
            return ah_keys.index(p)
        most_significant_perm = min(permutation, key=permutation_position)
        approved = self.approval_hierarchy[most_significant_perm]

        # create the objects that will be used
        u = User.testing_create()
        p = Permission.testing_create()
        p2 = Permission.testing_create()
        perms = [p.id, p2.id]

        if 'ud' in permutation:
            User.replace_permissions(u.id, [], perms)

        if 'ua' in permutation:
            User.replace_permissions(u.id, perms, [])

        user_bundles = []
        if 'ubd' in permutation:
            b = Bundle.testing_create()
            user_bundles.append(b.id)
            Bundle.replace_permissions(b.id, [], perms)

        if 'uba' in permutation:
            b = Bundle.testing_create()
            user_bundles.append(b.id)
            Bundle.replace_permissions(b.id, perms, [])

        if user_bundles:
            User.replace_bundles(u.id, user_bundles)

        user_groups = []
        if 'gd' in permutation:
            g = Group.testing_create()
            user_groups.append(g.id)
            Group.replace_permissions(g.id, [], perms)

        if 'ga' in permutation:
            g = Group.testing_create()
            user_groups.append(g.id)
            Group.replace_permissions(g.id, perms, [])

        # with group bundles there are two "paths" we need to test.  The first
        # is the case that a single group has one or more bundles.  The second
        # is the case of multiple groups each having a bundle.
        gp2_flag = False
        if 'gba' in permutation or 'gbd' in permutation:
            gp2_flag = True
            p1g = Group.testing_create()
            p1g_bundles = []

            if 'gba' in permutation:
                # path 1
                b = Bundle.testing_create()
                Bundle.replace_permissions(b.id, [p2.id], [])
                p1g_bundles.append(b.id)

                # path 2
                g = Group.testing_create()
                b = Bundle.testing_create()
                Group.replace_bundles(g.id, [b.id])
                Bundle.replace_permissions(b.id, [p.id], [])
                user_groups.append(g.id)

            if 'gbd' in permutation:
                # path 1
                b = Bundle.testing_create()
                Bundle.replace_permissions(b.id, [], [p2.id])
                p1g_bundles.append(b.id)

                # path 2
                g = Group.testing_create()
                b = Bundle.testing_create()
                Group.replace_bundles(g.id, [b.id])
                Bundle.replace_permissions(b.id, [], [p.id])
                user_groups.append(g.id)

            Group.replace_bundles(p1g.id, p1g_bundles)
            user_groups.append(p1g.id)

        if user_groups:
            User.replace_groups(u.id, user_groups)

        db.sess.commit()

        result = User.has_permissions(u.id, p.application_id, [p.name])
        eq_(result, {p.name : approved})

        if gp2_flag:
            result = User.has_permissions(u.id, p2.application_id, [p2.name])
            eq_(result, {p2.name : approved})

    def test_permutations(self):

        # think of the possiblities like an 8-digit binary number.  Each digit
        # represents one of the keys in approval_hierarchy.  If the digit is
        # 1, then the permission assignment represented by the key is considered
        # to be in effect.  So if we have a list like:
        #
        #   ['ua', 'gbd']
        #
        # That means we need to run a test for the situation where the user has
        # a permission that is user approved but group-bundle denied.  The code
        # below gives us all the possible combinations for the eight different
        # keys we have.
        L = self.approval_hierarchy.keys()
        permutations = itertools.chain.from_iterable(itertools.combinations(L, x) for x in xrange(1, len(L) + 1))
        db.engine.echo = True
        for p in permutations:
            # filter out permutations that have user approve and user deny
            # as that is not a valid possiblity.
            if not ('ua' in p and 'ud' in p):
                yield self.check_permutation, p

    def test_multiple_permissions(self):
        u = User.testing_create()
        p = Permission.testing_create()
        p2 = Permission.testing_create(aid=p.application_id)
        User.replace_permissions(u.id, [p2.id], [])
        result = User.has_permissions(u.id, p.application_id, (p.name, p2.name))
        eq_(result, {p.name: False, p2.name: True})

    def test_wrong_application(self):
        u = User.testing_create()
        p = Permission.testing_create()
        p2 = Permission.testing_create()
        User.replace_permissions(u.id, [p2.id, p.id], [])
        result = User.has_permissions(u.id, p.application_id, (p.name, p2.name))
        eq_(result, {p.name: True, p2.name: None})

class TestUserPermissionTable(PermissionAssignmentBase):
    target_tbl = tbl_upa
    entity1 = User
    entity1_field = 'user_id'
    entity2 = Permission
    entity2_field = 'permission_id'
