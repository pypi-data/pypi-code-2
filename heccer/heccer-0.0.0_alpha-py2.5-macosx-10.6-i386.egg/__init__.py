"""!
@package heccer

The heccer python module provides an abstraction over the
heccer data structures and their accompanying functions.
"""

__author__ = 'Mando Rodriguez'
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__status__ = "Development"

# System imports
import os
import pdb
import sys

# User imports
from __cbi__ import PackageInfo
import errors

try:

    import heccer_base

except ImportError, e:
    sys.exit("Could not import compiled SWIG heccer_base library: %s" % e)


_package_info = PackageInfo()



def GetVersion():

    return _package_info.GetVersion()



#************************* Heccer Mathcomponent constants **************************
#
# Moved these here so that these constants can be accessible from the top level 
# import of the heccer module.
#
MATH_TYPE_ChannelConc = heccer_base.MATH_TYPE_ChannelConc 
MATH_TYPE_ChannelActConc = heccer_base.MATH_TYPE_ChannelActConc
MATH_TYPE_ChannelActInact = heccer_base.MATH_TYPE_ChannelActInact
MATH_TYPE_ChannelPersistentSteadyStateDualTau = heccer_base.MATH_TYPE_ChannelPersistentSteadyStateDualTau
MATH_TYPE_ChannelPersistentSteadyStateTau = heccer_base.MATH_TYPE_ChannelPersistentSteadyStateTau
MATH_TYPE_ChannelSpringMass = heccer_base.MATH_TYPE_ChannelSpringMass
MATH_TYPE_ChannelSteadyStateSteppedTau = heccer_base.MATH_TYPE_ChannelSteadyStateSteppedTau 
MATH_TYPE_Compartment = heccer_base.MATH_TYPE_Compartment 
MATH_TYPE_ExponentialDecay = heccer_base.MATH_TYPE_ExponentialDecay 
MATH_TYPE_GHK = heccer_base.MATH_TYPE_GHK 
MATH_TYPE_InternalNernst = heccer_base.MATH_TYPE_InternalNernst 
MATH_TYPE_MGBlocker = heccer_base.MATH_TYPE_MGBlocker 
MATH_TYPE_SpikeGenerator = heccer_base.MATH_TYPE_SpikeGenerator
MATH_TYPE_Concentration = heccer_base.MATH_TYPE_Concentration 
MATH_TYPE_GateConcept = heccer_base.MATH_TYPE_GateConcept 
MATH_TYPE_CallOut_flag = heccer_base.MATH_TYPE_CallOut_flag
MATH_TYPE_CallOut_conductance_current = heccer_base.MATH_TYPE_CallOut_conductance_current

#********************* End Heccer Mathcomponent constants **************************






#************************* Start HeccerOptions **************************
class HeccerOptions(heccer_base.HeccerOptions):

    def __init__(self, options=0, corrections=0, 
                 interval_set=0, interval_start=-0.1, interval_end=0.05,
                 activator_set=0,
                 concentration_gate_start=4e-05, concentration_gate_end=0.29999999999999999,
                 interval_entries=3000, small_table_size=149):

        heccer_base.HeccerOptions.__init__(self)

        self.SetOptions(options)
        self.SetCorrections(corrections)
        self.SetInterval(interval_set)
        self.SetInternalStart(interval_start)
        self.SetInternalEnd(interval_end)
        self.SetActivator(activator_set)
        self.SetConcentrationGateStart(concentration_gate_start)
        self.SetConcentrationGateEnd(concentration_gate_end)
        self.SetIntervalEntries(interval_entries)
        self.SetSmallTableSize(small_table_size)
        

#---------------------------------------------------------------------------

    def __str__(self):

        return "Heccer Options:\n \
 - Options: %d\n \
 - Corrections: %d\n \
 - Interval Set: %d\n \
 - Interval Start: %f\n \
 - Interval End: %f\n \
 - Activator Set: %d\n \
 - Concentration Gate Start: %f\n \
 - Concentration Gate End: %f\n \
 - Interval Entries: %d\n \
 - Small Table Size: %d\n" % (self.iOptions, self.iCorrections,
        self.iIntervalSet, self.dIntervalStart, self.dIntervalEnd,
        self.iActivatorSet, self.dConcentrationGateStart,
        self.dConcentrationGateEnd, self.iIntervalEntries,
        self.iSmallTableSize) 
    
#---------------------------------------------------------------------------

    def SetOptions(self, options):
 
        self.iOptions = options
        
#---------------------------------------------------------------------------

    def SetCorrections(self, corrections):

        self.iCorrections = corrections

