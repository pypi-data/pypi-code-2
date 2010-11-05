#!/usr/bin/python

"""
metals: metadata list (here movies)

copyright (c) 2010  david (dayf)

for a similar project regarding metadata for scholarly pdf files see 'pdfmeat'
(could combine both approaches into a generic one)

intial 'imdb movie data on the command line' script 'lm' by goffi

further ideas/todos:
- akas (original vs foreign film title)
- open web browser tab (as by goffi's script?)
- option to delete entries (just use sqliteman!)
- mark unfound movies/wrong findings
"""


import sys
import os

userdir = os.path.expanduser('~') + os.sep
#userdir+= 'Dropbox' + os.sep
#userdir+= 'Ubuntu\ One' + os.sep


sqlitefile = 'sqlite:///' + userdir + 'movienodes.sqlite'

ext_movie = [u'.divx', u'.mov', u'.avi', u'.ogv', u'.rmvb', u'.mkv', u'.mpg', u'.wmv', u'.mp4', u'.m4v']
strip_exp = ['divx','xvid', 'dvdrip', 'b[rd][ -]rip', '720p?', '1080p?', 'x?264', 'HDTV','AC3','[^a-z]HD[^a-z]', 'Sample', '^Audio', 'audio track',]

import argparse
import re
import urllib
import json

try:
    import imdb
    import sqlalchemy
    import opensubtitleshashing #http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes#Python
except:
    print """
metals needs the following libraries

* IMDbPY                                   (sudo apt-get install python-imdbpy)
* SQLAlchemy                               (sudo apt-get install python-sqlalchemy)
* opensubtitles.org hashing function       (opensubtitleshashing.py)
* termcolor [recommended for color output] (sudo pip install termcolor)

"""
    sys.exit(2)

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
 
Base = declarative_base()

class MovieNode(Base):
    __tablename__ = 'movienode'

    inode = Column(Integer, primary_key=True)
    filename = Column(String(255))
    filedir = Column(String(255))
    ososh = Column(String(64)) # opensubtitles org hash
    
    imdb = Column(String(16)) # int nicer? front zero
    title = Column(String(255))
    canonical = Column(String(255))
    year = Column(Integer)
    rating = Column(Float)
    director = Column(String(255))
    country = Column(String(255))    
    genre = Column(String(255))
    outline = Column(Text)
    plot = Column(Text)
    cast = Column(Text)
    fulltext = Column(Text)
    #directed_by = Column(Integer, ForeignKey('directors.id'))
    #director = relation("Director", backref='movies', lazy=False)
 
    def __init__(self, inode=None, filename=None, filedir=None, ososh=None):
        self.inode = inode
        self.filename = filename
        self.filedir = filedir
        self.ososh = ososh
    def __repr__(self):
        try:
            # sudo pip install termcolor
            from termcolor import colored
            return u"%s %s %s %s %s" % (
                colored("%s" % self.title,  attrs=('bold',)),
                colored("(%d, %s)" % (self.year, self.country), 'blue', attrs=('bold',)),
                #colorize("%s" % self.country, fg='blue'),
                colored("[%.1f, %s]" % (self.rating, self.director), 'magenta', attrs=('bold',)),
                colored("%s" % self.genre, 'blue'),
                self.filename)
        except Exception, e:
            #print 'no color', e
            pass
        return u"%s (%d, %s) [%.1f, %s] - %s" % (self.title, self.year, self.country, self.rating, self.genre, self.filename)
        #return "MovieNode(%r, %r)" % (self.inode, self.filename)
    def __unicode__(self):
        return self.title

    def create_fulltext(self):
        #d = {'inode': self.inode,'filename':self.filename, 'filedir'}
        d = self.inode, self.filename, self.filedir, self.ososh, self.imdb, self.title, self.canonical, self.year, self.rating, self.director, self.country, self.genre, self.outline, self.plot, self.cast
        return json.dumps(d)



engine = create_engine(sqlitefile)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
sess = Session()


i = imdb.IMDb()

