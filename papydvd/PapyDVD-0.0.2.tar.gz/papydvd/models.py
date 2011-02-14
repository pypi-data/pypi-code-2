# -*- coding: utf-8 -*-

import transaction
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import DateTime
from sqlalchemy import Unicode
from sqlalchemy import LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.util import buffer

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

metadata = Base.metadata

class Director(Base):
    __tablename__ = 'directors'
    director_id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    photo = Column(LargeBinary)

    def __init__(self, name, photo=None):
        self.name = name
        self.photo = photo

    @classmethod
    def all_by_name(cls):
        dbsession = DBSession()
        return dbsession.query(Director).order_by(Director.name).all()


class Genre(Base):
    __tablename__ = 'genres'
    genre_id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    description = Column(Unicode(1000))
    image = Column(LargeBinary)

    def __init__(self, name, description=u'', image=None):
        self.name = name
        self.description = description
        self.image = image

    @classmethod
    def all_by_name(cls):
        dbsession = DBSession()
        return dbsession.query(Genre).order_by(Genre.name).all()


class Movie(Base):
    __tablename__ = 'movies'
    movie_id = Column(Integer, primary_key=True)
    title = Column(Unicode(100), nullable=False)
    primary_number = Column(Integer, nullable=False)
    secondary_number = Column(Integer, nullable=False)
    year = Column(SmallInteger)
    genre_id = Column(SmallInteger, ForeignKey('genres.genre_id'), nullable=False)
    director_id = Column(Integer, ForeignKey('directors.director_id'))
    story = Column(Unicode(5000))
    cover = Column(LargeBinary)
    add_date = Column(DateTime, nullable=False)
    modification_date = Column(DateTime, nullable=False)

    genre = relationship(Genre, backref=backref('movies', order_by=modification_date.desc()))
    director = relationship(Director, backref=backref('movies', order_by=modification_date.desc()))
    
    __table_args__  = ((UniqueConstraint(primary_number, secondary_number)), {})

    def __init__(self, title, genre_id, primary_number=None, secondary_number=0,
                 director_id=None, year=None, story=u'', cover=None, add_date=None):
        if not add_date:
            add_date = datetime.now()
        if not primary_number:
            dbsession = DBSession()
            primary_number = dbsession.query(Movie).count()+1
        self.title = title
        self.primary_number = primary_number
        self.secondary_number = secondary_number
        self.genre_id = genre_id
        self.director_id = director_id
        self.year = year
        self.story = story
        self.cover = cover
        self.add_date = add_date
        self.modification_date = add_date # Yes, the same date

    @classmethod
    def all(cls):
        dbsession = DBSession()
        return dbsession.query(Movie).order_by(Movie.modification_date.desc()).all()

    @classmethod
    def getMovieById(self, id):
            dbsession = DBSession()
            return dbsession.query(Movie).filter(Movie.movie_id==id).one()

class AppInfo(Base):
    """General application registry"""
    __tablename__ = 'app_info'
    key = Column(Unicode(50), primary_key=True)
    value = Column(Unicode(1000))

    def __init__(self, key, value):
        self.key = key
        self.value = value

class Image(Base):
    """Table for store general images"""
    __tablename__ = 'images'
    
    image_id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    data = Column(LargeBinary, nullable=False)

    def __init__(self, name, data):
        self.name = name
        self.data = data

def populate():
    session = DBSession()
    model = AppInfo(key=u'db_version', value=u'0.0.2')
    session.add(model)    
    model = Director(name=u'Terry Jones', photo=buffer(open('papydvd/tests/250px-Terry_Jones.jpg').read()))
    session.add(model)
    session.add_all([Genre(name=u'Commedia',
                           description=u'Comedies are light-hearted plots consistently and deliberately designed to amuse and provoke laughter',
                           image=buffer(open('papydvd/tests/comedy-genre.jpg').read())),
                     Genre(name=u'Azione',
                           description=u"Action films usually include high energy, big-budget physical stunts and chases, possibly with rescues, battles, "
                                       u"fights, escapes, destructive crises (floods, explosions, natural disasters, fires, etc.), non-stop motion, spectacular "
                                       u"rhythm and pacing, and adventurous, often two-dimensional 'good-guy' heroes (or recently, heroines) battling 'bad guys' - "
                                       u"all designed for pure audience escapism",
                           image=buffer(open('papydvd/tests/comedy-genre.jpg').read())),
                     ])
    model = Movie(title=u"Monty Python's The Meaning of Life", primary_number=1, genre_id=1, director_id=1, year=1983,
                  story=u"An examination of the meaning of life in a series of sketches from conception to death and beyond, from the uniquely Python perspective.",
                  cover=buffer(open('papydvd/tests/220px-Meaningoflife.jpg').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    model = Image(name=u"transparent.png",
                  data=buffer(open('papydvd/transparent.png').read()))
    session.add(model)
    session.flush()
    transaction.commit()
    
def initialize_sql(db_string, db_echo=False):
    engine = create_engine(db_string, echo=db_echo)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    
    try:
        populate()
    except IntegrityError:
        pass
