"""Tests for SQLAlchemy support"""

import cherrypy, os, threading, turbogears

from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String
try:
    from sqlalchemy.ext.activemapper import ActiveMapper, column, one_to_many
except ImportError: # SQLAlchemy >= 0.5
    ActiveMapper = None
    from sqlalchemy.orm import relation

from turbogears import config, redirect, expose, errorhandling
from turbogears.database import get_engine, metadata, session, mapper
from turbogears.controllers import RootController
from turbogears.testutil import create_request, sqlalchemy_cleanup, \
    capture_log, print_log


# Fixture

class User(object):
    def __repr__(self):
        return "(User %s, password %s)" % (self.user_name, self.password)


def setup_module():
    global fresh_metadata, users_table, test_table, Person, Address, Test

    config.update({
        "sqlalchemy.dburi" : "sqlite:///:memory:"})

    if os.path.exists('freshtest.db'):
        os.unlink('freshtest.db')

    get_engine()
    fresh_metadata = MetaData()
    # :memory: can't be used in multiple threads
    fresh_metadata.bind = 'sqlite:///freshtest.db'
    metadata.bind.echo = True
    fresh_metadata.bind.echo = True

    users_table = Table("users", metadata,
        Column("user_id", Integer, primary_key=True),
        Column("user_name", String(40)),
        Column("password", String(10)))

    mapper(User, users_table)

    if ActiveMapper:

        class Person(ActiveMapper):
            class mapping:
                id = column(Integer, primary_key=True)
                name = column(String(40))
                addresses = one_to_many("Address")

        class Address(ActiveMapper):
            class mapping:
                id = column(Integer, primary_key=True)
                address = column(String(40))
                city = column(String(40))
                person_id = column(Integer,
                    foreign_key=ForeignKey("person.id"))

    else:

        persons_table = Table("persons", metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String(40)))
        addresses_table = Table("addresses", metadata,
                Column("id", Integer, primary_key=True),
                Column("address", String(40)),
                Column("city", String(40)),
                Column("person_id", Integer,
                    ForeignKey(persons_table.c.id)))

        class Person(object):
            pass

        class Address(object):
            pass

        mapper(Person, persons_table)
        mapper(Address, addresses_table, properties=dict(
            person=relation(Person, backref='addresses')))

    test_table = Table("test", fresh_metadata,
        Column("id", Integer, primary_key=True),
        Column("val", String(40)))

    class Test(object):
        pass

    mapper(Test, test_table)

    metadata.create_all()
    fresh_metadata.create_all()


def teardown_module():
    metadata.drop_all()
    fresh_metadata.drop_all()
    fresh_metadata.bind.dispose()
    if os.path.exists('freshtest.db'):
        os.unlink('freshtest.db')
    sqlalchemy_cleanup()


# Simple database tests

def test_query_in_session():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    query = session.query(User)
    globbo = query.filter_by(user_name="globbo").one()
    assert globbo.password == "thegreat!"
    users_table.delete().execute()

def test_create_and_query():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    s = users_table.select()
    r = s.execute()
    assert len(r.fetchall()) == 1
    users_table.delete().execute()

def test_active_mapper():
    p = Person(name="Ford Prefect")
    a = Address(address="1 West Guildford", city="Betelgeuse")
    p.addresses.append(a)
    session.flush()
    session.clear()
    q = session.query(Person)
    ford = q.filter_by(name="Ford Prefect").one()
    assert ford is not p
    assert len(ford.addresses) == 1


# Exception handling

class MyRoot(RootController):
    """A small root controller for our exception handling tests"""

    [expose()]
    def no_error(self, name):
        """Test controller"""
        Person(name=name)
        raise redirect("/confirm")

    def e_handler(self, tg_exceptions=None):
        """Test error handler"""
        cherrypy.response.code = 501
        return "An exception occurred: %r (%s)" % ((tg_exceptions,)*2)

    [expose()]
    def create_person(self, id, docom=0, doerr=0, doflush=0):
        """Test controller"""
        Person(id=id)
        if int(docom):
            cherrypy.request.sa_transaction.commit()
        if int(doerr) == 1:
            raise Exception('User generated exception')
        if int(doerr) == 2:
            raise turbogears.redirect('/')
        if int(doflush):
            try:
                session.flush()
            except Exception:
                if int(doflush) == 1:
                    raise
        return "No exceptions occurred"
    create_person = errorhandling.exception_handler(e_handler)(create_person)


