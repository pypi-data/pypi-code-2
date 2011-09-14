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
The experiment module houses experimental protocols for use
in simulations in GENESIS 3. 
"""
__download_url__ = "http://repo-genesis3.cbi.utsa.edu"

class PackageInfo:
    
    def GetRevisionInfo(self):
# $Format: "        return \"${monotone_id}\""$
        return "b827606eacc9c544355df892a8244865898ab937"

    def GetName(self):
# $Format: "        return \"${package}\""$
        return "experiment"

    def GetVersion(self):
# $Format: "        return \"${major}.${minor}.${micro}-${label}\""$
        return "0.0.0-alpha"

    def GetDependencies(self):
        """!
        @brief Provides a list of other CBI dependencies needed.
        """
        dependencies = []
        
        return dependencies

