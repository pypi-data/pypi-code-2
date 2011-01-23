#!/usr/bin/env python

# Alchemy Libraries
from sqlalchemy import create_engine, Table, Column, Numeric, Integer, String, Boolean, MetaData, ForeignKey, Sequence
from sqlalchemy.orm import sessionmaker, mapper, backref, relation, clear_mappers
from sqlalchemy.types import DateTime, Date

import conf.settings
import clsexceptions
import dbobjects
from writer import Writer

class HMISCSV27Writer(dbobjects.DatabaseObjects):

    # Writer Interface
    implements (Writer)

    def __init__(self):
        pass

