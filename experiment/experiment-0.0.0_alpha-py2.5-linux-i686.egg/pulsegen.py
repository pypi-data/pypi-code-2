"""!
This is the module used to create a pulsegen python object
from the swig bindings.
"""
import ctypes
import os
import sys
import pdb


try:

    import pulsegen_base

except ImportError, e:
    sys.exit("Could not import compiled SWIG pulsegen_base library: %s", e)

from pulsegen_base import simobj_PulseGen
from pulsegen_base import PulseGenNew
from pulsegen_base import PulseGenFinish
from pulsegen_base import PulseGenAddInput
from pulsegen_base import PulseGenAddVariable
from pulsegen_base import PulseGenReset
from pulsegen_base import PulseGenSingleStep
from pulsegen_base import PulseGenSetFields

from pulsegen_base import new_pdouble
from pulsegen_base import copy_pdouble
from pulsegen_base import delete_pdouble
from pulsegen_base import pdouble_assign
from pulsegen_base import pdouble_value

#importing our constants.
from pulsegen_base import FREE_RUN
from pulsegen_base import EXT_TRIG
from pulsegen_base import EXT_GATE

FREE_RUN = pulsegen_base.FREE_RUN
EXT_TRIG = pulsegen_base.EXT_TRIG
EXT_GATE = pulsegen_base.EXT_GATE


class PulseGen:

    def __init__(self,name="Unnamed PulseGen",
                 level1=0, width1=0, delay1=0,
                 level2=0, width2=0, delay2=0,
                 base_level=0, trigger_mode=0):

        self.spg = PulseGenNew(name)

        PulseGenSetFields(self.spg,
                          level1,width1,delay1,
                          level2,width2,delay2,
                          base_level,trigger_mode)

    def __str__(self):

        string = "---\n \
 - Name: %s\n \
 - Level1: %s\n \
 - Width1: %s\n \
 - Delay1: %s\n \
 - Level2: %s\n \
 - Width2: %s\n \
 - Delay2: %s\n \
 - BaseLevel: %s\n \
 - TriggerMode: %s\n" % (spg.pcName,
 spg.dLevel1, spg.dWidth1, spg.dDelay1,
 spg.dLevel2, spg.dWidth2, spg.dDelay2,
 spg.dBaseLevel, spg.iTriggerMode)

        return string
        
    def SetName(self,name):

        self.spg.pcName = name

    def GetName(self):

        return self.spg.pcName

    def SetLevel1(self,level1):

        self.spg.dLevel1 = level1

    def GetLevel1(self):

        return self.spg.dLevel1

    def SetWidth1(self,width1):

        self.spg.dWidth1 = width1

    def GetWidth1(self):

        return self.spg.dWidth1

    def SetDelay1(self,delay1):

        self.spg.dDelay1 = delay1

    def GetDelay1(self):

        return self.spg.dDelay1

    def SetLevel2(self,level2):

        self.spg.dLevel2 = level2

    def GetLevel2(self):

        return self.spg.dLevel2

    def SetWidth2(self,width2):

        self.spg.dWidth2 = width2

    def GetWidth2(self):

        return self.spg.dWidth2

    def SetDelay2(self,delay2):

        self.spg.dDelay2 = delay2

    def GetDelay2(self):

        return self.spg.dDelay2

    def SetBaseLevel(self,base_level):

        self.spg.dBaseLevel = base_level

    def GetBaseLevel(self):

        return self.spg.dBaseLevel

    def SetTriggerMode(self,trigger_mode):

        self.spg.iTriggerMode = trigger_mode

    def GetTriggerMode(self):

        return self.spg.iTriggerMode

    def GetOutput(self):

        if self.spg.pdPulseOut == None:

            return None
        
        return pdouble_value(self.spg.pdPulseOut)

    def SingleStep(self,time=0.0):

        PulseGenSingleStep(self.spg,time)

    def Reset(self):

        PulseGenReset(self.spg)

    def Finish(self):

        val = PulseGenFinish(self.spg)

        if val == 0:

            return False

        else:

            return True

    def AddInput(self,input):

        PulseGenAddInput(self.spg,input)



    def AddVariable(self,output):

        PulseGenAddVariable(self.spg,output)
       
        

