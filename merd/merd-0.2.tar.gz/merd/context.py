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

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session

from data import DataSetBuilder, ds_intersect, ds_union, ds_minus, ds_stripe
from runs import Executor
from runs import ExecutorThread

from messages import log
from messages import ERROR, WARNING, MESSAGE
from messages import CREATE_FAILED, CREATED_PAPER, FOUND_PAPER, \
    CREATED_DATASET, FOUND_DATASET, FOUND_DATASETS, FOUND_RUNS, \
    ROLLBACK, INTERNAL_ERROR, NO_CURRENT_PAPER, USE_DB_TYPES,   \
    USE_PAPER_TYPES, USE_DATASET_TYPES, BUILD_DATASET_TYPES,    \
    BUILD_DATASET_MISSING_ARG, BUILD_DATASET_BAD_ARG,           \
    DATASET_NOT_FOUND, FLUSH_ERROR, GET_RUNS_KEY_ERROR,         \
    DATAELT_ADD_FAIL, DATAELT_OTHER_FAIL, DATASET_BUILT,        \
    DATASET_EXISTS, DATASET_EXISTS_OK, OTHERPAPERMATCH,         \
    CANNOT_ADD_DATASET, RESETTING_CURDATASET, CONDUCT_RUN_MISSING_ARG, \
    CONDUCT_RUN_BAD_ARG, CONDUCT_RUN_OTHER_DS, \
    CONDUCT_RUN_USE_CONT, CONDUCT_RUN_IN_PROGRESS, THREAD_FAILED, \
    BINOP_TYPES, STRIPE_TYPES, NOT_ENOUGH_ELEMENTS, CONDUCT_RUN_TYPES

from model import Paper, DataSet, DataElt, Run, Result, INPROGRESS, DONE, NEW

