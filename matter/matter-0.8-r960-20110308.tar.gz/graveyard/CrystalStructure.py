import numpy
import  Matrix 
import  copy
import  LinearAlgebra
#import arrayfns
#from math import cos,sin
import math
import os

class CrystalStructure:  
    """Representation of Crystal Structure."""
    # Constructor of CrystalStructure.
    # Here one passes  the relevant parameter (see default list)

    def __init__(
        self,
        cellvectors=numpy.array( [ (1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0) ] ), 
        AtomNames=['a','b'],
        PositionsList=[numpy.array(  [ numpy.array((0.0,0.0,0.0))]    ), numpy.array( [numpy.array((0.5,0.5,0.5))]  )]
        ):
      
        self.cellvectors = cellvectors
        self.AtomNames  = AtomNames
        self.PositionsList = PositionsList
        self.atomlist=[]
        for i in range(0, len(AtomNames)):
            for j in range(0, len(PositionsList[i])):
                self.atomlist.append( (AtomNames[i],j ) )


    def __deepcopy__(self):
        res = CrystalStructure()
        res.cellvectors = numpy.array(self.cellvectors, copy=1)
        res.AtomNames  = copy.copy(self.AtomNames)
        res.PositionsList = copy.copy(self.PositionsList)
        for i in range(0, len(res.PositionsList)):
            res.PositionsList[i] = numpy.array(res.PositionsList[i],  copy=1 )
        return res

    def getCellVectors(self):
        return self.cellvectors

    def getAtomNames(self):
        return self.AtomNames

    def getPositionsList(self):
        return self.PositionsList

    def getAtomList(self):
        return self.atomlist
  
