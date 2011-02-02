import os
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from rumalchemy.tests import model
from rumalchemy import SARepositoryFactory
from rum import transaction, query

engine = create_engine(os.environ.get('DBURL','sqlite:///:memory:'))
class BaseRepositoryTest(TestCase):
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=True))

    factory = SARepositoryFactory( [model], session_factory=Session)

    def makeOne(self, for_obj=model.User):
        return self.factory(for_obj)


    def setUp(self):
        model.metadata.create_all(bind=engine)
        self.Session.configure(bind=engine)
        transaction.begin()

    def tearDown(self):
        if self.factory:
            self.factory.cleanup()
        model.metadata.drop_all(bind=engine)

    def clear_memory(self):
        """
        Clears all in-memory objects so we
        can check that objects have actually been clear_memoryed.
        """
        self.Session.expunge_all()


class TestRepositoryBasic(BaseRepositoryTest):

    def test_create_save_select(self):
        repo = self.makeOne()
        obj = repo.create({'name':u'Alberto'})
        repo.save(obj)
        self.clear_memory()
        self.failUnless(filter(lambda o: o.name == u'Alberto', repo.select()))

    def test_create_save_select_with_query(self):
        repo = self.makeOne()
        obj = repo.create({'name':u'Alberto'})
        repo.save(obj)
        obj = repo.create({'name':u'Michael'})
        repo.save(obj)
        self.clear_memory()
        self.failUnlessEqual(len(list(repo.select())), 2)
        q = repo.make_query(expr=query.eq('name', u'Michael'))
        self.failUnlessEqual(len(list(repo.select(q))), 1)
        q = repo.make_query(expr=query.eq('name', u'Alberto'))
        self.failUnlessEqual(len(list(repo.select(q))), 1)
    
    def test_create_save_get(self):
        repo = self.makeOne()
        obj = repo.create({'name':u'Alberto'})
        repo.save(obj)
        obj_id = repo.get_id(obj)
        self.clear_memory()
        self.failUnless(repo.get(obj_id))
        self.failUnless(repo.get(obj_id).name == u'Alberto')

    def test_create_delete(self):
        repo = self.makeOne()
        obj = repo.create({'name':u'Alberto'})
        repo.save(obj)
        obj_id = repo.get_id(obj)
        self.clear_memory()
        obj = repo.get(obj_id)
        repo.delete(obj)
        self.clear_memory()
        self.failUnless(not list(repo.select()))

    def test_create_update(self):
        repo = self.makeOne()
        obj = repo.create({'name':u'Alberto'})
        repo.save(obj)
        obj_id = repo.get_id(obj)

        self.clear_memory()
        obj = repo.get(obj_id)
        self.failUnlessEqual(obj.name, 'Alberto')
        repo.update(obj, {'name': u'Peter'})

        self.clear_memory()
        obj = repo.get(obj_id)
        self.failUnlessEqual(obj.name, 'Peter')

        
class TestRepositoryReflect(TestRepositoryBasic):
    def setUp(self):
        self.factory = SARepositoryFactory(
            engine=engine,
            reflect='all'
            )
        self.Session = self.factory.session_factory
        # create the model tables so SqlSoup can introspect them
        model.metadata.create_all(bind=engine)
        self.factory.load_resources()
        self.User = [r for r in self.factory.resources.keys()
                     if r.__name__=='User'][0]
        self.Session.configure(bind=engine)
        transaction.begin()

    def makeOne(self):
        return super(TestRepositoryReflect, self).makeOne(self.User)


class TestRepositoryOthers(BaseRepositoryTest):
    def test_composite_key(self):
        repo = self.makeOne(model.WithCompositeKey)
        obj = repo.create({'id1':'foo', 'id2':'bar'})
        repo.save(obj)
        obj_id = repo.get_id(obj)
        self.clear_memory()

        obj = repo.get(obj_id)
        self.failUnlessEqual(obj.id1, 'foo', obj.id1)
        self.failUnlessEqual(obj.id2, 'bar', obj.id2)

    def test_slash_in_id(self):
        "Test that PK can contain a slash but the id string won't contain it"
        # ... so it isn't treated as a path component when it reached the URL
        repo = self.makeOne(model.WithCompositeKey)
        obj = repo.create({'id1':'foo/car', 'id2':'bar'})
        repo.save(obj)
        obj_id = repo.get_id(obj)
        self.failUnless('/' not in obj_id, obj_id)
        self.clear_memory()

        obj = repo.get(obj_id)
        self.failUnlessEqual(obj.id1, 'foo/car', obj.id1)
        self.failUnlessEqual(obj.id2, 'bar', obj.id2)
