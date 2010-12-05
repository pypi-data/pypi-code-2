#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
import string
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

current_directory = dirname(abspath(__file__))+os.sep

pysp_examples_dir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep+"examples"+os.sep+"pysp"+os.sep

coopr_bin_dir = dirname(dirname(dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))))+os.sep+"bin"+os.sep

#
# Import the testing packages
#
import pyutilib.misc
import pyutilib.th as unittest
import pyutilib.subprocess
import coopr.pysp
import coopr.plugins.mip
import coopr.pysp.phinit
import coopr.pysp.ef_writer_script

def filter_time(line):
    return "seconds" in line or line.startswith("Data for")

cplex = None
cplex_available = False
try:
    cplex = coopr.plugins.mip.CPLEX(keepFiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False

glpk = None
glpk_available = False
try:
    glpk = coopr.plugins.mip.GLPK(keepFiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
except pyutilib.common.ApplicationError:
    glpk_available=False

#
# Define a testing class, using the unittest.TestCase class.
#

# @unittest.category('nightly')
class TestPH(unittest.TestCase):

    def cleanup(self):

        # IMPT: This step is key, as Python keys off the name of the module, not the location.
        #       So, different reference models in different directories won't be detected.
        #       If you don't do this, the symptom is a model that doesn't have the attributes
        #       that the data file expects.
        if "ReferenceModel" in sys.modules:
           del sys.modules["ReferenceModel"]

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_farmer(self):
        pyutilib.misc.setup_redirect(current_directory+"farmer_quadratic.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.run(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.failUnlessFileEqualsBaseline(current_directory+"farmer_quadratic.out",current_directory+"farmer_quadratic.baseline", filter=filter_time)
       
    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer(self):
        if cplex_available:
            solver_string="cplex"
        pyutilib.misc.setup_redirect(current_directory+"farmer_linearized.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.run(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.failUnlessFileEqualsBaseline(current_directory+"farmer_linearized.out",current_directory+"farmer_linearized.baseline", filter=filter_time)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_nodedata(self):
        if cplex_available:
            solver_string="cplex"
        pyutilib.misc.setup_redirect(current_directory+"farmer_linearized_nodedata.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.run(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.failUnlessFileEqualsBaseline(current_directory+"farmer_linearized_nodedata.out",current_directory+"farmer_linearized_nodedata.baseline", filter=filter_time)        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_sizes3(self):

        # Ignore this for now
        return
       
        pyutilib.misc.setup_redirect(current_directory+"sizes3_quadratic.out")

        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"        
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=200"+ \
                    " --rho-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --scenario-solver-options=mip_tolerances_integrality=1e-7"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.cfg"+ \
                    " --ww-extension-suffixfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.suffixes"
        args = string.split(argstring)
        coopr.pysp.phinit.run(args=args)                
        pyutilib.misc.reset_redirect()
        self.failUnlessFileEqualsBaseline(current_directory+"sizes3_quadratic.out",current_directory+"sizes3_quadratic.baseline", filter=filter_time)
        self.cleanup()        

    def test_farmer_ef(self):
        pyutilib.misc.setup_redirect(current_directory+"farmer_ef.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runef --verbose --output-file=farmer_ef.out --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.run(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.failUnlessFileEqualsBaseline(current_directory+"farmer_ef.out",current_directory+"farmer_ef.baseline", filter=filter_time)

    def test_farmer_ef_cvar(self):
        pyutilib.misc.setup_redirect(current_directory+"farmer_ef_cvar.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runef --verbose --output-file=farmer_ef_cvar.out --generate-weighted-cvar --risk-alpha=0.90 --cvar-weight=0.0 --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.run(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.failUnlessFileEqualsBaseline(current_directory+"farmer_ef_cvar.out",current_directory+"farmer_ef_cvar.baseline", filter=filter_time)

TestPH = unittest.category('nightly')(TestPH)


if __name__ == "__main__":
    unittest.main()