#---------------------------------------------------------------------------

    def SetInterval(self, interval_set):

        self.iIntervalSet = interval_set

#---------------------------------------------------------------------------

    def SetInternalStart(self, interval_start):

        self.dIntervalStart = interval_start

#---------------------------------------------------------------------------

    def SetInternalEnd(self, interval_end):

        self.dIntervalEnd = interval_end

#---------------------------------------------------------------------------

    def SetActivator(self, activator_set):

        self.iActivatorSet = activator_set

#---------------------------------------------------------------------------

    def SetConcentrationGateStart(self, concentration_gate_start):

        self.dConcentrationGateStart = concentration_gate_start

#---------------------------------------------------------------------------

    def SetConcentrationGateEnd(self, concentration_gate_end):

        self.dConcentrationGateEnd = concentration_gate_end

#---------------------------------------------------------------------------

    def SetIntervalEntries(self, interval_end):

        self.iIntervalEntries = interval_end

#---------------------------------------------------------------------------

    def SetSmallTableSize(self, small_table_size):

        self.iSmallTableSize = small_table_size
        

#************************* End HeccerOptions ****************************




#************************* Begin Heccer **************************
class Heccer:

    """!
    @class Heccer

    The Heccer class manages a heccer solver object and its options.

    """

#---------------------------------------------------------------------------

    def __init__(self, name="Untitled", model=None,
                 pts=None, ped=None,
                 peq=None, iOptions=None, dStep=None,
                 pinter=None, filename=None):
        """!
        @brief Constructor
        @param name The identifier for this Heccer
        @param pts Pointer to a translation service
        @param ped Pointer to an event queuer object
        @param iOptions
        @param dStep Step size value
        @param pinter A pointer to an intermediary
        @param model A pointer to a model container
        """

        self._options_core = None

        self._compiled_p1 = False
        self._compiled_p2 = False
        self._compiled_p3 = False

        self._model_source = model

        self._is_constructed = False


        # If we have a filename then we load from a file
        if filename is not None:

            if os.path.isfile(filename):

                self._heccer_core = heccer_base.HeccerFromFile(filename)

        elif pinter is not None:

            self._heccer_core = heccer_base.HeccerNewP2(name, pinter)

            self._is_constructed = True

            self._compiled_p1 = True


        # If options and step is given then we load via P1
        elif iOptions is not None and dStep is not None:

            self._heccer_core = heccer_base.HeccerNewP1(name, pts, ped, peq, iOptions, dStep)

        else:
            # without options and step we load via New
            
            self._heccer_core = heccer_base.HeccerNew(name, pts, ped, peq)


        # If no heccer options are present then we create one.
        if self._heccer_core.ho is not None:
    
            self._options_core = self._heccer_core.ho

        else:

            self._options_core = heccer_base.HeccerOptions()
        


#---------------------------------------------------------------------------

    def New(cls, name, pts, ped, peq):
        """!
        @brief Factory Method
        @param name Name for this heccer object
        @param pts Pointer to a translation service
        @param ped Pointer to an event queuer object
        
        """
        obj = cls(name=name, pts=pts, ped=ped, peq=peq)
        
        return obj        

#---------------------------------------------------------------------------

    def NewP1(cls, name , pts, ped, peq, iOptions, dStep):
        """!
        @brief Factory Method
        @param name Name for this heccer object
        @param pts Pointer to a translation service
        @param ped Pointer to an event distributor
        @param iOptions
        @param dStep Step size value
        """
        obj = cls(name=name, pts=pts, ped=ped, iOptions=iOptions, dStep=dStep)

        return obj

#---------------------------------------------------------------------------

    def NewP2(cls, name, pinter):
        """!
        @brief Factory Method
        """
        obj = cls(name=name, pinter=pinter)

        return obj

#---------------------------------------------------------------------------

    def NewFromFile(cls, filename):
        """!
        @brief Factory Method
        @param pc 
        """
        obj = cls(filename=filename)

        return obj


#---------------------------------------------------------------------------

    def SetModel(self, model_source):
        """

        """
        self._model_source = model_source

#---------------------------------------------------------------------------

    def Construct(self, model=None):
        """
        @brief Constructs heccer from the options
        """
        if self.GetCore() is not None:

            heccer = self.GetCore()
            
        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()



        if self.GetOptions() is not None:

            options = self.GetOptions()

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


        # Here we connect the model to heccer
        model_source = None

        if model is not None:

            try:

                model_source = model.GetCore()

            except TypeError:
                
                model_source = model

        elif self._model_source is not None:

            try:
                
                model_source = self._model_source.GetCore()

            except TypeError:

                model_source = self._model_source

        else:
            
            from errors import HeccerOptionsError

            raise HeccerOptionsError("Model not found, cannot construct a Heccer")

        # Probably need to check allow options to be passed to the next two
        # args

        model_name = heccer.pcName

        result = heccer_base.HeccerConstruct( heccer,
                                     model_source,
                                     model_name,
                                     None,
                                     None
                                     )

        if result == 1:

            self._is_constructed = True
            
        return result

