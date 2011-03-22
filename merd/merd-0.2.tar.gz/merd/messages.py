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

from sys import stdout
from traceback import format_exc

from config import VERSION

ERROR    = "ERROR"
WARNING  = "WARNING"
MESSAGE  = ":"

def log(severity, message):
    print ("%s: %s" % (severity, message))
    stdout.flush()

def CREATE_FAILED(url):
    return "Could not start db engine for url '%s'; aborting\nInternal exception:\n======\n%s\n\n" \
        % (url,format_exc())

def CREATED_PAPER(name):
    return ("New paper '%s'" % (name,))

def FOUND_PAPER(name):
    return ("Selected paper '%s'" % (name,))

def CREATED_DATASET(name):
    return ("New dataset '%s'" % (name,))

def FOUND_DATASET(name):
    return ("Selected dataset '%s'" %(name,))

def FOUND_DATASETS(papername, count):
    return ("Found %s dataset(s) for paper '%s'" % (count, papername))

def FOUND_RUNS(papername, count):
    return ("Found %s runs(s) for paper '%s'" % (count, papername))

def ROLLBACK():
    return "Session was rolled back"

def INTERNAL_ERROR():
    return "Encountered an inconsistent state; aborting"

def NO_CURRENT_PAPER():
    return "Must select a paper first with `use_paper`, or use `paper=...` argument"

def USE_DB_TYPES():
    return "`use_db` Expects argument of type `str` or `unicode`; aborting"

def USE_PAPER_TYPES():
    return "`use_paper` Expects argument of type `str`, `unicode`, or `Paper`; aborting"

def USE_DATASET_TYPES():
    return """`use_dataset` Expects:
     - name argument of type `str`, `unicode`, or `DataSet`
     - (optional) paper argument of type `str`, `unicode`, or `Paper`"""

def DATASET_NOT_FOUND(dsname):
    return "No dataset found with name '%s'; aborting" % (dsname,)

def CANNOT_ADD_PAPER(papername):
    return "Could not commit new paper '%s'; aborting" % (papername,)

def CANNOT_ADD_DATASET(dsname):
    return "Could not commit new dataset '%s'; aborting" % (dsname,)

def FLUSH_ERROR():
    return "Unable to flush database session; aborting\nInternal exception:\n======\n%s\n\n" \
                % (format_exc(),)

def GET_RUNS_KEY_ERROR(key, rightkeys):
    return "Unknown key '%s' passed to `get_runs`; legal keys are %s" % (key, str(rightkeys))

def PATH_DNE(path):
    return "Path '%s' does not exist" % (path,)

def SOURCE_DEFAULT():
    return "[Source not available]\n"

def FILE_TREE_BUILDER_DESCR(paths, excludes):
    return "Built with FileTreeBuilder v. %s (or a derived class). Settings:\n - paths: %s\n - excludes: %s\n\nSource code follows:\n\n" \
        % (VERSION, paths, excludes)

def RUN_PRED_BUILDER_DESCR(runname):
    return "Built with RunPredBuilder v. %s (or a derived class). Settings:\n - based on run: '%s'\n\n Source code follows:\n\n" \
        % (VERSION,runname)

def BUILD_DATASET_TYPES():
    return """`build_dataset` Expects arguments with types:
     - name    : str or unicode, or a DataSet
     - paper   : paper name or object
     - descr   : str or unicode
     - builder : merd.data.DataSetBuilder or subtype
     - update  : boolean or compatible\n"""

def CONDUCT_RUN_TYPES():
    return """`conduct` Expects arguments with types:
     - name    : str or unicode
     - paper   : paper name or object
     - descr   : str or unicode
     - builder : merd.data.DataSetBuilder or subtype
     - update  : boolean or compatible\n"""

def USE_DATASET_BAD_ARG(name):
    return "Unknown argument '%s' for `use_dataset`" % (name,)

def BUILD_DATASET_BAD_ARG(name):
    return "Unknown argument '%s' for `build_dataset`" % (name,)

def BUILD_DATASET_MISSING_ARG(name):
    return "Missing argument '%s' for `build_dataset`" % (name,)

def DATASET_EXISTS(name):
    return "Dataset '%s' already exists. Use `update=True` to override" % (name,)

def DATASET_EXISTS_OK(name):
    return "Updating existing dataset '%s' (appending to description; skipping existing elements)" % (name,)

def DATASET_ADD_FAIL():
    return "Error while adding dataset; aborting"

def DATAELT_ADD_FAIL():
    return "Encountered a database error while adding a data element; dataset may be incomplete\nInternal exception:\n======\n%s\n\n" \
        % (format_exc(),)

def DATAELT_OTHER_FAIL():
    return "Encountered an error while building data elements; dataset may be incomplete\nInternal exception:\n======\n%s\n\n" \
        % (format_exc(),)

def DATASET_BUILT(name, count):
    return "Built dataset '%s' with %s elements" % (name, count)

def OTHERPAPERMATCH(papername, datasetname):
    return "A dataset '%s' already exists for paper '%s'; aborting" % (datasetname, papername)

def RESETTING_CURDATASET(datasetname, papername):
    return "Resetting current dataset '%s'; no longer belongs to paper '%s'" % (datasetname, papername)

def CONDUCT_RUN_BAD_ARG(k):
    return "Unkown argument '%s' for `conduct_run`" % (k,)

def CONDUCT_RUN_MISSING_ARG(k):
    return "Missing argument '%s' for `build_dataset`" % (k,)

def CONDUCT_RUN_USE_CONT(name):
    return "Run '%s' already exists. Use `cont=True` to override" % (name,)

def CONDUCT_RUN_OTHER_DS(runname, datasetname, papername):
    return "Run '%s' already exists for dataset '%s', which belongs to paper '%s'" % (runname, datasetname, papername)

def CONDUCT_RUN_IN_PROGRESS(name):
    return "Run '%s' is in progress" % (name,)

def THREAD_FAILED():
    return "Unable to create a thread; aborting run"

def BASIC_PROC_EXECUTOR_DESCR():
    return "Conducted with subclass of BasicProcExecutor v. %s. Source code follows:\n\n" \
        % (VERSION,)

def FILE_EXECUTOR_DESCR():
    return "Conducted with FileExecutor v. %s (or a derived class). Source code follows:\n\n" \
        % (VERSION,)

def NOT_EXECUTABLE(path):
    return "Path '%s' not found, or not executable" % (path,)

def BINOP_TYPES():
    return "DataSet operation expects two parameters of type `str`, `unicode`, or `model.DataSet`"

def DATASETOP_NEEDS_CONTEXT():
    return "Both operands for operators `| & -` must be persistent in the db and part of an active context."

def STRIPE_TYPES():
    return "`stripe`: wrong parameter type"

def NOT_ENOUGH_ELEMENTS(count, number):
    return "Found %s elements; cannot distribute across %s stripes" % (count, number)
