#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
import string
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

this_test_file_directory = dirname(abspath(__file__))+os.sep

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

def filter_time_and_data_dirs(line):
    return "seconds" in line or line.startswith("Output file written to") or "filename" in line or "directory" in line or "file" in line

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
    def test_farmer_quadratic_cplex(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_cplex.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_cplex.out",this_test_file_directory+"farmer_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_gurobi(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_gurobi.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_gurobi.out",this_test_file_directory+"farmer_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_verbose_cplex(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_verbose_cplex.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver=cplex --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_verbose_cplex.out",this_test_file_directory+"farmer_quadratic_verbose_cplex.baseline", filter=filter_time_and_data_dirs)                

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_verbose_gurobi(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_verbose_gurobi.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver=gurobi --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_verbose_gurobi.out",this_test_file_directory+"farmer_quadratic_verbose_gurobi.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_with_rent_quadratic_cplex(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_rent_quadratic_cplex.out")
        farmer_examples_dir = pysp_examples_dir + "farmerWrent"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"        
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_rent_quadratic_cplex.out",this_test_file_directory+"farmer_with_rent_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_with_rent_quadratic_gurobi(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_rent_quadratic_gurobi.out")
        farmer_examples_dir = pysp_examples_dir + "farmerWrent"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"        
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_rent_quadratic_gurobi.out",this_test_file_directory+"farmer_with_rent_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)        
       
    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_cplex(self):
        if cplex_available:
            solver_string="cplex"
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_cplex.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_cplex.out",this_test_file_directory+"farmer_linearized_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_farmer_gurobi(self):
        if gurobi_available:
            solver_string="gurobi"
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_gurobi.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_gurobi.out",this_test_file_directory+"farmer_linearized_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_nodedata_cplex(self):
        if cplex_available:
            solver_string="cplex"
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_nodedata_cplex.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_nodedata_cplex.out",this_test_file_directory+"farmer_linearized_nodedata_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_farmer_nodedata_gurobi(self):
        if gurobi_available:
            solver_string="gurobi"
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_nodedata_gurobi.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"        
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_nodedata_gurobi.out",this_test_file_directory+"farmer_linearized_nodedata_gurobi.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_sizes3_cplex(self):

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_quadratic_cplex.out")

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
        coopr.pysp.phinit.main(args=args)                
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_cplex.out",this_test_file_directory+"sizes3_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_quadratic_sizes3_gurobi(self):

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_quadratic_gurobi.out")

        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"        
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=200"+ \
                    " --rho-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --scenario-solver-options=mip_tolerances_integrality=1e-7"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.cfg"+ \
                    " --ww-extension-suffixfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.suffixes"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)                
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_gurobi.out",this_test_file_directory+"sizes3_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_networkflow1ef10_cplex(self):

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_quadratic_cplex.out")

        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"        
        argstring = "runph --solver=cplex --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=100"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosetter1.0.cfg"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"wwph-immediatefixing.cfg"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)                
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_quadratic_cplex.out",this_test_file_directory+"networkflow1ef10_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_quadratic_networkflow1ef10_gurobi(self):

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_quadratic_gurobi.out")

        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"        
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=100"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosetter1.0.cfg"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"wwph-immediatefixing.cfg"
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)                
        pyutilib.misc.reset_redirect()
        self.cleanup()        
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_quadratic_gurobi.out",this_test_file_directory+"networkflow1ef10_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    def test_farmer_ef(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        ef_output_file = this_test_file_directory+"test_farmer_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef.out",this_test_file_directory+"farmer_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_ef.baseline.lp")

    def test_hydro_ef(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"hydro_ef.out")
        hydro_examples_dir = pysp_examples_dir + "hydro"
        model_dir = hydro_examples_dir + os.sep + "models"
        instance_dir = hydro_examples_dir + os.sep + "scenariodata"        
        ef_output_file = this_test_file_directory+"test_hydro_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"hydro_ef.out",this_test_file_directory+"hydro_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"hydro_ef.baseline.lp")

    def test_sizes3_ef(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_ef.out")
        sizes3_examples_dir = pysp_examples_dir + "sizes"
        model_dir = sizes3_examples_dir + os.sep + "models"
        instance_dir = sizes3_examples_dir + os.sep + "SIZES3"        
        ef_output_file = this_test_file_directory+"test_sizes3_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_ef.out",this_test_file_directory+"sizes3_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"sizes3_ef.baseline.lp.gz")

    def test_networkflow1ef10_ef(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_ef.out")
        networkflow1ef10_examples_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow1ef10_examples_dir + os.sep + "models"
        instance_dir = networkflow1ef10_examples_dir + os.sep + "1ef10"        
        ef_output_file = this_test_file_directory+"test_networkflow1ef10_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_ef.out",this_test_file_directory+"networkflow1ef10_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"networkflow1ef10_ef.baseline.lp.gz")

    def test_farmer_ef_cvar(self):
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_cvar.out")
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"        
        ef_output_file = this_test_file_directory+"test_farmercvar_ef.lp"
        argstring = "runef --verbose --generate-weighted-cvar --risk-alpha=0.90 --cvar-weight=0.0 --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)        
        pyutilib.misc.reset_redirect()
        self.cleanup()                
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_cvar.out",this_test_file_directory+"farmer_ef_cvar.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_ef_cvar.baseline.lp")

TestPH = unittest.category('nightly', 'performance')(TestPH)

if __name__ == "__main__":
    unittest.main()
