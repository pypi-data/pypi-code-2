#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from coopr.opt.base import ProblemFormat, ResultsFormat
from coopr.opt.solver import SystemCallSolver
from pyutilib.component.core import alias
from pyutilib.misc import Bunch
from pyutilib.services import register_executable, registered_executable
from pyutilib.services import TempfileManager

create_tempfile = TempfileManager.create_tempfile

class OSSolver(SystemCallSolver):
    """The Optimization Systems solver."""

    alias('ossolver', doc='A draft interface to a generic OS solver')

    def __init__ (self, **kwargs):
        #
        # Call base constructor
        #
        kwargs['type'] = 'ossolver'
        SystemCallSolver.__init__( self, **kwargs )
        #
        # Valid problem formats, and valid results for each format
        #
        pformat = [ ProblemFormat.osil, ]
        rformat = { ProblemFormat.osil : ResultsFormat.osrl, }
        self._valid_problem_formats = pformat
        self._valid_result_formats  = rformat

    def executable ( self ):
        executable = registered_executable('ossolver')
        if executable is None:
            self.enable = False
            return 'intentional bad "path": no ossolver executable'
        return executable.get_path()

    def create_command_line ( self, executable, problem_files ):

        options = ('',)
        options = ' '.join( options )
        cmdline = executable + options

        return Bunch(cmd=cmdline, log_file=None, env=None)

    def process_logfile ( self ):
        return

    def process_soln_file ( self, results ):
        problem_files = ', '.join( self._problem_files )
        print 'Problem input files: %s' % problem_files

        plural = ''
        if len(self._problem_files) > 1: plural = 's'

        msg  = 'Coopr does not (currently) support an OSiL capable solver.\n'
        msg += 'To solve this problem, you must manually pass the above OSiL\n'
        msg += 'file%s to an OSiL compliant solver.\n'

        raise NotImplementedError, msg % plural

# register_executable(name='ossolver')