#---------------------------------------------------------------------------

    def IsConstructed(self):

        return self._is_constructed

#---------------------------------------------------------------------------

    def GetCore(self):
        """!
        @brief Returns the internal raw heccer struct
        """
        return self._heccer_core


#---------------------------------------------------------------------------

    def SetCore(self, hecc):
        """!
        @brief Sets the core heccer to the value passed in hecc
        """
        self._heccer_core = hecc

#---------------------------------------------------------------------------

    def GetOptions(self):
        """!

        """
        return self._options_core


#---------------------------------------------------------------------------

    def SetOptions(self, ho):
        """!
        @brief 
        """

        if isinstance(ho, heccer_base.HeccerOptions):

            self._options_core = ho

        elif isinstance(ho, dict):

            pass


#---------------------------------------------------------------------------

    def GetName(self):
        """!
        @brief 
        """
        if self.GetCore() is not None:
            
            return self.GetCore().pcName

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

#---------------------------------------------------------------------------

    def SetName(self, name):
        """!
        @brief 
        """
        if self.GetCore() is not None:
            
            self.GetCore().pcName = name

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


#---------------------------------------------------------------------------

    def GetErrorCount(self):
        """!
        @brief 
        """
        if self.GetCore() is not None:
            
            return self.GetCore().iErrorCount

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


#---------------------------------------------------------------------------

    def GetStatus(self):
        """!
        @brief 
        """
        if self.GetCore() is not None:
            
            return self.GetCore().iStatus

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()
        

#---------------------------------------------------------------------------

    def GetAddress(self, path, field):
        """!
        @brief Returns the Heccer Address variable
        """
        address = None
        
        if self.GetCore() is None:


            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

        elif self._model_source is None:

            from errors import HeccerAddressError
            
            raise HeccerAddressError(path, field)

        else:

            serial = self._model_source.GetSerial(path)

            # check serial value, exception?
            
            address = heccer_base.HeccerAddressVariable(self.GetCore(),
                                                        serial,
                                                        field)

            if address == None:

                from errors import HeccerAddressError
                
                raise HeccerAddressError(serial, field)
        
        return address


#---------------------------------------------------------------------------

    def SetParameter(self, path, field, value):
        """!
        @brief Returns the Heccer Address variable
        """
        address = None
        
        if self.GetCore() is None:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

        elif self._model_source is None:

            from errors import HeccerAddressError
            
            raise HeccerAddressError(path, field)

        else:

            serial = self._model_source.GetSerial(path)

            result_msg = heccer_base.HeccerAddressableSet(self.GetCore(), serial,
                                                          field, value)
            if not result_msg is None:

                raise Exception(result_msg)
            

            return True
        
#---------------------------------------------------------------------------

    def GetParameter(self, path, field):
        """!
        @brief Returns the Heccer Address variable
        """
        address = None
        
        if self.GetCore() is None:


            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

        elif self._model_source is None:

            from errors import HeccerAddressError
            
            raise HeccerAddressError(path, field)

        else:

            serial = self._model_source.GetSerial(path)


            value = heccer_base.HeccerAddressGetValue(self.GetCore(), serial, field)
        
        return value


#---------------------------------------------------------------------------

    def GetCompartmentAddress(self, intermediary=-1, field="Vm"):

        """!
        @brief Returns the Heccer Address variable
        """
        address = None
        
        if self.GetCore() is None:


            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


        else:


            if intermediary == -1:

                raise Exception("Invalid intermediary index '%d'" % intermediary)

            serial = -1
            
            if not isinstance(intermediary, int):

                serial = self._model_source.GetSerial(intermediary)

            else:

                serial = intermediary
            
            address = heccer_base.HeccerAddressCompartmentVariable(self.GetCore(),
                                                        serial,
                                                        field)

            if address == None:

                from errors import HeccerAddressError
                
                raise HeccerAddressError(str(intermediary), field)
        
        return address
    
#---------------------------------------------------------------------------

    def SetIntervalStart(self, dstart):

        if self.GetOptions() is not None:

            self.GetOptions().dIntervalStart = dstart

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#---------------------------------------------------------------------------  


    def GetIntervalStart(self):

        if self.GetOptions() is not None:

            return self.GetOptions().dIntervalStart

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")

