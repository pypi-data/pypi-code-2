"""
FunctionalAnnotation.py

AIGO is a python library for
the Analysis and Inter-comparison of Gene Ontology functional annotations.
see (http://code.google.com/p/aigo).
        
Created by Michael Defoin-Platel on 21/02/2010.
Copyright (c) 2010. All rights reserved.

AIGO is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pylab import *
import csv

from AIGO import logger, logFun
from AIGO import IO


class FuncAnnot(dict):
    """
    This class stores the mapping between gene products and GO terms.
    It also provides methods to compute statistis about this mapping.
    """

    def __init__(self, name, refSet, G , **args):
        
        self.name = str(name)
        self.refSet = refSet
        self.G = G

        self.status="Empty"
        self.GPtoGO, self.GOtoGP = dict(),dict()

        # set any keyword valued parameters
        for k,v in args.items():
            self.__dict__[k] = v

    def isEmpty(self):
        return self.status=="Empty"

    @logFun("Adding functional annotation")
    def add(self, FA):
        logger.info("Name :\t%s" % self.name)
        
        for aspect in FA.GPtoGO:
            if not self.GPtoGO.has_key(aspect):
                self.GPtoGO[aspect]=dict()
                
            for gp in FA.GPtoGO[aspect]:                
                self.GPtoGO[aspect].setdefault(gp, set()).update(FA.GPtoGO[aspect][gp])

        for aspect in FA.GOtoGP:
            if not self.GOtoGP.has_key(aspect):
                self.GOtoGP[aspect]=dict()
                
            for go in FA.GOtoGP[aspect]:
                self.GOtoGP[aspect].setdefault(go, set()).update(FA.GOtoGP[aspect][go])

        self['GA']=set()
        for a in  self.G.aspect:
            self['GA']=self['GA']  | set(self.GPtoGO[a].keys())

        logger.info ("%d gene products are annotated" % (len(self['GA'])))

        self.status="Loaded"
            
        for  a in self.G.aspect:
            logger.info ("%s : %.2f annotations per set" % (a, mean([len(self.GPtoGO[a][gp]) for gp in self.GPtoGO[a]])))

    @logFun("Intersecting with another functional annotation")
    def inter(self, FA):
        logger.info("Name :\t%s" % self.name)
        
        for aspect in self.GPtoGO:
            if not FA.GPtoGO.has_key(aspect):
                self.GPtoGO[aspect]=dict()
            else:
                for gp in set(self.GPtoGO[aspect].keys()).difference(FA.GPtoGO[aspect]):
                    del self.GPtoGO[aspect][gp]
                    
                for gp in set(self.GPtoGO[aspect].keys()).intersection(FA.GPtoGO[aspect]):
                    self.GPtoGO[aspect][gp].intersection_update(FA.GPtoGO[aspect][gp])

        for aspect in self.GOtoGP:
            if not FA.GOtoGP.has_key(aspect):
                self.GOtoGP[aspect]=dict()
            else:
                for go in set(self.GOtoGP[aspect].keys()).difference(FA.GOtoGP[aspect].keys()):
                    del self.GOtoGP[aspect][go]
                for go in set(self.GOtoGP[aspect].keys()).intersection(FA.GOtoGP[aspect].keys()):
                    self.GOtoGP[aspect][go].intersection_update(FA.GOtoGP[aspect][go])

        self['GA']=set()
        for a in  self.G.aspect:
            self['GA']=self['GA']  | set(self.GPtoGO[a].keys())

        logger.info ("%d gene products are annotated" % (len(self['GA'])))

        self.status="Loaded"
            
        for  a in self.G.aspect:
            logger.info ("%s : %.2f annotations per set" % (a, mean([len(self.GPtoGO[a][gp]) for gp in self.GPtoGO[a]])))
    

    @logFun("Remove gene products and their annotations")
    def removeGP(self, GP, myAspects=None):
        logger.info("Name :\t%s" % self.name)

        if myAspects==None:
            myAspects=self.GPtoGO
        
        for aspect in myAspects:
            for g in GP:
                if self.GPtoGO[aspect].has_key(g):
                    del self.GPtoGO[aspect][g]

        self.GOtoGP=dict()
        for aspect in self.G.aspect:
            self.GOtoGP[aspect]=dict()

            for gp in self.GPtoGO[aspect]:
                for go in self.GPtoGO[aspect][gp]:
                    self.GOtoGP[aspect].setdefault(go, set()).add(gp)

        self['GA']=set()
        for a in  self.G.aspect:
            self['GA']=self['GA']  | set(self.GPtoGO[a].keys())

        logger.info ("%d gene products are annotated" % (len(self['GA'])))

        self.status="Loaed"
            
        for  a in self.G.aspect:
            logger.info ("%s : %.2f annotations per set" % (a, mean([len(self.GPtoGO[a][gp]) for gp in self.GPtoGO[a]])))

    @logFun("Checking validity of functional annotation")
    def checkValidity(self):
        logger.info("Name :\t%s" % self.name)
        
        allValid=True
        for aspect in self.GPtoGO:
            valid=True
            for gp in self.GPtoGO[aspect]:
                for go in self.GPtoGO[aspect][gp]:
                    if not gp in self.GOtoGP[aspect][go]:
                        logger.handleWarning ("%s not found in GOtoGP[%s][%s]" % (gp,aspect,go))
                        valid=False

            for go in self.GOtoGP[aspect]:
                for gp in self.GOtoGP[aspect][go]:
                    if not go in self.GPtoGO[aspect][gp]:
                        logger.handleWarning ("%s not found in GPtoGO[%s][%s]" % (go,aspect,gp))
                        valid=False


            if valid:
                logger.info ("%s : is valid" % (aspect))
            
            allValid = allValid and valid
            
        return allValid


    @logFun("Reading functional annotation")
    def read(self, fileName="", fileType=""):
        """
        This method reads functional annotations.
        Available file format are GO annotation file (GAF), Blast2GO (B2G), Affymetrix,(AFFY) , ArrayIDer (AID) , GP2GO or GO2GP  for a simple GPid to GOids mapping
        """

        logger.info("Name :\t%s" % self.name)

        if not fileName=="":
            self.__dict__['fileName'] = fileName

        if not fileType=="":
            self.__dict__['fileType'] = fileType


        fileType=IO.IOType.get(self.fileType, self.fileType)
        
        if fileType not in IO.IOType.values():
            print "Sorry, unknown file type : %s" % fileType
            raise ValueError

        logger.info("%s file : \t%s " % (fileType, fileName ) )

        try:
            if fileType=="GAF":
                self.GPtoGO, self.GOtoGP = IO.extract_GAF(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="B2G":
                self.GPtoGO, self.GOtoGP = IO.extract_GP2GO(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="AFFY":
                self.GPtoGO, self.GOtoGP = IO.extract_Affy(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="AID":
                self.GPtoGO, self.GOtoGP = IO.extract_AID(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="SCOP":
                self.GPtoGO, self.GOtoGP = IO.extract_SCOP(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="GNISD": #gene networks in seed development format http://seedgenenetwork.net/annotate#arabidopsis
                self.GPtoGO, self.GOtoGP = IO.extract_Affy(self.fileName, self.G, refSet=self.refSet, GO_columns=[6, 7, 8], filetype="GNIS-Affy", delimiter='	', quoting=csv.QUOTE_MINIMAL)
            elif fileType=="GP2GO":
                self.GPtoGO, self.GOtoGP = IO.extract_GP2GO(self.fileName, self.G, refSet=self.refSet)
            elif fileType=="GO2GP":
                self.GPtoGO, self.GOtoGP = IO.extract_GO2GP(self.fileName, self.G, refSet=self.refSet)
                
        except Exception, e:
            logger.handleFatal("Unable to read file %s: %s" % (fileName, str(e)))

        else:            
            #Find the set of annotated gene products
            self['GA']=set()
            for a in  self.G.aspect:
                self['GA']=self['GA']  | set(self.GPtoGO[a].keys())

            logger.info ("%d gene products are annotated" % (len(self['GA'])))

            self.status="Loaded"
            
            for  a in self.G.aspect:
                logger.info ("%s : %.2f annotations per set" % (a, mean([len(self.GPtoGO[a][gp]) for gp in self.GPtoGO[a]])))


