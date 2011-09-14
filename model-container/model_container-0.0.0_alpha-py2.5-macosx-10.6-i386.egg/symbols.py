"""!
@file symbols.py 


File contains the implentation for symbols in the model
container.
"""
import pdb
import errors

try:

    import model_container_base as nmc_base

except ImportError, e:
    sys.exit("Could not import compiled SWIG model container base library: %s", e)





#*************************** Start Symbol **************************


class Symbol:
    """!
    @class Symbol An abstract class used for all symbols.

    A base object for a symbol in the model container. Object contains
    the only methods needed to  perform basic symbol manipulation such
    as adding parameters.
    Can be inherited by more complex objects for more complex symbols.
    Should note that currently in Python there is no difference between
    an Abstract class and a concrete class when they are user defined.
    """

#---------------------------------------------------------------------------

    def __init__(self, path=None, model=None):
        """!
        @brief Constructor
        """

        if path is None:

            raise errors.SymbolError("Cannot create symbol, no path given")
        
        self._path = path

        self._nmc_core = model

#---------------------------------------------------------------------------

    def GetPath(self):
        """!
        @brief Returns the saved pathname in a python string
        @returns self._path The class variable that holds the path for the symbol
        """
        return self._path

#---------------------------------------------------------------------------

    def GetCore(self):
        """!
        @brief Returns the core object in the Symbol abstraction

        Returns the Hsolve list element pointer that is managed by
        the object. Replaces the previous \"backend_object\",hopefully
        is more clear :)
        """
        return self._core

#---------------------------------------------------------------------------

    def InsertChild(self, child):
        """!
        @brief Inserts the child object under the core_symbol

 
        """
        core_symbol = self.GetSymbol()

        try:

            core_child = child.GetSymbol()

        except AttributeError:

            # if it is not a high level object symbol
            # we assume it is a core C struct symbol
            core_child = child


        result = nmc_base.SymbolAddChild(core_symbol,core_child)

        return result

#---------------------------------------------------------------------------

    def ImportChild(self, path):
        """!
        @brief Imports a child into the current symbol from the given path
        """
        if self._nmc_core is None:

            raise errors.ImportChildError("No model container defined for symbol '%s', can't perform child import for '%s'" % (self._path, path))

        import re

        p = re.split("::", path)

        if len(p) != 2:

            raise errors.ImportChildError("Error importing '%s' into symbol '%s'" %
                                          path, self._path)

        filename = p[0]
        component = p[1]

        result = nmc_base.NeurospacesRead(self._nmc_core, 2, [ "python", filename ] )

        if result < 1:

            raise errors.ImportChildError("Error importing '%s' into symbol '%s'" %
                                          path, self._path)

        context = nmc_base.PidinStackParse(component)
        
        top = nmc_base.PidinStackLookupTopSymbol(context)
#        pdb.set_trace()



        self.InsertChild(top)
        
        # check result 

#---------------------------------------------------------------------------

    def GetParameter(self, parameter):
        """!
        @brief Returns a parameter value from the current symbol.
        @param parameter The parameter value to look up
        """

        path = self.GetPath()
        
        ppist = nmc_base.PidinStackParse(path)

        phsle = self.GetSymbol()
                               
        if phsle is None:

            return None

        value = nmc_base.SymbolParameterResolveValue(phsle, ppist, parameter)

        return value

#---------------------------------------------------------------------------

    def SetParameter(self, parameter, value):
        """!
        @brief Sets a parameter for the symbol

        A \"smart\" method that will determine the value
        type and pass it to the appropriate model container
        parameter set method.
        """
        result = self.SetParameterDouble(parameter,value)

        # Exception if bad?
        
        return result


#---------------------------------------------------------------------------

    def SetParameters(self, parameters):
        """
        @brief Sets a set of parameters in a dictionary
        """

        try:

            items = parameters.items()
            
        except AttributeError:

            raise errors.ParameterError("Error Invalid dictionary: %s" % str(parameters))

        for key, value in parameters.iteritems():

            self.SetParameter(key, value)
            
#---------------------------------------------------------------------------


    def SetParameterDouble(self, parameter, value):
        """!
        @brief Sets a double parameter

        Should note that python does not use actual doubles but
        instead uses floats, so we check for a float value. Name is kept
        the same to ensure compatability with the model container code.
        """

        symbol = self.GetSymbol()
        
        result = nmc_base.SymbolSetParameterDouble(symbol, parameter, value)

        return result


