"""
We test an initialization pattern for z3c.saconfig where the metadata
is set up in an event handler.

Let's first grok things::

  >>> grok.testing.grok('megrok.rdb.meta')
  >>> grok.testing.grok(__name__)

We start using the database now::

  >>> session = rdb.Session()

Let's start using the database now::

  >>> session = rdb.Session()
  >>> philosophy = Department(name='Philosophy')
  >>> session.add(philosophy)
  >>> logic = Course(name='Logic')
  >>> ethics = Course(name='Ethics')
  >>> metaphysics = Course(name='Metaphysics')
  >>> session.add_all([logic, ethics, metaphysics])
  
Let's now add them to the courses container::

  >>> philosophy.courses.set(logic)
  >>> philosophy.courses.set(ethics)
  >>> philosophy.courses.set(metaphysics)

We can now verify that the courses are there::

  >>> [(course.id, course.name, course.department_id) for course in
  ... session.query(Course)]
  [(1, 'Logic', 1), (2, 'Ethics', 1), (3, 'Metaphysics', 1)]

  >>> for key, value in sorted(philosophy.courses.items()):
  ...   print key, value.name, value.department.name
  1 Logic Philosophy
  2 Ethics Philosophy
  3 Metaphysics Philosophy
"""

import grokcore.component as grok
from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineCreatedEvent

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation

from megrok import rdb

TEST_DSN = 'sqlite:///:memory:'

engine_factory = EngineFactory(TEST_DSN)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)

metadata = rdb.MetaData()

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    rdb.setupDatabase(metadata)

rdb.metadata(metadata)

class Courses(rdb.Container):
    pass

class Department(rdb.Model):
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))
    courses = relation('Course', 
                       backref='department',
                       collection_class=Courses)

class Course(rdb.Model):
    id = Column('id', Integer, primary_key=True)
    department_id = Column('department_id', Integer, 
                           ForeignKey('department.id'))
    name = Column('name', String(50))

