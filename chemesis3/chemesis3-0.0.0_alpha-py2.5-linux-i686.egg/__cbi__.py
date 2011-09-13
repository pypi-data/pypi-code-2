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
Chemesis3 is a GENESIS3 reimplementation of chemesis from GENESIS. Chemesis3 is a solver
used to model kinetic and biochemical reaction pathways for GENESIS3.
"""
__download_url__ = "http://repo-genesis3.cbi.utsa.edu"

class PackageInfo:
    
    def GetRevisionInfo(self):
# $Format: "        return \"${monotone_id}\""$
        return "40ac0a7a884b8f9a4d9a793c25dcf28ea8eb503a"

    def GetName(self):
# $Format: "        return \"${package}\""$
        return "chemesis3"

    def GetVersion(self):
# $Format: "        return \"${major}.${minor}.${micro}-${label}\""$
        return "0.0.0-alpha"

    def GetDependencies(self):
        """!
        @brief Provides a list of other CBI dependencies needed.
        """
        dependencies = []
        
        return dependencies