class Context:
    def __init__(self):
        self.dbengine  = None
        self.dbsession = None
        self.sessionmaker = None
        self.curpaper   = None
        self.curdataset = None
        self.executors = []

    def use_db(self, db_url):
        if type(db_url) not in [str, unicode]:
            log(ERROR, USE_DB_TYPES())
            return 

        try:
            engine = create_engine(db_url)
            self.dbengine = engine

            Paper.metadata.create_all(self.dbengine)
            self.sessionmaker = sessionmaker(bind=self.dbengine)
            self.dbsession = scoped_session(self.sessionmaker)
            self.dbsession.registry().expcontext = self

        except (SQLAlchemyError, ValueError, ImportError):
            log(ERROR, CREATE_FAILED(db_url))
            return

    def commit(self):
        try:
            self.dbsession.commit()
        except (SQLAlchemyError, ValueError):
            log(ERROR, FLUSH_ERROR())
            return False

        if self.curpaper is not None and self.curdataset is not None:
            if self.curdataset.paper != self.curpaper:
                log(WARNING, RESETTING_CURDATASET(self.curdataset.name, self.curpaper.name))
                self.curdataset = None

        return True

    def add(self, something):
        try:
            self.dbsession.add(something)
        except (SQLAlchemyError):
            return False
        return self.commit()
                
    def rollback(self):
        if self.dbsession is not None:
            self.dbsession.rollback()
            log(MESSAGE, ROLLBACK())
        else:
            log(ERROR, INTERNAL_ERROR())

    def get_papers(self):
        if not self.commit():
            return None

        return self.dbsession.query(Paper).all()

    def use_paper(self, papername):
        if not self.commit():
            return None

        if isinstance(papername, Paper):
            papername = papername.name
        elif type(papername) in [str, unicode]:
            pass
        else:
            log(ERROR, USE_PAPER_TYPES())
            return

        match = self.dbsession.query(Paper).filter_by(name=papername).first()
        if match is None:
            newpaper = Paper(papername)
            if not self.add(newpaper):
                log(ERROR, CANNOT_ADD_PAPER(papername))
                return None

            log(MESSAGE, CREATED_PAPER(papername))
            self.curpaper = newpaper
        else:
            self.curpaper = match
            log(MESSAGE, FOUND_PAPER(papername))
        return self.curpaper

    def get_datasets(self, **kwargs):
        if not self.commit():
            return None

        defaultargs = { "paper" : self.curpaper }

        for k in kwargs:
            if k not in defaultargs:
                log(ERROR, GET_DATASETS_BAD_ARG(k))
                return None

        for k in defaultargs:
            if k not in kwargs:
                if defaultargs[k] is None:
                    log(ERROR, NO_CURRENT_PAPER())
                    return None
                kwargs[k] = defaultargs[k]

        paper = kwargs["paper"]

        if self.curpaper is None or \
                (type(paper) in [str,unicode] and paper != self.curpaper.name) or \
                (isinstance(paper, Paper) and (paper.pid != self.curpaper.pid)):
            p = self.use_paper(paper)
            if p is None:
                return None

        count = self.dbsession.query(DataSet).with_parent(self.curpaper).count()
        log(MESSAGE, FOUND_DATASETS(self.curpaper.name, count))
        return self.dbsession.query(DataSet).with_parent(self.curpaper).all()

    def use_dataset(self, ds, **kwargs):
        dsname = None

        if not self.commit():
            return None

        if isinstance(ds, DataSet):
            dsname = ds.name
        elif type(ds) in [ str, unicode]:
            dsname = ds
        else:
            log(ERROR, USE_DATASET_TYPES())
            return None

        defaultargs = { "paper" : self.curpaper }

        for k in kwargs:
            if k not in defaultargs:
                log(ERROR, USE_DATASET_BAD_ARG(k))
                return None

        for k in defaultargs:
            if k not in kwargs:
                if defaultargs[k] is None:
                    log(ERROR, NO_CURRENT_PAPER())
                    return None
                kwargs[k] = defaultargs[k]

        if not (isinstance(kwargs["paper"], Paper) or type(kwargs["paper"]) in [str,unicode]):
            log(ERROR, USE_DATASET_TYPES())
            return None

        paper = kwargs["paper"]

        if self.curpaper is None or \
                (type(paper) in [str,unicode] and paper != self.curpaper.name) or \
                (isinstance(paper, Paper) and (paper.pid != self.curpaper.pid)):
            p = self.use_paper(paper)
            if p is None:
                return None

        match = self.dbsession.query(DataSet).filter_by(name=dsname).with_parent(self.curpaper).first()
        if match is None and type(ds) in [str, unicode]:
            try:
                otherpapermatch = self.dbsession.query(DataSet).filter_by(name=dsname).first()
                if otherpapermatch is not None:
                    log(ERROR, OTHERPAPERMATCH(otherpapermatch.paper.name, dsname))
                    return None
            except SQLAlchemyError as e:
                log(ERROR, INTERNAL_ERROR())
                return None

            ds = DataSet(dsname, "")
            ds.paper = self.curpaper
            if not self.add(ds):
                log(ERROR, CANNOT_ADD_DATASET(dsname))
                return None

            log(MESSAGE, CREATED_DATASET(dsname))
            self.curdataset = ds
            return self.curdataset

        if match is None and isinstance(ds, DataSet):
            ds.paper = self.curpaper
            if not self.add(ds):
                log(ERROR, CANNOT_ADD_DATASET(dsname))
                return None

            self.curdataset = ds
            log(MESSAGE, CREATED_DATASET(ds.name))
            return self.curdataset

        self.curdataset = match
        log(MESSAGE, FOUND_DATASET(dsname))
        return self.curdataset

    def build_dataset(self, **kwargs):
        if not self.commit():
            return None

        defaultargs = { "name"    : self.curdataset,
                        "paper"   : self.curpaper,
                        "builder" : None,
                        "update"  : False,
                        "descr"   : "" }

        for k in kwargs:
            if k not in defaultargs:
                log(ERROR, BUILD_DATASET_BAD_ARG(k))
                return None

        for k in defaultargs:
            if k not in kwargs:
                if defaultargs[k] is None:
                    log(ERROR, BUILD_DATASET_MISSING_ARG(k))
                    return None
                kwargs[k] = defaultargs[k]

        name    = kwargs["name"]
        paper   = kwargs["paper"]
        descr   = kwargs["descr"]
        builder = kwargs["builder"]
        update  = kwargs["update"]

        if not( type(name) in [str,unicode, DataSet] and
                type(descr) in [str,unicode] and
                type(paper) in [str,unicode, Paper] and
                isinstance(builder, DataSetBuilder) ):
            log(ERROR, BUILD_DATASET_TYPES())
            return None

        if type(name) == DataSet:
            dsname = name.name
        else:
            dsname = name

        existed = self.dbsession.query(DataSet).filter_by(name=dsname).first() != None
        ds = self.use_dataset(name, paper=paper)
        
        if ds is None:
            return None

        if existed and not update:
            log(ERROR, DATASET_EXISTS(name))
            return None

        if existed and update:
            log(MESSAGE, DATASET_EXISTS_OK(dsname))
            ds.descr = ds.descr + "\n\n====\n\n" + descr + \
                builder.meta_description()
        else: # didn't exist before
            ds.descr = ds.descr + builder.meta_description()
        
        try:
            for newelt in builder.elt_gen():
                newelt.datasets = [ds]
                if not self.add(newelt):
                    log(ERROR, DATAELT_ADD_FAIL())
                    return ds
        except Exception as e:
            log(ERROR, DATAELT_OTHER_FAIL())

        if not self.commit():
            raise ValueError()

        count = self.dbsession.query(DataElt).with_parent(ds).count()
        log(MESSAGE, DATASET_BUILT(name, count))
        return ds

    def conduct_run(self, **kwargs):
        if not self.commit():
            return None

        defaultargs = { "name"     : None,
                        "paper"    : self.curpaper,
                        "dataset"  : self.curdataset,
                        "executor" : None,
                        "cont"     : False,
                        "descr"    : "",
                        "meta"     : 0 }
        
        for k in kwargs:
            if k not in defaultargs:
                log(ERROR, CONDUCT_RUN_BAD_ARG(k))
                return None

        for k in defaultargs:
            if k not in kwargs:
                if defaultargs[k] is None:
                    log(ERROR, CONDUCT_RUN_MISSING_ARG(k))
                    return None
                if k == "meta":
                    kwargs[k] = None
                else:
                    kwargs[k] = defaultargs[k]

        name     = kwargs["name"]
        paper    = kwargs["paper"]
        dataset  = kwargs["dataset"]
        executor = kwargs["executor"]
        cont     = kwargs["cont"]
        descr    = kwargs["descr"]

        if not( type(name) in [str,unicode] and
                type(descr) in [str,unicode] and
                type(paper) in [str, unicode,Paper] and
                type(dataset) in [str, unicode,DataSet] and
                isinstance(executor, Executor) ):
           log(ERROR, CONDUCT_RUN_TYPES())
           return None

        ds = self.use_dataset(dataset, paper=paper)
        if ds is None:
            return None

        if type(name) == Run:
            runname = name.name
        else:
            runname = name

        run = self.dbsession.query(Run).filter_by(name=runname).first()

        if run is not None:
            if run.dataset != ds:
                if run.dataset is None:
                    rdsname = "<None>" 
                else:
                    rdsname = run.dataset.name

                if run.paper is None:
                    rpname = "<None>"
                else:
                    rpname = run.paper.name
                
                log(ERROR, CONDUCT_RUN_OTHER_DS(run.name, rdsname, rpname))
                return None

            if not cont:
                log(ERROR, CONDUCT_RUN_USE_CONT(run.name))
                return None

            if run.status == INPROGRESS:
                log(ERROR, CONDUCT_RUN_IN_PROGRESS(run.name))
                return None
            
            run.status = INPROGRESS
        else: # run is None
            if type(name) in [str,unicode]:
                run = Run(name, descr)
                run.status = INPROGRESS
                run.paper = self.curpaper
                run.dataset = self.curdataset
            else:
                run = name
                run.descr = run.descr + "\n" + descr
                run.status = model.INPROGRESS
                run.paper = self.curpaper
                run.dataset = self.curdataset

            if not self.add(run):
                log(ERROR, CANNOT_ADD_RUN(run.name))
                return None
        self.commit()
        self.dbsession.merge(run)

        runthread = ExecutorThread(executor, run.rid, self.curdataset.dsid, 
                                   self.curpaper.pid, self.sessionmaker)
        runthread.start()
        self.executors.append(runthread)
        self.dbsession.expire(run)
        return runthread

    def binopchecks(self, lhs, rhs):
        if not (type(lhs) in [str, unicode, DataSet] and
                type(rhs) in [str, unicode, DataSet]):
            log(ERROR, BINOP_TYPES())
            return None

        if self.curpaper is None:
            log(ERROR, NO_CURRENT_PAPER())
            return None

        if type(lhs) in [str, unicode]:
            lhsname = lhs
            lhs = self.dbsession.query(DataSet).filter_by(name=lhs).with_parent(self.curpaper).first()

        if lhs is None:
            log(ERROR, DATASET_NOT_FOUND(lhsname))
            return None
    
        if type(rhs) in [str, unicode]:
            rhsname = rhs
            rhs = self.dbsession.query(DataSet).filter_by(name=rhs).with_parent(self.curpaper).first()

        if rhs is None:
            log(ERROR, DATASET_NOT_FOUND(rhsname))
            return None

        return (lhs, rhs)

    def union(self, lhs, rhs):
        if not self.commit():
            return None

        res = self.binopchecks(lhs, rhs)
        if res is None:
            return None

        lhs = res[0]
        rhs = res[1]

        newname = ' '.join([str(lhs.dsid), "cup", str(rhs.dsid)])
        descr = "'%s' union '%s'" % (lhs.name, rhs.name)

        ds = DataSet(newname, descr)
        ds.paper = self.curpaper
        
        if not self.add(ds):
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            return None

        statement = ds_union(ds.dsid, lhs.dsid, rhs.dsid)
        try:
            self.dbengine.execute(statement)
        except Exception, e:
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            self.dbsession.delete(ds)
            self.dbsession.commit()
            return None
        
        self.dbsession.merge(ds)
        return ds
        
    def minus(self, lhs, rhs):
        if not self.commit():
            return None

        res = self.binopchecks(lhs, rhs)
        if res is None:
            return None

        lhs = res[0]
        rhs = res[1]

        newname = ' '.join([str(lhs.dsid), "sub", str(rhs.dsid)])
        descr = "'%s' setminus '%s'" % (lhs.name, rhs.name)

        ds = DataSet(newname, descr)
        ds.paper = self.curpaper
        
        if not self.add(ds):
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            return None

        statement = ds_minus(ds.dsid, lhs.dsid, rhs.dsid)
        try:
            self.dbengine.execute(statement)
        except Exception, e:
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            self.dbsession.delete(ds)
            self.dbsession.commit()
            return None
        
        self.dbsession.merge(ds)
        return ds

    def intersect(self, lhs, rhs):
        if not self.commit():
            return None

        res = self.binopchecks(lhs, rhs)
        if res is None:
            return None

        lhs = res[0]
        rhs = res[1]

        newname = ' '.join([str(lhs.dsid), "cap", str(rhs.dsid)])
        descr = "'%s' intersect '%s'" % (lhs.name, rhs.name)

        ds = DataSet(newname, descr)
        ds.paper = self.curpaper
        
        if not self.add(ds):
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            return None

        statement = ds_intersect(ds.dsid, lhs.dsid, rhs.dsid)
        try:
            self.dbengine.execute(statement)
        except Exception, e:
            log(ERROR, CANNOT_ADD_DATASET(ds.name))
            self.dbsession.delete(ds)
            self.dbsession.commit()
            return None
        
        self.dbsession.merge(ds)
        return ds
        
    def stripes(self, source, number):
        if not self.commit():
            return None

        if not (type(source) in [str, unicode, DataSet] and
                type(number) in [int, long]):
            log(ERROR, STRIPE_TYPES())
            return None

        if number < 1:
            log(ERROR, STRIPE_TYPES())
            return None

        if self.curpaper is None:
            log(ERROR, NO_CURRENT_PAPER())
            return None

        if type(source) in [str, unicode]:
            sourcename = source
            source = self.dbsession.query(DataSet).filter_by(name=source).with_parent(self.curpaper).first()

        if source is None:
            log(ERROR, DATASET_NOT_FOUND(sourcename))
            return None

        count = self.dbsession.query(DataElt).with_parent(source).count()

        if count < number:
            log(ERROR, NOT_ENOUGH_ELEMENTS(count, number))
            return None

        stripesize = count // number
        datasets = []

        for i in range(number):
            newds = DataSet("%s stripe %s" % (source.dsid, i), "Stripe %s out of %s for dataset '%s'." % (i + 1, number, source.name))
            newds.paper = self.curpaper
            self.add(newds)
            datasets.append(newds)

        if not self.commit():
            return None

        for i in range(number):
            lower = i * stripesize
            upper = (i + 1) * stripesize

            if i == number - 1:
                upper = count

            statement = ds_stripe(datasets[i].dsid, source.dsid, lower, upper)
            try:
                self.dbengine.execute(statement)
            except Exception, e:
                log(ERROR, CANNOT_ADD_DATASET(datasets[i].name))
                return None

        return datasets

            

            
            
            
                
                
            







        
