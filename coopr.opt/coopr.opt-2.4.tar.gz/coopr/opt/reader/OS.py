#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Utility classes for dealing with the COIN-OR optimization
# services
#

import os
import sys
from xml.dom import minidom, Node
import xml
from pyutilib.enum import Enum
from pyutilib.misc import get_xml_text
from coopr.opt import SolutionStatus

#
# A class for reading/writing OSrL file
#
class OSrL(object):

    GeneralStatus = Enum('error', 'warning', 'success')
    SolutionStatus = Enum('unbounded', 'globallyOptimal', 'locallyOptimal', 
                        'optimal', 'bestSoFar', 'feasible', 'infeasible', 
                        'stoppedByLimit', 'unsure', 'error', 'other')

    class ResultHeader(object):
        def __init__(self):
            self.generalStatus=OSrL.GeneralStatus.error
            self.serviceURI=None
            self.serviceName=None
            self.instanceName=None
            self.time=None
            self.message=None
            self.jobID=None

        def _parse_xml(self, node):
            for child in node.childNodes:
              if child.nodeType == Node.ELEMENT_NODE:
                 if child.nodeName in ["generalStatus","serviceURI","serviceName","instanceName","time","message", "jobID"]:
                    setattr(self,child.nodeName, get_xml_text(child))

        def validate(self):
            if self.generalStatus not in OSrL.GeneralStatus:
               raise ValueError, "General status value '"+str(self.generalStatus)+"' is not in OSrL.GeneralStatus"

        #def __repr__(self):
            #return "OSrL ResultHeader"
            
        #__str__ = __repr__

        def write(self,ostream=None, prefix=""):
            if ostream is None:
               ostream = sys.stdout
            self.validate()
            os.write(ostream.fileno(), prefix)
            os.write(ostream.fileno(), "<ResultHeader>\n")
            #
            os.write(ostream.fileno(), prefix+"  <generalStatus>")
            os.write(ostream.fileno(), str(self.generalStatus))
            os.write(ostream.fileno(), "</generalStatus>\n")
            #
            if self.serviceURI is not None:
               os.write(ostream.fileno(), prefix+"  <serviceURI>"+str(self.serviceURI)+"</serviceURI>\n")
            #
            os.write(ostream.fileno(), prefix+"  <serviceName>")
            if self.serviceName is None:
               os.write(ostream.fileno(), "unknown")
            else:
               os.write(ostream.fileno(), str(self.serviceName))
            os.write(ostream.fileno(), "</serviceName>\n")
            #
            os.write(ostream.fileno(), prefix+"  <instanceName>")
            if self.instanceName is None:
               os.write(ostream.fileno(), "unknown")
            else:
               os.write(ostream.fileno(), str(self.instanceName))
            os.write(ostream.fileno(), "</instanceName>\n")
            #
            if self.time is not None:
               os.write(ostream.fileno(), prefix+"  <time>"+str(self.time)+"</time>\n")
            #
            if self.message is not None:
               os.write(ostream.fileno(), prefix+"  <message>"+str(self.message)+"</message>\n")
            #
            if self.jobID is not None:
               os.write(ostream.fileno(), prefix+"  <jobID>"+str(self.jobID)+"</jobID>\n")
            #
            os.write(ostream.fileno(), prefix)
            os.write(ostream.fileno(), "</ResultHeader>\n")


    class Solution(object):
        def __init__(self):
            self.status_type=OSrL.SolutionStatus.unsure
            self.status_description=None
            self.message=None
            self.variable={}
            self.dual={}
            self.objective={}
            self.other={}

        def _parse_xml(self, node):
            for child in node.childNodes:
              if child.nodeType == Node.ELEMENT_NODE:
                 if child.nodeName.lower() == "message":
                    self.message = get_xml_text(child)

                 elif child.nodeName.lower() == "status":
                    for (name,value) in child.attributes.items():
                      if name == "type":
                             self.status_type = str(value)
                      elif name == "description":
                             self.status_description = str(value)
                 elif child.nodeName.lower() == "variables":
                    for gchild in child.childNodes:
                      if gchild.nodeType == Node.ELEMENT_NODE and\
                         gchild.nodeName.lower() == "values":
                         for ggchild in gchild.childNodes:
                           if ggchild.nodeType == Node.ELEMENT_NODE and\
                              ggchild.nodeName.lower() == "var":
                              index=None
                              for (name,value) in ggchild.attributes.items():
                                if name == "idx":
                                   index = int(value)
                              self.variable[index] = get_xml_text(ggchild)
                 elif child.nodeName.lower() == "objectives":
                    for gchild in child.childNodes:
                      if gchild.nodeType == Node.ELEMENT_NODE and\
                         gchild.nodeName.lower() == "values":
                         for ggchild in gchild.childNodes:
                           if ggchild.nodeType == Node.ELEMENT_NODE and\
                              ggchild.nodeName.lower() == "obj":
                              index=None
                              for (name,value) in ggchild.attributes.items():
                                  if name == "idx":
                                   index = int(value)
                              self.objective[index] = get_xml_text(ggchild)
                 elif child.nodeName.lower() == "constraints":
                    for gchild in child.childNodes:
                      if gchild.nodeType == Node.ELEMENT_NODE and\
                         gchild.nodeName.lower() == "dualvalues":
                         for ggchild in gchild.childNodes:
                           if ggchild.nodeType == Node.ELEMENT_NODE and\
                              ggchild.nodeName.lower() == "con":
                              index=None
                              for (name,value) in ggchild.attributes.items():
                                  if name == "idx":
                                   index = int(value)
                              self.dual[index] = get_xml_text(ggchild)

        def validate(self):
            if self.status_type not in OSrL.SolutionStatus:
               raise ValueError, "Solution status value '"+str(self.status_type)+"' is not in OSrL.SolutionStatus"
            for key in self.variable:
              if type(key) is not int or (type(key) is int and key < 0):
                 raise KeyError, "Solution variables index '"+str(key)+"' is not an nonnegative integer"
            for key in self.dual:
              if type(key) is not int or (type(key) is int and key < 0):
                 raise KeyError, "Solution constraint index '"+str(key)+"' is not an nonnegative integer"
            for key in self.objective:
              if type(key) is not int or (type(key) is int and key >= 0):
                 raise KeyError, "Solution objective index '"+str(key)+"' is not a negative integer"

        def write(self,ostream=None, prefix=""):
            if ostream is None:
               ostream = sys.stdout
            self.validate()
            os.write(ostream.fileno(), prefix)
            os.write(ostream.fileno(), "<solution>\n")
            #
            os.write(ostream.fileno(), prefix+"  <status type=\""+str(self.status_type)+"\"")
            if self.status_description is not None:
               os.write(ostream.fileno(), " description=\""+str(self.status_description)+"\"")
            os.write(ostream.fileno(), " />\n")
            #
            if len(self.variable) > 0:
               os.write(ostream.fileno(), prefix+"  <variables>\n")
               os.write(ostream.fileno(), prefix+"    <values>\n")
               tmp = self.variable.keys()
               tmp.sort()
               for ndx in tmp:
                 os.write(ostream.fileno(), prefix+"      <var idx=\""+str(ndx)+"\">"+str(self.variable[ndx])+"</var>\n")
               os.write(ostream.fileno(), prefix+"    </values>\n")
               os.write(ostream.fileno(), prefix+"  </variables>\n")
            #
            if len(self.objective) > 0:
               os.write(ostream.fileno(), prefix+"  <objectives>\n")
               os.write(ostream.fileno(), prefix+"    <values>\n")
               tmp = self.objective.keys()
               tmp.sort()
               for ndx in tmp:
                 os.write(ostream.fileno(), prefix+"      <obj idx=\""+str(ndx)+"\">"+str(self.objective[ndx])+"</obj>\n")
               os.write(ostream.fileno(), prefix+"    </values>\n")
               os.write(ostream.fileno(), prefix+"  </objectives>\n")
            #
            if len(self.dual) > 0:
               os.write(ostream.fileno(), prefix+"  <constraints>\n")
               os.write(ostream.fileno(), prefix+"    <dualValues>\n")
               tmp = self.dual.keys()
               tmp.sort()
               for ndx in tmp:
                 os.write(ostream.fileno(), prefix+"      <con idx=\""+str(ndx)+"\">"+str(self.dual[ndx])+"</con>\n")
               os.write(ostream.fileno(), prefix+"    </dualValues>\n")
               os.write(ostream.fileno(), prefix+"  </constraints>\n")
            #
            os.write(ostream.fileno(), prefix)
            os.write(ostream.fileno(), "</solution>\n")


    def __init__(self):
        self.header = OSrL.ResultHeader()
        self.numVariables=0
        self.numConstraints=0
        self.numObjectives=0
        self.solution = []

    def add_solution(self):
        tmp = OSrL.Solution()
        self.solution.append(tmp)
        return tmp

    def __len__(self):
        return len(self.solution)

    def __iter__(self):
        return self.solution.__iter__()

    def validate(self):
        self.header.validate()
        for soln in self.solution:
          soln.validate()

    def write(self,ostream=None, prefix=""):
        if ostream is None:
           ostream = sys.stdout
        self.validate()
        if type(ostream) is str:
           self._tmpfile = ostream
           ostream = open(self._tmpfile,"w")
        else:
           self._tmpfile = None

        os.write(ostream.fileno(), prefix)
        os.write(ostream.fileno(), "<OSrL>\n")

        self.header.write(ostream,prefix+"  ")

        os.write(ostream.fileno(), prefix+"  <ResultData>\n")
        os.write(ostream.fileno(), prefix+"    <optimization\n")
        os.write(ostream.fileno(), prefix+"      numberOfSolutions=\""+str(len(self.solution))+"\"\n")
        os.write(ostream.fileno(), prefix+"      numberOfVariables=\""+str(self.numVariables)+"\"\n")
        os.write(ostream.fileno(), prefix+"      numberOfObjectives=\""+str(self.numObjectives)+"\"\n")
        os.write(ostream.fileno(), prefix+"      numberOfConstraints=\""+str(self.numConstraints)+"\"\n")
        os.write(ostream.fileno(), prefix+"    >\n")

        for soln in self.solution:
          soln.write(ostream, prefix+"      ")

        os.write(ostream.fileno(), prefix+"    </optimization>\n")
        os.write(ostream.fileno(), prefix+"  </ResultData>\n")

        os.write(ostream.fileno(), prefix)
        os.write(ostream.fileno(), "</OSrL>\n")
        if self._tmpfile is not None:
           ostream.close()

    def read(self, filename):
        try:
          doc = minidom.parse(filename)
        except xml.parsers.expat.ExpatError, e:
             raise xml.parsers.expat.ExpatError, "Problem parsing XML file " + filename+": "+str(e)
        except Exception, e:
             raise
        try:
          self._parse_xml(doc.documentElement)
        except:                                 #pragma:nocover
          raise IOError, "Problem initializing with data from the XML file " + filename
        self.validate()

    def _parse_xml(self, node):
        for child in node.childNodes:
          if child.nodeType == Node.ELEMENT_NODE and \
             child.nodeName.lower() == "resultheader":
             self.header._parse_xml(child)
          if child.nodeType == Node.ELEMENT_NODE and \
             child.nodeName.lower() == "resultdata":
             for gchild in child.childNodes:
               if gchild.nodeType == Node.ELEMENT_NODE and \
                  gchild.nodeName.lower() == "optimization":
                  for (name,value) in gchild.attributes.items():
                      if name == "numberOfSolutions":
                            self.numSolutions = str(value)
                      elif name == "numberOfObjectives":
                            self.numObjectives = str(value)
                      elif name == "numberOfVariables":
                            self.numVariables = str(value)
                      elif name == "numberOfConstraints":
                            self.numConstraints = str(value)
                  for ggchild in gchild.childNodes:
                    if ggchild.nodeType == Node.ELEMENT_NODE and \
                       ggchild.nodeName.lower() == "solution":
                       tmp = self.add_solution()
                       tmp._parse_xml(ggchild)




