"""
It's possible to directly specify a table using ``rdb.table`` as well.

Let's first grok things::

  >>> from grokcore.component.testing import grok
  >>> grok('megrok.rdb.meta')
  >>> grok(__name__)

We need to set up an engine::

  >>> from megrok.rdb.testing import configureEngine
  >>> engine = configureEngine()
  
We now need to create the tables we defined in our database::

  >>> rdb.setupDatabase(metadata)

Let's start using the database now::

  >>> session = rdb.Session()
  >>> dummy = User(name=u'dummy', password=u'secret', role=u'admin')
  >>> session.add(dummy)
  >>> silly = User(name=u'silly', password=u'secret', role=u'admin')
  >>> session.add(silly)

We can now verify that the users are there::

  >>> [(user.id, user.name, user.password, user.role) for user in
  ... session.query(User)]
  [(1, u'dummy', u'secret', u'admin'), (2, u'silly', u'secret', u'admin')]
    
"""


from megrok import rdb

from sqlalchemy import (Table, Column, MetaData, Integer, Unicode)

metadata = rdb.MetaData()


user_table = Table(
    'user_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(20), nullable=False, index=True, unique=True),
    Column('password', Unicode(100), nullable=False),
    Column('role', Unicode(20), nullable=False, index=True),
    )

class User(rdb.Model):
    rdb.metadata(metadata)
    rdb.table(user_table)
