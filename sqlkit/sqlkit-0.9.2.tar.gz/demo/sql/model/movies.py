from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import relation, backref

from sqlkit.db.utils import Descr
from sqlkit.db import proxy
import os

Base = declarative_base()
engine = "sqlite:///%s/db.sqlite" % os.path.abspath(os.path.dirname(__file__))
db = proxy.DbProxy(engine=engine, metadata=Base.metadata)


movie_casting = Table('movie_casting' , Base.metadata,
                      Column('movie_id', Integer, ForeignKey('movie.id')),
                      Column('actor_id', Integer, ForeignKey('actor.id')),
                      )

movie_genre = Table('movie_genre' , Base.metadata,
                      Column('movie_id', Integer, ForeignKey('movie.id')),
                      Column('genre_name', Integer, ForeignKey('genre.name')),
                      )

class Director(Base):
    __tablename__ = 'director'
    id             = Column(Integer, primary_key=True)
    last_name   = Column(String(60), nullable=False)
    first_name  = Column(String(60), nullable=False)
    nation      = Column(String(6))
    
    movies      = relation('Movie', backref='director', cascade='all, delete-orphan',)
    def __str__(self):
        return u'%s (%s)' % (self.last_name, self.nation)

    def __repr__(self):
        return u'<Director: %s (%s)>' % (self.last_name, self.nation)

class Movie(Base):
    __tablename__  = 'movie'
    id             = Column(Integer, primary_key=True)
    title          = Column(String(60), nullable=False)
    description    = Column(String(512))
    year           = Column(Integer())
    date_release   = Column(Date())
    director_id    = Column(Integer, ForeignKey('director.id'), nullable=False, info={'attach_instance': 'director'})

    ## relations
    # alternative way to set the relation between movies and actors
    # director       = relation('Director', backref=backref('movies', cascade='all, delete-orphan',))
    actors         = relation('Actor', backref='movies', secondary=movie_casting)
    genres         = relation('Genre', backref='movies', secondary=movie_genre)


    def __str__(self):
        return u'%s' % self.title

    def __repr__(self):
        return u'<Movie: %s>' % self.title


class Genre(Base):
    __tablename__ = 'genre'
    name     = Column(Unicode(55, assert_unicode=False), primary_key=True)
    
    def __repr__(self):
        return u'<Genre "%s">' % self.name

class Actor(Base):
    __tablename__ = 'actor'
    id             = Column(Integer, primary_key=True)
    first_name     = Column(String(60), nullable=False)
    last_name      = Column(String(60))
    nation_cod     = Column(ForeignKey('nation.cod'))

    nation         = relation('Nation', backref='actors')
    def __repr__(self):
        return u'<Actor %s %s>' % (self.first_name, self.last_name)

class Nation(Base):
    __tablename__ = 'nation'
    cod        = Column(String(4), primary_key=True)
    nation     = Column(String(20))
    

class AllTypes(Base):
    __tablename__ = 'all_types'
    id             = Column(Integer(), primary_key=True)
    varchar10      = Column(String(10), nullable=False)
    varchar200     = Column(String(200))
    text           = Column(Text())
    uni            = Column(Unicode(10, assert_unicode=False))
    uni_text       = Column(UnicodeText(assert_unicode=False), nullable=False)
    date           = Column(Date())
    datetime       = Column(DateTime(timezone=False))
    datetime_tz    = Column(DateTime(timezone=True))
    interval       = Column(Interval())
    time           = Column(Time(timezone=False))
    time_tz        = Column(Time(timezone=True))
    integer        = Column(Integer())
    float          = Column(Float())
    numeric        = Column(Numeric(8,2))
    bool           = Column(Boolean, nullable=False)
    bool_null      = Column(Boolean, nullable=True)
#    pickle         = Column(PickleType())
    
    
