"""
@file __cbi__.py

This file provides data for a packages integration
into the CBI architecture.
"""

__author__ = "Mando Rodriguez"
__copyright__ = "Copyright 2010, The GENESIS Project"
__credits__ = ["Hugo Cornelis", "Dave Beeman"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Mando Rodriguez"
__email__ = "rodrigueza14@uthscsa.edu"
__status__ = "Development"
__url__ = "http://genesis-sim.org"
__description__ = """
The Model Container is used as an abstraction layer on top of a simulator and deals with biological entities and end-user concepts instead of mathematical equations. It provides a solver independent internal storage format for models that allows user independent optimizations of the numerical core. By containing the biological model, the Model Container makes the implementation of the numerical core independent of software implementation.
The Model Container API abstracts away all the mathematical and computational details of the simulator. Optimized to store large models in little memory it stores neuronal models in a fraction of the memory that would be used by conventional simulators and provides automatic partitioning of the model such that simulations can be run in parallel. From the modeler's perspective, the Model Container will be able to import and export NeuroML files to facilitate model exchange and ideas.
"""
__download_url__ = "http://repo-genesis3.cbi.utsa.edu"

class PackageInfo:
    
    def GetRevisionInfo(self):
# $Format: "        return \"${monotone_id}\""$
        return "c387d0fa6f794c217458406adefa206a5adaeca6"

    def GetName(self):
# $Format: "        return \"${package}\""$
        return "model-container"

    def GetVersion(self):
# $Format: "        return \"${major}.${minor}.${micro}-${label}\""$
        return "0.0.0-alpha"

    def GetDependencies(self):
        """!
        @brief Provides a list of other CBI dependencies needed.
        """
        dependencies = []
        
        return dependencies
