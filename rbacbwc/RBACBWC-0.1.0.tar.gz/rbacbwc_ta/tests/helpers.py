from nose.tools import eq_
from nose.plugins.skip import SkipTest
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import sqlalchemy.sql as sasql
from sqlalchemybwc import db
from sqlalchemybwc.lib.helpers import is_fk_exc, is_null_exc, is_unique_exc

from rbacbwc_ta.model.entities import User, Group, Bundle, Permission, \
    AuthUser, AuthGroup, AuthBundle, AuthPermission

def delete_all():
    db.sess.execute(User.__table__.delete())
    db.sess.execute(Group.__table__.delete())
    db.sess.execute(Bundle.__table__.delete())
    db.sess.execute(Permission.__table__.delete())
    db.sess.execute(AuthUser.__table__.delete())
    db.sess.execute(AuthGroup.__table__.delete())
    db.sess.execute(AuthBundle.__table__.delete())
    db.sess.execute(AuthPermission.__table__.delete())
    db.sess.commit()

class HasPermsBase(object):
    perms_entity = Permission
    myentity = None
    assigned_entity1 = None
    assigned_entity1_type = None
    assigned_entity2 = None
    assigned_entity2_type = None

    def setUp(self):
        delete_all()

    def test_add(self):
        u = self.myentity.add(name=u'foo')
        assert u.id > 0
        assert u.createdts

    def test_permission_assignment_approved(self):
        u = self.myentity.testing_create()
        uid = u.id

        p1 = self.perms_entity.testing_create()

        p1id = p1.id
        self.myentity.replace_permissions(u.id, [p1.id], [])
        db.sess.commit()
        db.sess.remove()

        u = self.myentity.get(uid)
        approved, denied = self.myentity.assigned_permissions(u.id)
        eq_(len(approved), 1)
        eq_(len(denied), 0)
        assert approved[0] == p1id

    def test_permission_assignment_denied(self):
        u = self.myentity.testing_create()
        uid = u.id
        p1 = self.perms_entity.testing_create()
        p1id = p1.id
        self.myentity.replace_permissions(u.id, [], [p1.id])
        db.sess.commit()
        db.sess.remove()

        u = self.myentity.get(uid)
        approved, denied = self.myentity.assigned_permissions(u.id)
        eq_(len(approved), 0)
        eq_(len(denied), 1)
        assert denied[0] == p1id

    def check_assign_entity(self, assigned_entity, type):
        count_func = getattr(self.myentity, 'count_' + type)
        replace_func = getattr(self.myentity, 'replace_' + type)
        assigned_func = getattr(self.myentity, 'assigned_' + type)

        u1 = assigned_entity.testing_create()
        u2 = assigned_entity.testing_create()
        g1 = self.myentity.testing_create()
        g2 = self.myentity.testing_create()

        count = replace_func(g1.id, [u1.id, u2.id])
        assert count == 2
        count = replace_func(g2.id, [u1.id, u2.id])
        assert count == 2
        db.sess.commit()

        # test the count function with a parameter
        count = count_func(g1.id)
        assert count == 2, count

        # test the count function without a parameter
        count = count_func()
        assert count == 4

        # make sure replace is deleting the correct records
        u3 = assigned_entity.testing_create()
        replace_func(g1.id, [u3.id])
        eq_(count_func(g1.id), 1)

        # test the assigned function
        assigned_ids = assigned_func(g1.id)
        eq_([u3.id], assigned_ids)
        assigned_ids = assigned_func(g2.id)
        eq_([u1.id, u2.id], assigned_ids)

    def test_assign1_entity(self):
        self.check_assign_entity(self.assigned_entity1, self.assigned_entity1_type)

    def test_assign2_entity(self):
        self.check_assign_entity(self.assigned_entity2, self.assigned_entity2_type)

class Many2ManyBase(object):
    target_tbl = None
    entity1 = None
    entity1_field = None
    entity2 = None
    entity2_field = None

    def setUp(self):
        delete_all()

    @property
    def target_tbl_count(self):
        sql = sasql.select([func.count("*")], from_obj=[self.target_tbl])
        return db.engine.execute(sql).scalar()

    def insert_dict(self):
        u = self.entity1.testing_create()
        p = self.entity2.testing_create()
        return {self.entity1_field: u.id, self.entity2_field: p.id}

    def test_insert(self):
        sql = self.target_tbl.insert(self.insert_dict())
        db.engine.execute(sql)
        assert self.target_tbl_count == 1

    def test_fk_on_field2(self):
        insdict = self.insert_dict()
        insdict[self.entity2_field] = 10000
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False
        except Exception, e:
            if not is_fk_exc(e, self.entity2_field):
                raise

    def test_null_on_field2(self):
        insdict = self.insert_dict()
        insdict[self.entity2_field] = None
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False
        except Exception, e:
            # sqlite throws the FK exception with Null, postgres throws null
            if not is_null_exc(e, self.entity2_field) and not is_fk_exc(e, self.entity2_field):
                raise

    def test_fk_on_field1(self):
        insdict = self.insert_dict()
        insdict[self.entity1_field] = 10000
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False
        except Exception, e:
            if not is_fk_exc(e, self.entity1_field):
                raise

    def test_null_on_field1(self):
        insdict = self.insert_dict()
        insdict[self.entity1_field] = None
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False
        except Exception, e:
            # sqlite throws the FK exception with Null, postgres throws null error
            if not is_null_exc(e, self.entity1_field) and not is_fk_exc(e, self.entity2_field):
                raise

    def test_entity1_delete_cascade(self):
        insdict = self.insert_dict()
        sql = self.target_tbl.insert(insdict)
        res = db.engine.execute(sql)
        assert self.target_tbl_count == 1

        self.entity1.delete(insdict[self.entity1_field])
        assert self.target_tbl_count == 0

    def test_entity2_delete_cascade(self):
        insdict = self.insert_dict()
        sql = self.target_tbl.insert(insdict)
        res = db.engine.execute(sql)
        assert self.target_tbl_count == 1

        self.entity2.delete(insdict[self.entity2_field])
        assert self.target_tbl_count == 0

    def test_unique_index(self):
        insdict = self.insert_dict()
        sql = self.target_tbl.insert(insdict)
        res = db.engine.execute(sql)
        assert self.target_tbl_count == 1

        # duplicate record should not be allowed
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False, 'unique index failed'
        except IntegrityError:
            pass

        # alternate entity1 id should insert
        e1 = self.entity1.testing_create()
        insdict[self.entity1_field] = e1.id
        res = db.engine.execute(sql)
        assert self.target_tbl_count == 2

        # alternate entity2 id should insert
        e2 = self.entity2.testing_create()
        insdict[self.entity2_field] = e2.id
        res = db.engine.execute(sql)
        assert self.target_tbl_count == 3

