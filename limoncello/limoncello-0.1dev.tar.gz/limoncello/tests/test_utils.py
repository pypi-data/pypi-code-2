from unittest import TestCase
from sqlalchemy import create_engine, sql
from sqlalchemy.orm import create_session
from rum import query as rumquery
#TODO: Use rumalchemy.tests.model instead and remove that module
from limoncello.tests import model
from rumalchemy.query import SAQuery, _escape_char


class TestSAQuery(TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        model.Model.metadata.create_all(bind=self.engine)

    def tearDown(self):
        model.Model.metadata.drop_all(bind=self.engine)
    
    def test_foo(self):
        pass
    # def makeSession(self):
    #        return create_session(bind=self.engine, autoflush=True,
    #                              autocommit=True)
    # 
    #     def test_filtering(self):
    #         test_data = [
    #             model.Person(name=u'Albaricoque'),
    #             model.Person(name=u'Peter'),
    #             model.Person(name=u'Lucy'),
    #             model.Person(name=u'Alba'),
    #             ]
    #         session = self.makeSession()
    #         map(session.add, test_data)
    #         session.flush()
    #         session.expunge_all()
    # 
    #         q = session.query(model.Person)
    #         query = SAQuery(rumquery.startswith('name', 'A'), resource=model.Person)
    #         items = list(query.filter(q))
    #         self.failUnlessEqual(len(items), 2)
    #         self.failUnlessEqual(query.count, 2)
    # 
    #     def test_sorting(self):
    #         test_data = [
    #             model.Person(name=u'Albaricoque', age=23),
    #             model.Person(name=u'Peter', age=32),
    #             model.Person(name=u'Lucy', age=19),
    #             model.Person(name=u'Albino', age=23),
    #             ]
    #         session = self.makeSession()
    #         map(session.add, test_data)
    #         session.flush()
    #         session.expunge_all()
    # 
    #         q = session.query(model.Person)
    #         query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
    #                         resource=model.Person)
    #         names = [p.name for p in query.filter(q)]
    #         expected = ["Lucy", "Albaricoque", "Albino", "Peter"]
    #         self.failUnlessEqual(names, expected)
    # 
    #     def test_pagination(self):
    #         test_data = [
    #             model.Person(name=u'Albaricoque', age=23),
    #             model.Person(name=u'Peter', age=32),
    #             model.Person(name=u'Lucy', age=19),
    #             model.Person(name=u'Albino', age=23),
    #             ]
    #         session = self.makeSession()
    #         map(session.add, test_data)
    #         session.flush()
    #         session.expunge_all()
    # 
    #         q = session.query(model.Person)
    #         query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
    #                         limit=2,
    #                         offset=0,
    #                         resource=model.Person)
    #         names = [p.name for p in query.filter(q)]
    #         expected = ["Lucy", "Albaricoque"]
    #         self.failUnlessEqual(names, expected)
    # 
    #         q = session.query(model.Person)
    #         query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
    #                         limit=2,
    #                         offset=2,
    #                         resource=model.Person)
    #         names = [p.name for p in query.filter(q)]
    #         expected = ["Albino", "Peter"]
    #         self.failUnlessEqual(names, expected)
    