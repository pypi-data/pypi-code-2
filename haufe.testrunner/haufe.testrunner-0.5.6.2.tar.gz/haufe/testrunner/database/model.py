################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
################################################################

"""
The database model
"""

import os
import datetime

from sqlalchemy import *
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base


def getModel(engine):

    Base = declarative_base(engine)

    class Testrunner(Base):
        __tablename__ = 'testrunner'

        id = Column(Integer, Sequence('testrunner_id_seq'), primary_key=True)
        name = Column(Unicode(256), index=True )
        last_run = Column(DateTime())
        run = relation('Run', backref='run_id', passive_deletes=True, cascade='all, delete-orphan')


    class Run(Base):
        __tablename__ = 'run'

        id = Column(Integer, Sequence('runs_id_seq'), primary_key=True)
        testrunner_id = Column(Integer, ForeignKey('testrunner.id'), index=True)
        created = Column(DateTime(), index=True)
        creator = Column(String(32))
        hostname = Column(String(32))
        ipaddress = Column(String(16))
        results_cumulated = Column(String(32))
        link = Column(String(256))
        description = Column(TEXT)
        run_ok = Column(Boolean, default=False)
        result = relation('Result', backref='result_id', passive_deletes=True, cascade='all, delete-orphan')


    class Result(Base):
       __tablename__ = 'result'

       id = Column(Integer, Sequence('result_id_seq'), primary_key=True)
       run_id = Column(Integer, ForeignKey('run.id'), index=True)
       module = Column(Unicode(512), index=True)
       logfile = Column(Unicode(512))
       logdata = Column(Text)
       tests_ok = Column(Boolean, default=False, index=True)
       tests_total = Column(Integer, default=0)
       tests_passed = Column(Integer, default=0)

    return Base, (Testrunner, Run, Result)
