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

from inspect import getsource

from itertools import chain

from os import walk
from os.path import abspath, exists as pathexists, isdir, join as pathjoin, normpath, relpath
from messages import log, ERROR, PATH_DNE, SOURCE_DEFAULT, FILE_TREE_BUILDER_DESCR, \
    RUN_PRED_BUILDER_DESCR
from model import DataSet, DataElt, datasets_dataelts

### Experimental SQLAlchemy source
### for generating dependent select clauses
### as part of an insert statement

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import select, exists, and_, or_, not_, join
from sqlalchemy.sql.expression import Executable, ClauseElement

class InsertFromSelect(Executable, ClauseElement):
    def __init__(self, table, select):
        self.table = table
        self.select = select

@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    return "INSERT INTO %s %s" % (
        compiler.process(element.table, asfrom=True),
        compiler.process(element.select)
    )
##############################3

class DataSetBuilder:
    def meta_description(self):
        raise NotImplementedError()

    def elt_gen(self):
        raise NotImplementedError()

class FileTreeBuilder(DataSetBuilder):
    def __init__(self, paths, excludedirs=[]):
        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            if not (pathexists(path) and isdir(path)):
                log(ERROR, PATH_DNE(path))
                raise ValueError()

        self.paths = paths
        self.excludedirs = excludedirs

    def meta_description(self):
        src = SOURCE_DEFAULT()
        try:
            src = getsource(self.__class__)
        except Exception:
            pass
        return FILE_TREE_BUILDER_DESCR(self.paths, self.excludedirs) + src
        
    def elt_gen(self):
        for path in self.paths:
            for root, dirs, files in walk(path, topdown=True):
                for d in self.excludedirs:
                    if d in dirs: dirs.remove(d)

                for filename in files:
                    name = normpath(pathjoin(path, relpath(pathjoin(root,filename), path)))
                    f = open(pathjoin(root,filename))
                    content = f.read()
                    f.close()
                    retval = DataElt(name, content)
                    yield retval

class RunPredBuilder(DataSetBuilder):
    def __init__(self, run):
        self.run = run

    def meta_description(self):
        src = SOURCE_DEFAULT()
        try:
            src = getsource(self.__class__)
        except Exception:
            pass
        return RUN_PRED_BUILDER(self.run.name) + src

    def elt_gen(self):
        for r in self.run.results:
            if self.want(r):
                yield r.dataelt

    def want(self, result):
        raise NotImplementedError()

def ds_intersect(targetid, lhsid, rhsid):
    a = datasets_dataelts.alias()
    b = datasets_dataelts.alias()
    
    sp = b.select().where(and_(b.c.dsid==rhsid, b.c.deid==a.c.deid))
    s  = select([targetid, a.c.deid]).where( and_(a.c.dsid==lhsid, exists(sp)) )
    return InsertFromSelect(datasets_dataelts, s)

def ds_union(targetid, lhsid, rhsid):
    a = datasets_dataelts.alias()
    s  = select([targetid, a.c.deid]).where(or_(a.c.dsid==lhsid, a.c.dsid==rhsid))
    return InsertFromSelect(datasets_dataelts, s)

def ds_minus(targetid, lhsid, rhsid):
    a = datasets_dataelts.alias()
    b = datasets_dataelts.alias()
    sp = b.select().where(and_(b.c.dsid==rhsid, b.c.deid==a.c.deid))
    s  = select([targetid, a.c.deid]).where( and_(a.c.dsid==lhsid, not_(exists(sp))) )
    return InsertFromSelect(datasets_dataelts, s)

def ds_stripe(targetid, sourceid, lower, upper):
    a = datasets_dataelts.alias()
    s = select([targetid, a.c.deid], offset=lower, limit=upper - lower).where(a.c.dsid==sourceid)
    return InsertFromSelect(datasets_dataelts, s)

