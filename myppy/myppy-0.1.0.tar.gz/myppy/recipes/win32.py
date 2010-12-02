#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.

from __future__ import with_statement

import os
import sys
import tempfile
import stat
import urlparse
import urllib2
import subprocess
import shutil
from textwrap import dedent

from myppy.util import md5file, do, bt, cd, relpath, tempdir, chstdin

from myppy.recipes import base

class Recipe(base.Recipe):

    def _generic_configure(self,script=None,vars=None,args=None,env={}):
        if script is None:
            script = self.CONFIGURE_SCRIPT
        script = ["sh","-C",script]
        super(Recipe,self)._generic_configure(script,vars,args,env)