class PermissionAssignmentBase(Many2ManyBase):

    def insert_dict(self):
        insdict = Many2ManyBase.insert_dict(self)
        insdict['approved'] = 1
        return insdict

    def test_check_constraint_on_approved(self):
        insdict = self.insert_dict()
        insdict['approved'] = 0
        sql = self.target_tbl.insert(insdict)
        try:
            db.engine.execute(sql)
            assert False
        except IntegrityError:
            pass

class PermissionBase(object):
    perm_entity = None
    app_entity = None

    def setUp(self):
        delete_all()

    def test_add(self):
        a = self.app_entity.testing_create()
        p = self.perm_entity.add(name=u'foo', application_id=a.id)
        assert p.id > 0
        assert p.createdts
        assert p.belongs_to is a

    def test_nullable_name(self):
        a = self.app_entity.testing_create()
        try:
            self.perm_entity.add(application_id=a.id)
            assert False
        except Exception, e:
            if not is_null_exc(e, 'name'):
                raise

    def test_protected_entity_fk_with_bad_id(self):
        try:
            self.perm_entity.add(name=u'foo', application_id=1000)
            assert False
        except Exception, e:
            if not is_fk_exc(e, 'application_id'):
                raise

    def test_protected_entity_fk_without_id(self):
        try:
            self.perm_entity.add(name=u'foo')
            assert False
        except Exception, e:
            # sqlite shows fk exc, postgres shows null exc
            if not is_fk_exc(e, 'application_id') and not is_null_exc(e, 'application_id'):
                raise

    def test_protected_entity_fk_delete(self):
        a = self.app_entity.testing_create()
        a.id
        p = self.perm_entity.add(name=u'foo', application_id=a.id)
        try:
            self.app_entity.delete(a.id)
            assert False
        except Exception, e:
            if 'UPDATE permissions' in str(e):
                assert False, 'self.perm_entity.application_id should not be set NULL when an application is deleted'
            if not is_fk_exc(e, 'application_id'):
                raise

    def test_unique_constraint(self):
        a1 = self.app_entity.testing_create()
        a2 = self.app_entity.testing_create()
        p1 = self.perm_entity.add(name=u'foo', application_id=a1.id)
        p2 = self.perm_entity.add(name=u'foo', application_id=a2.id)
        assert p1
        assert p2
        assert p1 is not p2

        # add duplicate ignoring a unique exception
        p3 = self.perm_entity.add_iu(name=u'foo', application_id=a2.id)
        assert p3 is None

    def test_indexes_for_queries(self):
        # not sure what it should be yet
        raise SkipTest

    def check_replace_assigned_obj(self, Ent, type):
        o = Ent.testing_create()
        o1id = o.id
        o = Ent.testing_create()
        o2id = o.id

        p1 = self.perm_entity.testing_create()
        p1id = p1.id

        replace_method = getattr(self.perm_entity, 'replace_%s' % type)
        assigned_method = getattr(self.perm_entity, 'assigned_%s' % type)

        replace_method(p1id, o1id)

        approved, denied = assigned_method(p1id)
        eq_(len(approved), 1)
        eq_(len(denied), 0)
        assert approved[0] == o1id

        replace_method(p1id, [o1id, o2id])

        approved, denied = assigned_method(p1id)
        eq_(len(approved), 2)
        eq_(len(denied), 0)
        assert approved[0] == o1id
        assert approved[1] == o2id

        replace_method(p1id)

        approved, denied = assigned_method(p1id)
        eq_(len(approved), 0)
        eq_(len(denied), 0)

        replace_method(p1id, o1id, o2id)

        approved, denied = assigned_method(p1id)
        eq_(len(approved), 1)
        eq_(len(denied), 1)
        assert approved[0] == o1id
        assert denied[0] == o2id

        replace_method(p1id, denied_ids=[o1id, o2id])

        approved, denied = assigned_method(p1id)
        eq_(len(approved), 0)
        eq_(len(denied), 2)
        assert denied[0] == o1id
        assert denied[1] == o2id

    def test_replace_assigned_users(self):
        self.check_replace_assigned_obj(self.UserEnt, 'users')

    def test_replace_assigned_groups(self):
        self.check_replace_assigned_obj(self.GroupEnt, 'groups')

    def test_replace_assigned_bundles(self):
        self.check_replace_assigned_obj(self.BundleEnt, 'bundles')
