import datetime

from sqlalchemy import Column, ForeignKey, Table, PrimaryKeyConstraint, ForeignKeyConstraint, join, and_
from sqlalchemy.types import *
from sqlalchemy.orm import relation, mapper
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base()

#
# Model declaration. This would usually be in your Pylons/TG2 app
#
class Person(Model):
    __tablename__ = "person"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', Unicode, nullable=False, unique=True)
    type = Column('type', String(50), nullable=False)
    age = Column('age', Integer)
    notes = Column('notes', Unicode)
    version = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity': 'Person',
        'version_id_col': version,
        }

    def __unicode__(self):
        return self.name


class Actor(Person):
    __tablename__ = "actor"

    id = Column('id', Integer, ForeignKey('person.id'), primary_key=True)
    oscars_won = Column('oscars_won', Integer, default=0)
    __mapper_args__ = {
        'polymorphic_identity': 'Actor',
        }


class Director(Person):
    __tablename__ = "director"

    id = Column('id', Integer, ForeignKey('person.id'), primary_key=True)
    chairs_broken = Column('chairs_broken', Integer, default=0)
    __mapper_args__ = {
        'polymorphic_identity': 'Director',
        }


class Genre(Model):
    __tablename__ = "genre"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', Unicode, nullable=False)
    
    def __unicode__(self):
        return self.name

_actor_movie = Table('actor_movie', Model.metadata,
    Column('actor_id', Integer, ForeignKey('actor.id')),
    Column('movie_id', Integer, ForeignKey('movie.id')),
    PrimaryKeyConstraint('movie_id', 'actor_id'),
    )

class Movie(Model):
    __tablename__ = "movie"

    id = Column('id', Integer, primary_key=True)
    title = Column('title', Unicode, nullable=False)
    filmed_on = Column('filmed_on', Date)
    genre_id = Column('genre_id', Integer, ForeignKey('genre.id'))
    director_id = Column('director_id', Integer, ForeignKey('director.id'))
    synopsis = Column('synopsis', Unicode, info={'rum': {'field':'HTMLText'}})
    
    genre = relation('Genre', backref='movies')
    director = relation('Director', backref='movies')
    actors = relation('Actor', secondary=_actor_movie, backref='movies')
    poster= Column('poster',Binary,info={'rum':{'field':'JPEGImage'}})
    def __unicode__(self):
        ret = self.title
        if self.filmed_on:
            ret += " (%d)" % self.filmed_on.year
        return ret

class Rental(Model):
    __tablename__ = "rental"
    id = Column('id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey('person.id'),
                       nullable=False)
    movie_id = Column('movie_id', Integer, ForeignKey('movie.id'),
                      nullable=False)
    date = Column('date', DateTime)
    due_date = Column('due_date', DateTime)

    movie = relation('Movie', backref='rentals')
    person = relation('Person', backref='rentals')

    @property
    def is_overtime(self):
        return self.due_date > datetime.datetime.now()

    def __unicode__(self):
        return u"%s -> %s" % (self.movie, self.person)

    
class ActorInMovie(object):
    pass

movie_in_genre_join=join(
    Movie.__table__, Genre.__table__)

class MovieInGenre(object):
    pass

mapper(MovieInGenre, movie_in_genre_join, properties=dict(
    genre_id=[Movie.__table__.c.genre_id, Genre.__table__.c.id],
    genre_name=Genre.__table__.c.name
))