#---------------------------------------------------------------------------




    def SetSmallTableSize(self, size):

        if self.GetOptions() is not None:

            self.GetOptions().iSmallTableSize = size

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")

#---------------------------------------------------------------------------  

    def SetIntervalEntries(self, entries):

        if self.GetOptions() is not None:

            self.GetOptions().iIntervalEntries = entries

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")

#---------------------------------------------------------------------------  

    def GetIntervalEntries(self):

        if self.GetOptions() is not None:

            return self.GetOptions().iIntervalEntries

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")
        
#---------------------------------------------------------------------------  



    def SetIntervalEnd(self, dend):

        if self.GetOptions() is not None:

            self.GetOptions().dIntervalEnd = dend

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#---------------------------------------------------------------------------

    def GetIntervalEnd(self):

        if self.GetOptions() is not None:

            return self.GetOptions().dIntervalEnd

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#--------------------------------------------------------------------------- 

    def IsActivatorSet(self):

        
        if self.GetOptions() is not None:

            value = self.GetOptions().iActivatorSet

            if value != 0:

                return True

            else:

                return False

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#---------------------------------------------------------------------------  

    def SetConcentrationGateStart(self, dconc):

        if self.GetOptions() is not None:

            self.GetOptions().dConcentrationGateStart = dconc

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#---------------------------------------------------------------------------  

    def GetConcentrationGateStart(self):

        if self.GetOptions() is not None:

            return self.GetOptions().dConcentrationGateStart

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")

#---------------------------------------------------------------------------  

    def SetConcentrationGateEnd(self, dconc):

        if self.GetOptions() is not None:

            self.GetOptions().dConcentrationGateEnd = dconc

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")

#---------------------------------------------------------------------------  

    def GetConcentrationGateEnd(self):

        if self.GetOptions() is not None:

            return self.GetOptions().dConcentrationGateEnd

        else:

            from errors import HeccerOptionsError

            raise HeccerOptionsError("Heccer Options are not allocated")


#---------------------------------------------------------------------------   

    def Initiate(self):
        """!
        @brief 
        """
        if self.GetCore() is not None:

            heccer_base.HeccerInitiate(self.GetCore())

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError("Can't initiate, Heccer not allocated")


#--------------------------------------------------------------------------- 

    def Dump(self, file, selection):
        """!

        """
        my_file = None
        
        if self.GetCore() is not None:

            if file == 0:

                my_file = None
                
            heccer_base.HeccerDump(self.GetCore(), my_file, selection)

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

#---------------------------------------------------------------------------

    def DumpV(self):
        """!

        """
        if self.GetCore() is not None:

            heccer_base.HeccerDumpV(self.GetCore())

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()   

#---------------------------------------------------------------------------         

    def WriteToFile(self, filename):
        """!
        @brief Writes out heccer to a file
        """
        if self.GetCore() is not None:

            heccer_base.HeccerWriteToFile(self.GetCore(), filename)

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()



#---------------------------------------------------------------------------

    def Step(self, time):
        """!
        @brief
        """

        if self.GetCore() is not None:

            return heccer_base.HeccerHeccs(self.GetCore(), time)

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

#---------------------------------------------------------------------------

    def Advance(self,time):
        """!
        @brief
        @sa Step
        """
        return self.Step(time)

#---------------------------------------------------------------------------

    def CanCompile(self):
        """!
        @brief Tests to see if we can compile this heccer 
        """
        result = 0
        
        if self.GetCore() is not None:
            
            result = heccer_base.HeccerCanCompile(self.GetCore())

        if result == 0:

            return False
        
        else:

            return True
    
#---------------------------------------------------------------------------

    def CompileAll(self):
        """!
        @brief This compiles the solver for the Heccer core
        """

        heccer_core = self.GetCore()

        if heccer_core is not None:

            if not self.IsConstructed():

                self.Construct()
            
            self.CompileP1()
            self.CompileP2()
            self.CompileP3()

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

#---------------------------------------------------------------------------

    def CompileP1(self):
        """!
        @brief This compiles the solver for the Heccer core

        Compile level 1 primarily deals with using a heccer
        translation service to convert compartments into
        an intermeidate format.
        """

        if self.GetCore() is not None:

            if self._compiled_p1 is False:

                if self._heccer_core.pts is None:

                    return
                    #raise errors.HeccerCompileError("No Heccer translation service present, can't construct an intermediary from the model")
                
                heccer_base.HeccerCompileP1(self.GetCore())

                self._compiled_p1 = True

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


