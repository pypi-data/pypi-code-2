import unittest
from datetime import datetime
from sqlalchemy import MetaData, create_engine, Table, Column, Integer
from sqlalchemy.orm import mapper, sessionmaker

from sa_mysql_dt import DateTime

metadata = MetaData()

foo_table = Table(
    'foo', metadata,
    Column('id', Integer, primary_key=True),
    Column('dt', DateTime(), nullable=False),
    mysql_engine='InnoDB')

class Foo(object):
    def __init__(self, dt):
        self.dt = dt

mapper(Foo, foo_table)
    
class TestCase(unittest.TestCase):
    def setUp(self):
        engine = setup_clean_database()
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.session.flush()
        self.session.commit()

    def tearDown(self):
        self.session.commit()

    def test_insert(self):
        dt = datetime(2008, 1, 1, 14, 34, 17, 8888)
        a = Foo(dt)
        self.session.add(a)
        self.session.commit()
        found = self.session.query(Foo).first()
        self.assertEquals(dt, found.dt)

    def test_search(self):
        session = self.session
        dt = datetime(2008, 1, 1, 14, 34, 17, 8888)
        a = Foo(dt)
        session.add(a)
        dt = datetime(2010, 1, 1, 1, 1, 1)
        b = Foo(dt)
        session.add(b)
        session.commit()
        found = self.session.query(Foo).filter(
            Foo.dt > datetime(2009, 1, 1)).first()
        self.assertEquals(b, found)

def setup_clean_database():
    engine = create_engine('mysql:///sa_mysql_dt_tests', echo=False)
    metadata.create_all(engine)
    
    metadata.reflect(engine)
    for table in reversed(metadata.sorted_tables):
        engine.execute(table.delete())
    return engine

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
            unittest.makeSuite(TestCase),
            ])
    return suite