def test_implicit_trans_no_error():
    """If a controller runs sucessfully, the transaction is commited."""
    capture_log("turbogears.database")
    cherrypy.root = MyRoot()
    create_request("/no_error?name=A.%20Dent")
    print_log()
    session.clear()
    q = session.query(Person)
    arthur = q.filter_by(name="A. Dent").one()

def test_raise_sa_exception():
    """If a controller causes an SA exception, it is raised properly."""
    capture_log("turbogears.database")
    cherrypy.root = MyRoot()
    create_request("/create_person?id=20")
    output = cherrypy.response.body[0]
    assert 'No exceptions occurred' in output
    create_request("/create_person?id=20")
    output = cherrypy.response.body[0]
    # SA 0.3 uses SQLError, 0.4 DBAPIError
    assert 'SQLError' in output or 'DBAPIError' in output

def test_user_exception():
    """If a controller raises an exception, transactions are rolled back."""
    cherrypy.root = MyRoot()
    create_request("/create_person?id=21&doerr=1")
    session.clear() # should be done automatically, but just in case
    assert Person.query().get(21) is None

def test_user_redirect():
    """If a controller redirects, transactions are committed."""
    cherrypy.root = MyRoot()
    create_request("/create_person?id=22&doerr=2")
    session.clear() # should be done automatically, but just in case
    assert Person.query().get(22) is not None

def test_cntrl_commit():
    """It's safe to commit a transaction in the controller."""
    cherrypy.root = MyRoot()
    create_request("/create_person?id=23&docom=1")
    assert 'InvalidRequestError' not in cherrypy.response.body[0]

def test_cntrl_flush():
    """It's safe to flush in the controller."""
    cherrypy.root = MyRoot()
    create_request("/create_person?id=24&doflush=1")
    assert 'No exceptions occurred' in cherrypy.response.body[0]
    create_request("/create_person?id=24&doflush=0")
    assert 'IntegrityError' in cherrypy.response.body[0]
    create_request("/create_person?id=24&doflush=1")
    assert 'IntegrityError' in cherrypy.response.body[0]
    create_request("/create_person?id=24&doflush=2")
    assert 'No exceptions occurred' in cherrypy.response.body[0]


# Exception handling with rollback

class RbRoot(RootController):
    """A small root controller for our transaction rollback tests"""

    def handerr(self, id):
        """Test error handler"""
        Person(id=int(id)+1)
        return dict()

    [expose()]
    def doerr(self, id, dorb=0):
        """Test controller"""
        Person(id=id)
        if int(dorb):
            cherrypy.request.sa_transaction.rollback()
        raise Exception('test')
    doerr = errorhandling.exception_handler(handerr)(doerr)


def test_exc_rollback():
    """"An exception within a controller method causes a rollback."""
    cherrypy.root = RbRoot()
    create_request('/doerr?id=25')
    assert Person.query().get(25) is None
    assert Person.query().get(26) is not None

def test_exc_done_rollback():
    """No problems with error handler if controller manually rollbacks."""
    cherrypy.root = RbRoot()
    create_request('/doerr?id=27&dorb=1')
    assert cherrypy.response.body[0] == '{"tg_flash": null}'


# Session freshness tests

class FreshRoot(RootController):
    """A small root controller for our session freshness tests"""

    [expose()]
    def test1(self):
        assert session.query(Test).get(1).val == 'a'
        return dict()

    [expose()]
    def test2(self):
        session.query(Test).get(1).val = 'b'
        return dict()

    [expose()]
    def test3(self):
        assert session.query(Test).get(1).val == 'b'
        return dict()


def test_session_freshness():
    """Check for session freshness.

    Changes made to the data in thread B should be reflected in thread A.

    """
    fresh_metadata.bind.execute(test_table.insert(), dict(id=1, val='a'))
    cherrypy.root = FreshRoot()
    create_request("/test1")
    assert cherrypy.response.status.startswith("200")
    assert 'AssertionError' not in cherrypy.response.body[0]
    # Call test2 in a different thread
    class ThreadB(threading.Thread):
        def run(self):
            create_request("/test2")
            assert cherrypy.response.status.startswith("200")
            assert 'AssertionError' not in cherrypy.response.body[0]
    thrdb = ThreadB()
    thrdb.start()
    thrdb.join()
    create_request("/test3")
    assert cherrypy.response.status.startswith("200")
    assert 'AssertionError' not in cherrypy.response.body[0]
