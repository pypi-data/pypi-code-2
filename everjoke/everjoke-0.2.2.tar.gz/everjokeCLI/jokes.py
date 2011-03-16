"""
Instantiate and manipulate a table of jokes.
"""

from re import search, match, findall
from datetime import datetime
from os import mkdir, system
from os.path import isfile, expanduser, join, basename, exists
from sys import platform
from pipes import quote

from sqlalchemy import Table, Column, Integer, String,\
                       MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, mapper, sessionmaker
from sqlalchemy.types import Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


##########################################################################
# ACCESSOR CLASS
##########################################################################


class JokeTable(object):
    """Establish and manipulate a database of jokes."""

    def __init__(self, engine_name=''):
        """Establish the working directory and map the database."""
        self.library_path = self._buildLibraryPath()
        x = datetime.now()
        self._buildDirs(str("%04d" %x.year), str("%02d" % x.month))
        self.yyyy_mm_path = "%04d/%02d" % (x.year, x.month)
        self.defaultfile = "%04d-%02d-%02d" % (x.year, x.month, x.day)

        # Map the database
        if engine_name:
            engine = create_engine(engine_name)
        else:
            engine = create_engine('sqlite:///' + self.library_path +
                                    '/jokes.db')
        # get a handle on the table object
        jokes_table = Joke.__table__
        # get a handle on the metadata
        metadata = Base.metadata
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    ######################################################################
    # read/write methods
    ######################################################################

    def EditJournal(self):
        """Open today's journal file in Vim, collect the output."""
        journalfile = join(self.library_path, 'journal', self.yyyy_mm_path,
                            self.defaultfile)
        system('vim ' + quote(journalfile))
        self.AddJokesFromFile(journalfile)

    def AddJokesFromFile(self, filename):
        """Update the database with jokes parsed from filename."""
        if isfile(filename):
            name = text = ""
            origin = basename(filename)
            f = open(filename, 'r')
            for line in f:
                if self._foundJokeName(line):
                    name = self._trimName(line)
                    text = ""
                elif self._endOfJoke(line):
                    self._addOrUpdateJoke(Joke(name, text, origin))
                else:
                    text += line
            f.close()
        self.session.commit()

    def AppendJokeToFile(self, id, suffix=False):
        """Append a joke by ID to a journal file or a set file."""
        joke = self.GetJokeByID(id)
        filename = ''
        if suffix:
            filename = join(self.library_path,
                        'sets',
                        self.yyyy_mm_path,
                        self.defaultfile +
                        '-' + suffix)
        else:
            filename = join(self.library_path,
                        'journal',
                        self.yyyy_mm_path,
                        self.defaultfile)
        f = open(filename, 'a')
        f.write('\n\n')
        f.write('--' + joke.name + '\n')
        f.write(joke.bodies[-1].text)
        f.write('--!')

    ######################################################################
    # accessor methods
    ######################################################################

    def GetJokeList(self, status=None):
        """Return the list of all jokes."""
        q = self.session.query(Joke)
        if status:
            q = q.filter(Joke.status == status)
        return q

    def GetJokeByID(self, id):
        q = self.session.query(Joke).filter(Joke.id == id)
        return q.first()

    ######################################################################
    # modifier methods
    ######################################################################

    def SetJokeStatus(self, id, status):
        """Set the status of an existing joke."""
        joke = self.GetJokeByID(id)
        joke.status = status
        self.session.merge(joke)
        self.session.commit()

    def _addOrUpdateJoke(self, joke):
        """Update the body of a joke, or create the joke if it is new."""
        existingJoke = self._getJokeByName(joke.name)
        if existingJoke:
            existingBody = joke._getExistingBody(existingJoke.bodies)
            if existingBody:
                existingBody.text = joke.bodies[0].text
            else:
                existingJoke.bodies.append(joke.bodies[0])
            existingJoke.wordcount =\
            existingJoke._countWords(joke.bodies[0].text)
            existingJoke.punchcount =\
            existingJoke._countPunches(joke.bodies[0].text)
            self.session.merge(existingJoke)
            return existingJoke.name
        else:
            self.session.add(joke)
            return joke.name

    ######################################################################
    # private methods
    ######################################################################

    def _getJokeByName(self, name):
        q = self.session.query(Joke).filter(Joke.name == name)
        if len(q.all()) > 1:
            raise Exception('Multiple jokes of the same name exist.')
        return q.first()

    def _foundJokeName(self, string):
        return match('--[^!]', string)

    def _endOfJoke(self, string):
        return match('--!', string)

    def _trimName(self, string):
        m = search('(?<=--).*', string)
        return m.group(0)

    def _buildLibraryPath(self):
        """
        Establish a local data directory appropriate to the OS.
        
        Build default working directories if they do not exist.
        """
        myOS = platform
        library_path = ''
        if myOS == 'darwin':
            library_path = expanduser('~')
            library_path = join(library_path, 'Library',
                            'Application Support', 'Everjoke')
            if not exists(library_path):
                mkdir(library_path)
            if not exists(join(library_path, 'journal')):
                mkdir(join(library_path, 'journal'))
            if not exists(join(library_path, 'sets')):
                mkdir(join(library_path, 'sets'))
        return library_path

    def _buildDirs(self, year, month):
        """Build YYYY/MM working directories if they do not exist."""
        year_journal = join(self.library_path, 'journal', year)
        year_sets = join(self.library_path, 'sets', year)
        month_journal = join(self.library_path, 'journal', year, month)
        month_sets = join(self.library_path, 'sets', year, month)
        if not exists(year_journal):
            mkdir(year_journal)
        if not exists(year_sets):
            mkdir(year_sets)
        if not exists(month_journal):
            mkdir(month_journal)
        if not exists(month_sets):
            mkdir(month_sets)


##########################################################################
# DATA CLASSES
##########################################################################


class Joke(Base):
    """Build a Joke."""
    __tablename__ = 'jokes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    isDeprecated = Column(Boolean)
    status = Column(String)
    wordcount = Column(Integer)
    punchcount = Column(Integer)
    # bodies = relationship(Body, backref=backref('jokes'))

    def __init__(self, name, bodytext, origin=None):
        self.name = name
        self.bodies.append(Body(bodytext, origin))
        self.wordcount = self._countWords(bodytext)
        self.punchcount = self._countPunches(bodytext)
        self.status = "Try"
        self.isDeprecated = False

    def _countWords(self, string):
        """Count the words in a Joke's Body."""
        return len(string.split())

    def _countPunches(self, string):
        """
        Count the punchlines in a Joke's Body.

        Punchlines are indicated by an asterisk '*'.
        """
        return len(findall('\*', string))

    def _getExistingBody(self, bodies):
        for body in bodies:
            if self.bodies[0].origin == body.origin:
                return body
            return False


class Body(Base):
    """Build a Body, backlinked to a Joke."""
    __tablename__ = 'bodies'
    id = Column(Integer, primary_key=True)
    origin = Column(String)
    text = Column(String)
    joke_id = Column(Integer, ForeignKey('jokes.id'))
    joke = relationship(Joke, backref=backref('bodies', order_by=id))

    def __init__(self, text, origin):
        self.text = text
        if origin:
            self.origin = origin
        # The "date" will always be derived from the adding file's name.
        # The following case will only be triggered in unit testing.
        else:
            x = datetime.now()
            origin = "%04d-%02d-%02d %02d:%02d:%02d" %\
                   (x.year, x.month, x.day, x.hour, x.minute,
                   x.microsecond)
            self.origin = origin