#---------------------------------------------------------------------------

    def _CreateNameAndSymbol(self,path):
        """!
        @brief Creates a name and context
        @returns result A tuple with a name and symbol 

        An internal helper method that creates a name and symbol
        """

        context = nmc_base.PidinStackParse(path)
        
        name = nmc_base.PidinStackTop(context)

        # Here we pop and return the top symbol, which would now be the parent
        # symbol.
        
        nmc_base.PidinStackPop(context)
        
        top_symbol = nmc_base.PidinStackLookupTopSymbol(context)

        result = [name, top_symbol]
        
        return result


#*************************** End Symbol ****************************




#*************************** Start Segment ****************************

class Segment(Symbol):
    
    """!
    @class Segment An object for managing a Segment symbol in the model container
    
    """
    def __init__(self, path=None, model=None):
        """!
        @brief Constructor

        @param path The complete path to the Segment object.
        """
        Symbol.__init__(self, path, model)

        name, top_symbol = self._CreateNameAndSymbol(path)

        self._core = self.__AllocateSegment(name.pcIdentifier)

        # Make our current symbol a child of the parent

        if top_symbol is not None:
            
            nmc_base.SymbolAddChild(top_symbol, self.GetSymbol())
        

#---------------------------------------------------------------------------

    def GetSymbol(self):
        """!
        @brief Returns the core objects hsolve list element (symbol).

        """
        return self._core.segr.bio.ioh.iol.hsle


#---------------------------------------------------------------------------

    def SetInitialVm(self,value):
        """!
        @brief Sets the initial membrane potential
        @param value float value for the membrane potential

        Sets the parameter \"Vm_init\" in the segment symbol
        in the model container.
        """
        self.SetParameter("Vm_init",value)
        
#---------------------------------------------------------------------------

    def SetRm(self,value):
        """!
        @brief Sets the membrane resistance
        @param value A float value to set the membrane resistance
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"RM\"
        parameter in the model container.
        """
        self.SetParameter("RM",value)

#---------------------------------------------------------------------------

    def SetRa(self,value):
        """!
        @brief Sets the axial resistance
        @param value A float value to set the axial resistance
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"RA\"
        parameter in the model container.

        """
        self.SetParameter("RA",value)

#---------------------------------------------------------------------------

    def SetCm(self,value):
        """!
        @brief Sets the membrane capacitance
        @param value A float value to set the membrane capacitance
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"CM\"
        parameter in the model container.
        """
        self.SetParameter("CM",value)

#---------------------------------------------------------------------------

    def SetDia(self,value):
        """!
        @brief Sets the segment diameter
        @param value A float value to set the segment diameter
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"DIA\"
        parameter in the model container.
        """
        self.SetParameter("DIA",value)

#---------------------------------------------------------------------------

    def SetEleak(self,value):
        """!
        @brief Sets Eleak
        @param value A float value to set Eleak
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"ELEAK\"
        parameter in the model container.
        """
        self.SetParameter("ELEAK",value)

#---------------------------------------------------------------------------

    def SetLength(self,value):
        """!
        @brief Sets Segment Length
        @param value A float value to set the segment length
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"LENGTH\"
        parameter in the model container.
        """
        self.SetParameter("LENGTH",value)

#---------------------------------------------------------------------------

    def SetInject(self,value):
        """!
        @brief Sets the injection value
        @param value A float value to set the injection voltage
        @sa SetParameter

        Just a simple wrapper to SetParameter. Sets the \"INJECT\"
        parameter in the model container.
        """
        self.SetParameter("INJECT",value)

        
#---------------------------------------------------------------------------

    def __AllocateSegment(self,name):
        """!
        @brief Allocates and sets the name for a segment.

        Method is name mangled since it should never be called
        outside of initialization.
        """
        
        segment = nmc_base.SegmentCalloc()

        if not segment:

            raise Exception("Error allocating the Segment")

        idin = nmc_base.IdinCallocUnique(name)

        nmc_base.SymbolSetName(segment.segr.bio.ioh.iol.hsle, idin)
        
        return segment
        

# An alias
Compartment = Segment

#*************************** End Segment ****************************




#*************************** Start Cell ****************************

class Cell(Symbol):
    """
    @class Cell A class object for managing a Cell symbol
    @brief A class object for managing a Cell symbol

    
    """
    def __init__(self, path=None, model=None):


        """!
        @brief Constructor

        @param path The complete path to the Segment object.
        """
        Symbol.__init__(self, path, model)

        name, top_symbol = self._CreateNameAndSymbol(path)

        self._core = self.__AllocateCell(name.pcIdentifier)

        # Make our current symbol a child of the parent

        if top_symbol is not None:
            
            nmc_base.SymbolAddChild(top_symbol, self.GetSymbol())