def google_imdb_id(q):
    """query google for imdb_id"""
    query_string = "site:imdb.com/title/ " + q.strip()
    query = urllib.urlencode({'q' : query_string})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % ( query  )
    #url+= '&key=GOOGLEAJAXKEY' #&userip=myIP' 
    resultset = urllib.urlopen(url)
    resjs = json.load(resultset)
    #restr = str(resjs).encode('utf-8')
    #['responseStatus'] == 200  #  403
    #try:    
    if resjs is not None and len(resjs['responseData']['results']) > 0:
        results = resjs['responseData']['results']
        for result in results:
            m = re.match('http://www.imdb.com/title/tt([0-9]+)/$', result['url'])
            if m is not None:
                imdb_id = m.group(1)
                print "Query for \"%s\" returned <%s>: %s" % (q, result['url'], result['titleNoFormatting'].replace(' - IMDb', '') )
                return imdb_id
                #break
    else:
        print q, "- no imdb_id found (hint: name movie files using title and year)"

class NodeLister():
    
    files = []

    def __init__(self, mypath = '.', ext_filter = ext_movie):
        self.get_files(mypath = mypath, ext_filter = ext_filter)


    def get_files(self, mypath = '.', ext_filter = None):
        """get a list files on given path filtered by given extension list"""
        filelist_ = []
        filelist = [] # map() ?
        filedir = os.path.realpath(mypath) # gets dirname
        if os.path.isdir(filedir):
            filelist_ = os.listdir(filedir)
            for filename in filelist_:
                filename = filedir + os.sep + filename
                filelist.append(filename)
        else:
            filelist.append(mypath)

        if ext_filter is not None:
            filelist = filter(lambda file:os.path.splitext(file)[1].lower() in ext_filter, filelist)

        for filename in filelist:
            #mn = MovieNode(inode = os.stat(filepath).st_ino)
            #mn = sess.merge(mn)
            q = sess.query(MovieNode)
            mn = q.get(os.stat(filename).st_ino)
            filenode = {'filedir': filedir, 
                        'filename': os.path.basename(filename),
                        'inode':    os.stat(filename).st_ino,
                        'filetitle': self.filename_title(os.path.basename(filename)),
                        'ososh': opensubtitleshashing.hashFile(filename),
                        'meta': mn
                       }
            #print filenode
            #sys.exit()
            self.files.append(filenode)




    def filename_title(self, filename):
        """clean movie filename fit for googleing site:imdb"""
        filetitle = re.sub('\.[^.]+$', '', filename) # strip .ext
        filetitle = re.sub('[^a-zA-Z 0-9]', ' ', filetitle)
        filetitle = re.sub('(.*?)([^0-9]([12][90][0-9][0-9])[^0-9]).*$', r'\1 \2', filetitle) # title year
        filetitle = re.sub('(.*?)([0-9])[^0-9]*?$', r'\1\2', filetitle) # truncate anything after very last digit
        for exp in strip_exp: # 
            filetitle = re.sub('(.*?)'+exp+'.*$', r'\1', filetitle, re.I)
        return filetitle


    def retrieve_metadata(self, filenode):
        """retrieve metadata for movie file via google and imdb"""
        imdb_id = google_imdb_id(filenode['filetitle'])
        if imdb_id is not None:
            movie = i.get_movie(imdb_id)
            mn = MovieNode(inode=filenode['inode'], filename=filenode['filename'], filedir=filenode['filedir'], ososh=filenode['ososh'])
            mn = sess.merge(mn)
            mn.imdb = imdb_id
            mn.title = movie.get('title')
            mn.canonical = movie.get('smart canonical title')# or movie.get('t
            mn.year = int(movie.get('year'))
            mn.rating = float(movie.get('rating'))
            mn.director = ', '.join([director.get('name') for director in (movie.get('director') or [])])
            mn.country = ', '.join(movie.get('countries')) #[country for country in (movie.get('countries') or [])] #imdbpy fixed mid 2010
            mn.genre = ', '.join(movie.get('genre'))
            mn.outline = movie.get('plot outline')
            mn.plot = (movie.get('plot') or [''])[0]
            mn.cast = ', '.join(  [actor.get('name') for actor in (movie.get('cast') or [])]  )
            #i.update(movie)
            mn.fulltext = json.dumps(mn.create_fulltext())
            #sess.add(mn)
            #sess.commit()
            filenode['meta'] = mn
            return mn





