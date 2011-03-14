#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
import string
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

this_test_directory = dirname(abspath(__file__))+os.sep

benders_example_dir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep+"examples"+os.sep+"pyomo"+os.sep+"benders"+os.sep

coopr_bin_dir = dirname(dirname(dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))))+os.sep+"bin"+os.sep

#
# Import the testing packages
#
import pyutilib.misc
import pyutilib.th as unittest
import pyutilib.subprocess
import coopr.plugins.mip

cplex = None
cplex_available = False
try:
    cplex = coopr.plugins.mip.CPLEX(keepFiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False

gurobi = None
gurobi_available = False
try:
    gurobi = coopr.plugins.mip.GUROBI(keepFiles=True)
    gurobi_available = (not gurobi.executable() is None) and gurobi.available(False)
except pyutilib.common.ApplicationError:
    gurobi_available=False

glpk = None
glpk_available = False
try:
    glpk = coopr.plugins.mip.GLPK(keepFiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
except pyutilib.common.ApplicationError:
    glpk_available=False

class TestBenders(unittest.TestCase):

    def cleanup(self):

        # IMPT: This step is key, as Python keys off the name of the module, not the location.
        #       So, different reference models in different directories won't be detected.
        #       If you don't do this, the symptom is a model that doesn't have the attributes
        #       that the data file expects.
        if "ReferenceModel" in sys.modules:
           del sys.modules["ReferenceModel"]

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_benders_cplex(self):
        pyutilib.misc.setup_redirect(this_test_directory+"benders_cplex.out")
        os.chdir(benders_example_dir)
        os.system("lbin python "+benders_example_dir+"runbenders")
        os.chdir(this_test_directory)        
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.failUnlessFileEqualsBaseline(this_test_directory+"benders_cplex.out",this_test_directory+"benders_cplex.baseline")

TestBenders = unittest.category('smoke')(TestBenders)

if __name__ == "__main__":
    unittest.main()