#---------------------------------------------------------------------------

    def GetSymbol(self):
        """!
        @brief Returns the core objects hsolve list element (symbol).

        """
        return self._core.segr.bio.ioh.iol.hsle

#---------------------------------------------------------------------------

    def __AllocateCell(self, name):
        """!
        @brief Allocates and sets the name for a segment.

        Method is name mangled since it should never be called
        outside of initialization.
        """
        
        cell = nmc_base.CellCalloc()

        if not cell:

            raise Exception("Error allocating the Cell")

        idin =  nmc_base.IdinCallocUnique(name)

        nmc_base.SymbolSetName(cell.segr.bio.ioh.iol.hsle, idin)
        
        return cell



#*************************** End Cell ****************************






#     class Channel(Symbol):
#         "ModelContainer.Channel constructor"
#         def __init__(self, path):
#             [ name, top_symbol ] = prepare(path)
#             import Neurospaces
#             channel = Neurospaces.Channel(name.pcIdentifier)
#             if top_symbol == None:
#                 print "Error: top_symbol is None"
#             else:
#                 SwiggableNeurospaces.SymbolAddChild(top_symbol, channel.backend.bio.ioh.iol.hsle)
#             self.backend = channel
        
#         def parameter(self, name, value):
#             self.backend.parameter(name, value)

#     class GateKinetic(Symbol):
#         "ModelContainer.GateKinetic constructor"
#         def __init__(self, path):
#             [ name, top_symbol ] = prepare(path)
#             import Neurospaces
#             gk = Neurospaces.GateKinetic(name.pcIdentifier)
#             if top_symbol == None:
#                 print "Error: top_symbol is None"
#             else:
#                 SwiggableNeurospaces.SymbolAddChild(top_symbol, gk.backend.bio.ioh.iol.hsle)
#             self.backend = gk
        
#         def parameter(self, name, value):
#             self.backend.parameter(name, value)




# class ContourGroup(Symbol):
#     "ContourGroup class"
#     def __init__(self, name):
#         group = SwiggableNeurospaces.VContourCalloc()
#         SwiggableNeurospaces.SymbolSetName(group.vect.bio.ioh.iol.hsle, SwiggableNeurospaces.IdinCallocUnique(name))
#         self.backend = group

#     def backend_object(self):
#         return self.backend.vect.bio.ioh.iol.hsle

# class ContourPoint(Symbol):
#     "ContourPoint class"
#     def __init__(self, name):
#         point = SwiggableNeurospaces.ContourPointCalloc()
#         SwiggableNeurospaces.SymbolSetName(point.bio.ioh.iol.hsle, SwiggableNeurospaces.IdinCallocUnique(name))
#         self.backend = point

#     def backend_object(self):
#         return self.backend.bio.ioh.iol.hsle

# class EMContour(Symbol):
#     "EMContour class"
#     def __init__(self, name):
#         contour = SwiggableNeurospaces.EMContourCalloc()
#         SwiggableNeurospaces.SymbolSetName(contour.bio.ioh.iol.hsle, SwiggableNeurospaces.IdinCallocUnique(name))
#         self.backend = contour

#     def backend_object(self):
#         return self.backend.bio.ioh.iol.hsle

# class Channel(Symbol):
#     "Channel class"
#     def __init__(self, name):
#         channel = SwiggableNeurospaces.ChannelCalloc()
#         SwiggableNeurospaces.SymbolSetName(channel.bio.ioh.iol.hsle, SwiggableNeurospaces.IdinCallocUnique(name))
#         self.backend = channel

#     def backend_object(self):
#         return self.backend.bio.ioh.iol.hsle

#     def parameter(self, name, value):
#         SwiggableNeurospaces.SymbolSetParameterDouble(self.backend.bio.ioh.iol.hsle, name, value)

# class GateKinetic(Symbol):
#     "GateKinetic class"
#     def __init__(self, name):
#         gk = SwiggableNeurospaces.GateKineticCalloc()
#         SwiggableNeurospaces.SymbolSetName(gk.bio.ioh.iol.hsle, SwiggableNeurospaces.IdinCallocUnique(name))
#         self.backend = gk

#     def backend_object(self):
#         return self.backend.bio.ioh.iol.hsle

#     def parameter(self, name, value):
#         SwiggableNeurospaces.SymbolSetParameterDouble(self.backend.bio.ioh.iol.hsle, name, value)