parser = argparse.ArgumentParser(description='Supply metadata to local movie files.', epilog='common invocation: metals, metals DIR, metals --sel ryt')
#parser.add_argument('files', metavar='F', type=str, nargs='+', help='movie file or dir')
parser.add_argument('dirfile', metavar='F', type=str, nargs='?', help='movie file or dir', default='.')
parser.add_argument('--update', action='store_true', help='retrieve data even if in db')
parser.add_argument('--info', action='append', help='additional field(s) to print (outline, plot, cast)')
parser.add_argument('--long', action='store_true', help='additionally prints outline and cast')
parser.add_argument('--db', action='store_true', help='list all films in db')
parser.add_argument('--by', help='list all films in db ordered by field')
parser.add_argument('--sel', action='store', help='list all films: selected fields denoted by initial: ryt for rating year title; ordering by first given field')
parser.add_argument('--dir', action='store', help='list all films from matching directory')
parser.add_argument('--any', action='store', help='list all films matching any field content')
parser.add_argument('--dbdo', action='store', help='[special maintenance work on db]')
parser.add_argument('--dry', action='store', help='dry run: query imdb by given keywords only')
args = parser.parse_args()


selkeys = {'y':'year', 'r':'rating', 't':'title', 'T':'canonical', 'c':'country', 'g':'genre', 'f':'filename', 'd':'director', 'D':'filedir', 'O':'outline','P':'plot', 'i':'imdb', 'I':'inode', 'H':'ososh'}

if args.dbdo == 'updatefulltext':
    sq = sess.query(MovieNode)
    for mn in sess.query(MovieNode).all():
        mn.fulltext = mn.create_fulltext()
    sess.commit()
    sys.exit(1)
    
if args.dry is not None:
    imdb_id = google_imdb_id(args.dry)
    if imdb_id is not None:
        movie = i.get_movie(imdb_id)
        #mn.title = movie.get('title')
        #mn.canonical = movie.get('smart canonical title')# or movie.get('t
        #mn.year = int(movie.get('year'))
        print "%s (%s) [%s]" % (movie.get('title'), movie.get('year'), movie.get('rating'))
    sys.exit(1)

if args.db or args.by or args.sel or args.dir or args.any: 
    sq = sess.query(MovieNode)
    if args.by is None:
        args.by = 'rating'
        if args.sel is not None:
            args.by = selkeys.get(args.sel[0])
        if args.dir is not None:
            sq = sq.filter(MovieNode.filedir.like('%'+args.dir+'%'))
        if args.any is not None:
            sq = sq.filter(MovieNode.fulltext.like('%'+args.any+'%'))
    for mn in sq.order_by(getattr(MovieNode, args.by)):
        if args.sel:
            output = []
            for selkey in args.sel:
                output.append(str(getattr(mn,selkeys.get(selkey))))
            print ' \t'.join(output)
        else:
            print mn,mn.filedir
        if args.long:
            print mn.outline, '\n', mn.cast, '\n\n'
else:

    nl = NodeLister(mypath = args.dirfile, ext_filter = ext_movie)
    
    if not nl.files:
        print 'no movie files found in', args.dirfile

    for filenode in nl.files:
        #print filenode
        #if not filenode.has_key('meta'):
        if filenode['meta'] is None or args.update is True:
            mn = nl.retrieve_metadata(filenode)
            sess.add(mn)
            sess.commit()
        #else:
        m = filenode['meta']
        #print m.inode, m.filename, m.title, m.year, m.rating, m.genre, m.country
        #print "%s (%d, %s) [%.1f, %s] - %s" % (m.title, m.year, m.country, m.rating, m.genre, m.filename)
        if m is not None:
            o = str(m)
            #todo: merge w/ above
            if args.long:
                #import termcolors
                #print termcolors.colorize(str(m.outline), 'bold', fg='red')
                o = '\n' + str(m) + '\n' + m.outline, '\n', m.cast, '\n\n'
            # sqlalchemy synonyms needed?
            for field in args.info or []:
                o = '\n' + str(m) + '\n' + getattr(m, field)
            print o

