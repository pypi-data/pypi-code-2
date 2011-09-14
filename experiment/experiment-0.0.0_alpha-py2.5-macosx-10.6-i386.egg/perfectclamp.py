"""

The perfect clamp module provides an abstraction
that encapsulates all of the complex operations of
the perfectclamp C code.
"""
import os
import pdb
import sys

try:

    import perfectclamp_base

except ImportError, e:
    sys.exit("Could not import compiled SWIG pulsegen_base library: %s" % e)


from perfectclamp_base import PerfectClampAddVariable
from perfectclamp_base import PerfectClampFinish
from perfectclamp_base import PerfectClampInitiate
from perfectclamp_base import PerfectClampNew
from perfectclamp_base import PerfectClampSetFields
from perfectclamp_base import PerfectClampSingleStep

from perfectclamp_base import new_pdouble
from perfectclamp_base import copy_pdouble
from perfectclamp_base import delete_pdouble
from perfectclamp_base import pdouble_assign
from perfectclamp_base import pdouble_value

__author__ = 'Mando Rodriguez'
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__status__ = "Development"

class PerfectClamp:


#---------------------------------------------------------------------------

    def __init__(self, name):

        self.pc = PerfectClampNew(name)

        if self.pc is None:

            raise Exception("Error: Can't create PulseGen '%s'" % name)

        self.name = name
        
        self.initiated = False

        # this will be the solved variable
        self.voltage = sys.maxint

        # exception?


#---------------------------------------------------------------------------

    def GetName(self):
        """
        @brief Returns the perfect clamps name
        """
        return self.name
        

#---------------------------------------------------------------------------

    def SetCommandVoltage(self,command):

        self.pc.dCommand = command


#---------------------------------------------------------------------------

    def GetCommandVoltage(self):

        return self.pc.dCommand


#---------------------------------------------------------------------------

    def GetVoltage(self):

        return pdouble_value(self.pc.pdVoltage)


#---------------------------------------------------------------------------

    def SetFields(self,command,filename):

        if not os.path.exists(filename):

            raise Exception("Command file %s does not exist" % filename)
            
        result = PerfectClampSetFields(self.pc,
                                       command,
                                       filename)
        # extra error checking?
        return result


#---------------------------------------------------------------------------

    def Step(self,time):

        # error cheking?
        result = PerfectClampSingleStep(self.pc,time)

        return result

#---------------------------------------------------------------------------
    
    def Finish(self):

        result = PerfectClampFinish(self.pc)

        return result

#---------------------------------------------------------------------------

    def Initialize(self):

        if not self.initiated:
            
            result = PerfectClampInitiate(self.pc)

            if result == 0:

                raise Exception("Can't initialize PerfectClamp '%s'" % self.GetName())

        return result


#---------------------------------------------------------------------------

    def AddVariable(self,voltage):
        """!
        @brief Add a solved variable.
        """
        
        result = PerfectClampAddVariable(self.pc,voltage)

        return result

#---------------------------------------------------------------------------

    def AddInput(self,voltage):
        """!
        @brief Add a solved variable.
        """
        
        return self.AddVariable(voltage)

#---------------------------------------------------------------------------
