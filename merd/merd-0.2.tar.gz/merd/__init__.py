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

__all__ = ["ctx", "use_db", "commit", "rollback", "papers", "use_paper", "datasets",
           "use_dataset", "build_dataset", "conduct_run", "conduct_file_run", "dataset_from_path", 
           "dataset_from_run", "stripes"]

from inspect import getsource

from context import Context
from data import FileTreeBuilder, RunPredBuilder
from messages import SOURCE_DEFAULT
from runs import FileExecutor


ctx = Context()

def use_db(db_url):
    ctx.use_db(db_url)

def commit():
    return ctx.commit()

def rollback():
    return ctx.rollback()

def papers():
    return ctx.get_papers()

def use_paper(papername):
    return ctx.use_paper(papername)

def datasets(**kwargs):
    return ctx.get_datasets(**kwargs)

def use_dataset(ds, **kwargs):
    return ctx.use_dataset(ds, **kwargs)

def build_dataset(**kwargs):
    return ctx.build_dataset(**kwargs)

def conduct_run(**kwargs):
    return ctx.conduct_run(**kwargs)

def conduct_file_run(path, timeout):
    fe = FileExecutor(path, timeout)
    conduct_run(name="new run", executor=fe)
    

def dataset_from_path(paths, excludes):
    b = FileTreeBuilder(paths, excludes)
    return build_dataset(name="new dataset from filesystem", descr="", builder=b)

def dataset_from_run(run, pred):
    class MonkeyBuilder(RunPredBuilder):
        def meta_description(self):
            parent = RunPredBuilder.meta_description(self)
            src = SOURCE_DEFAULT()
            try:
                src = getsource(pred)
            except Exception:
                pass

            res = "Using `dataset_from_run` call with predicate:\n%s" % (src,)
            return '\n======\n'.join([res, parent])

        def want(self, result):
            return pred(result)

    b = MonkeyBuilder(run)
    return build_dataset(name=u'new dataset from run', descr=u'', builder=b)

def stripes(dataset, number):
    return ctx.stripes(dataset, number)

    
