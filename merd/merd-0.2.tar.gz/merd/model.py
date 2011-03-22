# Copyright (c) 2011, The merd Project
# All rights reserved.
   
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#    * Neither the name of the merd project nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Pieter Hooimeijer, Dan Lepage

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, \
    MetaData, PickleType, String, Text, Table, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, deferred, object_session, \
    relation, backref

from messages import DATASETOP_NEEDS_CONTEXT, log


SqlaBaseClass = declarative_base()

class Paper(SqlaBaseClass):
    __tablename__ = 'papers'
    pid      = Column(Integer, primary_key=True)
    name     = Column(String(50, convert_unicode=True), nullable=False, unique=True, index=True)
    created  = Column(DateTime)
    updated  = Column(DateTime, default=datetime.today)
    datasets = relation('DataSet', backref='paper', cascade="all, delete, delete-orphan")
    runs     = relation('Run', backref='paper', cascade="all, delete, delete-orphan")

    def __init__(self, name):
        self.name    = name
        self.created = datetime.today()


    def __repr__(self):
        return "<Paper name='%s'>" %(self.name,)

datasets_dataelts = Table('datasets_dataelts', Paper.metadata,
                          Column('dsid', Integer, ForeignKey('datasets.dsid')),
                          Column('deid', Integer, ForeignKey('dataelts.deid')))

class DataSet(SqlaBaseClass):
    __tablename__ = 'datasets'
    dsid     = Column(Integer, primary_key=True)
    pid      = Column(Integer, ForeignKey('papers.pid'))    
    created  = Column(DateTime)
    updated  = Column(DateTime, default=datetime.today)
    name     = Column(String(50, convert_unicode=True), nullable=False, unique=True, index=True)
    descr    = Column(Text(convert_unicode=True))

    paper = None # populated using backref
    runs  = None 
    elements = relation('DataElt', secondary=datasets_dataelts, backref='datasets')

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.created = datetime.today()

    def __repr__(self):
        return "<DataSet name='%s'>" %(self.name,)

    def __or__(self, other):
        try:
            ctx = object_session(self).expcontext
        except Exception:
            log(WARNING, DATASETOP_NEEDS_CONTEXT())
            return None
        return ctx.union(self, other)

    def __and__(self, other):
        try:
            ctx = object_session(self).expcontext
        except Exception:
            log(WARNING, DATASETOP_NEEDS_CONTEXT())
            return None
        return ctx.intersect(self, other)

    def __sub__(self, other):
        try:
            ctx = object_session(self).expcontext
        except Exception:
            log(WARNING, DATASETOP_NEEDS_CONTEXT())
            return None
        return ctx.minus(self, other)


class DataElt(SqlaBaseClass):
    __tablename__ = 'dataelts'
    deid       = Column(Integer, primary_key=True)
    created    = Column(DateTime)
    updated    = Column(DateTime, default=datetime.today, index=True)
    name       = Column(String(200, convert_unicode=True), index=True)
    content    = deferred(Column(LargeBinary))
    extradata  = deferred(Column(PickleType(mutable=False)))

    datasets = None # populated using backref
    results  = None

    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.created = datetime.today()

    def __repr__(self):
        name = self.name[0:20]
        if len(name) < len(self.name):
            name = name + "..."
        return "<DataElt name='%s'>" %(name,)

NEW        = "[new]"
RUNNING    = "[running]"
FAIL       = "[fail]"
SUCCESS    = "[success]"
INPROGRESS = "[in progress]"
DONE       = "[done]"

resultstates     = [ NEW, RUNNING, FAIL, SUCCESS ]
runstates = [ NEW, INPROGRESS, DONE ]

class Run(SqlaBaseClass):
    __tablename__ = 'runs'
    rid         = Column(Integer, primary_key=True)
    dsid        = Column(Integer, ForeignKey('datasets.dsid'))    
    pid         = Column(Integer, ForeignKey('papers.pid'))

    created     = Column(DateTime)
    updated     = Column(DateTime, default=datetime.today)

    name        = Column(String(50, convert_unicode=True), index=True, unique=True)
    descr       = deferred(Column(Text(convert_unicode=True)))
    status      = Column(Enum(*runstates))
    executorsrc = deferred(Column(Text(convert_unicode=True)))
    
    dataset     = relation(DataSet, backref=backref('runs', order_by=rid, cascade="all, delete-orphan"))
    meta        = deferred(Column(PickleType(mutable=False)))

    results = None # populated using backref
    paper   = None

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.created = datetime.today()
        self.status = NEW

    def __repr__(self):
        return "<Run name='%s'>" %(self.name,)


class Result(SqlaBaseClass):
    __tablename__ = 'results'
    resid       = Column(Integer, primary_key=True)
    rid         = Column(Integer, ForeignKey('runs.rid'))
    deid        = Column(Integer, ForeignKey('dataelts.deid'))
    created     = Column(DateTime)
    updated     = Column(DateTime, default=datetime.today, index=True)
    started     = Column(DateTime)
    finished    = Column(DateTime)
    runningtime = Column(Integer, index=True)
    status      = Column(Enum(*resultstates))
    stdout      = deferred(Column(LargeBinary))
    stderr      = deferred(Column(LargeBinary))
    exitcode    = Column(Integer)
    extradata   = deferred(Column(PickleType(mutable=False)))

    run         = relation(Run, backref=backref('results', order_by=rid, cascade="all, delete-orphan"))
    dataelt     = relation(DataElt, backref=backref('results', order_by=rid, cascade="all, delete-orphan"))

    def __init__(self):
        self.created    = datetime.today()
        self.status     = NEW

    def __repr__(self):
        return "<Result for '%s'>" %(str(self.dataelt),)

