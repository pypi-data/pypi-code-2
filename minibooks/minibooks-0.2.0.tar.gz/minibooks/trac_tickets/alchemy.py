from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Float, String, Date, MetaData 
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import select
from django.conf import settings

from PIL import Image
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import date2num
from StringIO import StringIO

engine = create_engine('postgres://%s:%s@%s/%s' % (settings.TRAC_USER, settings.TRAC_PASS, settings.TRAC_HOST, settings.TRAC_BASE), echo=True)
metadata = MetaData()

author_hours_daily_summary = Table('author_hours_daily_summary', metadata,
        Column('date', Date, primary_key=True),
        Column('author', String(40)),
        Column('hours', Float )
)

class DayAuthorHoursSummary(object):
    def __init__(self, author, date, hours):
        self.author = author
        self.date = date
        self.hours = hours
        
    def __repr__(self):
        return "<Day('%s', '%s', '%f')>" % (self.author, self.date, self.hours)

mapper(DayAuthorHoursSummary, author_hours_daily_summary)

Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
session = Session()

def developers():
    """Return a list of authors for caktus projects"""
    connection = engine.connect()
    s = select([author_hours_daily_summary.c.author]).distinct()
    result = connection.execute(s)
    authors = []
    for row in result:
        if row[0] != 'root':
            authors.append(row[0])
    result.close()
    return authors
