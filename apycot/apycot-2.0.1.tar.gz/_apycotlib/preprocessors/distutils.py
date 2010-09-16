"""installation preprocessor using distutils setup.py

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import shutil
from os.path import join, exists, abspath

from logilab.common import optik_ext as opt
from logilab.common.shellutils import pushd

from apycotlib import register, SetupException
from apycotlib import Command
from apycotlib.preprocessors import BasePreProcessor


class DistutilsProcessor(BasePreProcessor):
    """python setup.py pre-processor

       Use a distutils'setup.py script to install a Python package. The
       setup.py should provide an "install" function which run the setup and
       return a "dist" object (i.e. the object return by the distutils.setup
       function). This preprocessor may modify the PATH and PYTHONPATH
       environment variables.
    """
    id = 'python_setup'
    _python_path_set = None
    _installed = set()

    options_def = {
        'verbose': {
            'type': 'int', 'default': False,
            'help': 'set verbose mode'
            },
        }

    # PreProcessor interface ##################################################

    def run(self, test, path=None):
        """run the distutils setup.py install method on a path if
        the path is not yet installed
        """
        if path is None:
            path = test.project_path()
        if not DistutilsProcessor._python_path_set:
            path = test.project_path()
            py_lib_dir = join(os.getcwd(), 'local', 'lib', 'python')
            # setuptools need this directory to exists
            if not exists(py_lib_dir):
                os.makedirs(py_lib_dir)
            test.update_env(path, 'PYTHONPATH', py_lib_dir, os.pathsep)
            test.update_env(path, 'PATH', join(os.getcwd(), 'bin'), os.pathsep)
            DistutilsProcessor._python_path_set = py_lib_dir
        # cache to avoid multiple installation of the same module
        if path in self._installed:
            return
        if not exists(join(path, 'setup.py')):
            raise SetupException('No file %s' % abspath(join(path, 'setup.py')))
        self._installed.add(path)
        cmd_args = ['python', 'setup.py', 'install', '--home',
                    join(test.tmpdir, 'local')]
        if not self.options.get('verbose'):
            cmd_args.append('--quiet')
        with pushd(path):
            cmd = Command(self.writer, cmd_args, raises=True)
            cmd.run()
            if exists('build'):
                shutil.rmtree('build') # remove the build directory


register('preprocessor', DistutilsProcessor)