#---------------------------------------------------------------------------

    def CompileP2(self):
        """!
        @brief This compiles the solver for the Heccer core
        """

        if self.GetCore() is not None:

            if self._compiled_p2 is False:
                
                heccer_base.HeccerCompileP2(self.GetCore())

                self._compiled_p2 = True

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


#---------------------------------------------------------------------------

    def CompileP3(self):
        """!
        @brief This compiles the solver for the Heccer core
        """

        if self.GetCore() is not None:

            if self._compiled_p3 is False:
                
                heccer_base.HeccerCompileP3(self.GetCore())

                self._compiled_p3 = True

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()

        
#---------------------------------------------------------------------------

    def Finish(self):
        """!
        @brief Completes the process and closes the solver
        """
        pass

#---------------------------------------------------------------------------

    def SetTimeStep(self, dt):
        """!
        @brief 
        """
        if self.GetCore() is not None:
        
            self.GetCore().dStep = dt

        else:

            from errors import HeccerNotAllocatedError
        
            raise HeccerNotAllocatedError()
    
#---------------------------------------------------------------------------

    def GetTimeStep(self):

        if self.GetCore() is not None:
        
            return self.GetCore().dStep 

        else:

            from errors import HeccerNotAllocatedError

            raise HeccerNotAllocatedError()


        
#************************* End Heccer **************************



        

#************************* Start Intermediary **************************

class Intermediary(heccer_base.Intermediary):
    """!
    @class Intermediary
    @brief Abstraction to the Intermediary base class

    This object inherits the Intermediary data class
    from the heccer base class and makes it accessible
    to the top level API. Methods for converting python
    lists to C pointers are provided.
    """


    def __init__(self, compartments=None, comp2mech=None):

        heccer_base.Intermediary.__init__(self)

        if compartments is not None:
            
            self.SetCompartments(compartments)

        if comp2mech is not None:

            self.SetComp2Mech(comp2mech)

        else:
            
            # Create a generic compartment to mechanism array
            
            comp_len = len(compartments)
            
            c2m = [0] * comp_len

            c2m.append(-1)
 
            self.SetComp2Mech(c2m)


#---------------------------------------------------------------------------

    def SetCompartments(self, comps):
        """!
        @brief Sets a python list into a C array
        """

        if comps is None:

            return

        if self.pcomp is not None:
        
            heccer_base.delete_CompartmentArray(self.pcomp)
            
        if isinstance(comps, list):
            
            num_comps = len(comps)
            
            self.pcomp = heccer_base.new_CompartmentArray(num_comps)

            
            for index, c in enumerate(comps):

                try:
                    
                    c.iParent = index - 1

                except AttributeError, e:

                    raise Exception("Can't construct Heccer Intermediary, Improper compartment at index %d" % index)
                
                heccer_base.CompartmentArray_setitem(self.pcomp, index, c)

            self.SetNumCompartments(num_comps)
            
        else:

            # If it's not a list then just set the value

            self.pcomp = heccer_base.new_CompartmentArray(1)

            heccer_base.CompartmentArray_setitem(self.pcomp, 0, comps)

            self.SetNumCompartments(1)


#---------------------------------------------------------------------------

    def GetCompartment(self, index):
        """!
        @brief 
        """

        c = heccer_base.CompartmentArray_getitem(self.pcomp,index)

        return c


#---------------------------------------------------------------------------

    def SetNumCompartments(self, ncomp):

        self.iCompartments = ncomp
        

#---------------------------------------------------------------------------

    def SetComp2Mech(self, c2m):

        if self.piC2m is not None:

            heccer_base.delete_IntArray(self.piC2m)

        size = 0
        
        if isinstance(c2m, list):

            size = len(c2m)

            self.piC2m = heccer_base.new_IntArray(size)

            for index, c in enumerate(c2m):

                heccer_base.IntArray_setitem(self.piC2m, index, c)

        else:

            size = 1

            self.piC2m = heccer_base.new_IntArray(size)

            heccer_base.IntArray_setitem(self.piC2m, 0, c2m)


#************************* End Intermediary *****************************




#************************* Start Compartment **************************
class Compartment(heccer_base.Compartment):
    """!
    @class Compartment
    @brief A compartment object

    This object inherits the Compartment data
    class from the heccer base and makes it accessible
    from the top level.
    """
    def __init__(self):
        """!
        @brief Constructor
        """
        heccer_base.Compartment.__init__(self)

        self.SetMathType(MATH_TYPE_Compartment)

#---------------------------------------------------------------------------

    def SetMathType(self, itype):
        """!
        @brief Sets the type for this math object
        """
        self.mc.iType = itype

#************************* End Compartment ****************************
