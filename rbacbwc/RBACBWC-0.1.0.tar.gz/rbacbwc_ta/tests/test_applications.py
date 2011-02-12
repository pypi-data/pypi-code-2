from nose.tools import eq_
from sqlalchemybwc import db

from rbacbwc_ta.model.entities import Application, Permission

class TestBasics(object):

    def setUp(self):
        Permission.delete_all()
        Application.delete_all()

    def test_add(self):
        a = Application.add(name=u'foo')
        assert a.id > 0
        assert a.createdts

    def test_permissions_property(self):
        a = Application(name=u'foo')
        p1 = Permission(name=u'p1')
        p2 = Permission(name=u'p2')
        a.permissions.extend((p1, p2))
        db.sess.add(a)
        db.sess.commit()
        db.sess.remove()
        a = Application.first()
        eq_(len(a.permissions), 2)
