#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import glob
import shutil
import os

class MockMIP(object):
    """Methods used to create a mock MIP solver used for testing
    """

    def __init__(self, mockdir):
        self.mock_subdir=mockdir

    def create_command_line(self,executable,problem_files):
        self._mock_problem = problem_files[0].split(os.sep)[-1]
        self._mock_problem = self._mock_problem.split(".")[0]
        self._mock_dir = os.sep.join(problem_files[0].split(os.sep)[:-1])

    def executable(self):
        return "mock"

    def _execute_command(self,cmd):
        for file in glob.glob(self._mock_dir+os.sep+self.mock_subdir+os.sep+self._mock_problem+"*"):
          if not self.soln_file is None and file.split(".")[-1] in ["soln","sol"]:
             shutil.copyfile(file,self.soln_file)
          if file.split(".")[-1] != "out":
             shutil.copyfile(file,self._mock_dir+os.sep+(file.split(os.sep)[-1]))
        log=""
        fname = self._mock_dir+os.sep+self.mock_subdir+os.sep+self._mock_problem+".out"
        if not os.path.exists(fname):
            raise ValueError, "Missing mock data file: "+fname
        INPUT=open(self._mock_dir+os.sep+self.mock_subdir+os.sep+self._mock_problem+".out")
        for line in INPUT:
            log = log+line
        INPUT.close()
        return [0,log]


