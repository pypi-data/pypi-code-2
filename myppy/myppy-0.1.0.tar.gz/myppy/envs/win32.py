#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.

from __future__ import with_statement

import os

from myppy.envs import base

from myppy.recipes import win32 as _win32_recipes


class MyppyEnv(base.MyppyEnv):
    """Myppy environment - win32 version.

    This environment depends on a recent version of MinGW and the associated
    developer tools (which helpfully includes some dependencies such as bz2).
    """

    def __init__(self,rootdir):
        super(MyppyEnv,self).__init__(rootdir)
        self.env = self._fix_env(self.env)

    def load_recipe(self,recipe):
        return self._load_recipe_subclass(recipe,MyppyEnv,_win32_recipes)

    def do(self,*cmdline,**kwds):
        env = kwds.pop("env",None)
        if env is not None:
            env = self._fix_env(env)
        cmdline = self._fix_cmdline(cmdline)
        print "CALLING", cmdline
        return super(MyppyEnv,self).do(*cmdline,**kwds)

    def bt(self,*cmdline,**kwds):
        env = kwds.pop("env",None)
        if env is not None:
            env = self._fix_env(env)
        cmdline = self._fix_cmdline(cmdline)
        print "CALLING", cmdline
        return super(MyppyEnv,self).bt(*cmdline,**kwds)

    def _fix_env(self,env):
        for (k,v) in env.iteritems():
            if isinstance(v,unicode):
                env[k] = v = v.encode("utf8")
            if not isinstance(v,str) or not isinstance(k,str):
                raise ValueError("bad env: %r => %r" % (k,v,))
        return env

    def _fix_cmdline(self,cmdline):
        cmdline = list(cmdline)
        if cmdline[0] in ("tar",):
            for i,path in enumerate(cmdline):
                if i == 0:
                    continue
                if len(path) < 3 or not path[1:3] == ":\\":
                    continue
                path = "/" + path.replace(":","").replace("\\","/")
                cmdline[i] = path
        return cmdline