from coopr.opt.base import results
from coopr.opt.base.formats import *
from coopr.opt import SolverResults
from pyutilib.component.core import alias

class ResultsReader_osrl(results.AbstractResultsReader):
    """
    Class that reads in an OSrL results file and generates a 
    SolverResults object.
    """

    alias(str(ResultsFormat.osrl))

    def __init__(self, name=None):
        results.AbstractResultsReader.__init__(self,ResultsFormat.osrl)
        if not name is None:
            self.name = name

    def __call__(self, filename, res=None):
        if res is None:
            res = SolverResults()  
        osrl = OSrL()
        osrl.read(filename)
        #
        # Transfer solver info into the SolverResults object
        #  
        ##res.solver.status = SolverResults.SolverStatus(osrl.generalStatus)
        res.solver.serviceURI = osrl.header.serviceURI
        res.solver.serviceName = osrl.header.serviceName
        res.solver.instanceName = osrl.header.instanceName
        res.solver.systime = osrl.header.time
        res.solver.message = osrl.header.message
        res.solver.id = osrl.header.jobID
        res.problem.name = osrl.header.instanceName
        #
        # Transfer solution info into the SolverResults object
        #  
        for soln in osrl:
          #
          # We create a solution, and then populate its data
          # The solution object is managed by the SolverResults instance
          #
          solution = res.solution.add()
          solution.status = SolutionStatus(soln.status_type)
          solution.status_description = soln.status_description
          solution.message = soln.message
          for key in soln.variable:
            solution.variable[key+1] = soln.variable[key]
          for key in soln.dual:
            solution.constraint[key+1].dual = soln.dual[key]
          i=0
          for key in soln.objective:
            solution.objective['f'+str(i)] = soln.objective[key]
            solution.objective['f'+str(i)].id = key
            i=i+1
          solution.other=soln.other
          res.problem.number_of_constraints = len(soln.dual) 
          res.problem.number_of_variables = len(soln.variable) 
          res.problem.number_of_objectives = len(soln.objective) 
        return res

