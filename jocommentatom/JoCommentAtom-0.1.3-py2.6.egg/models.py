"""Models for JoCommentAtom."""
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import ForeignKeyConstraint

from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper

from rfc3339 import rfc3339

DBSession = scoped_session(sessionmaker(autocommit=True))
metadata = MetaData()

class Comment(object):
    @property
    def rfc3339date(self):
        """Return date in format defined by RFC3339."""
        return rfc3339(self.date)

class Content(object):
    pass

def initialize_db(db_string, db_echo=False):
    engine = create_engine(db_string, echo=db_echo, convert_unicode=True)
    DBSession.configure(bind=engine)
    metadata.bind = engine

    jos_comment = Table('jos_comment', metadata,
        ForeignKeyConstraint(['contentid'], ['jos_content.id']),
        autoload=True)
    jos_content = Table('jos_content', metadata, autoload=True)

    mapper(Comment, jos_comment)
    comments = relationship(Comment, backref='content')
    mapper(Content, jos_content, properties={'comments': comments})
