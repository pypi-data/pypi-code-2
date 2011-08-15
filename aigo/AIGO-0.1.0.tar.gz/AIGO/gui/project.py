"""
projects.py

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

from AIGO import logger,logFun
from AIGO.Analyse import AnalyseFA
from AIGO.Compare import CompareFA

class Project(dict):
    def __init__(self, **args):
        
        self.status="New"

        self['allFA']=list()
        self['analyseFA']=AnalyseFA()
        self['compareFA']=CompareFA()
        
        for k,v in args.items():
            self[k] = v

    @logFun("Loading project")
    def load(self, fileName):
        
        import shelve
        try:
            logger.info("File :\t%s" % fileName)
            shelf=shelve.open(fileName, protocol=-1)
            for k,v in shelf.items():
                self[k]=v

            shelf.close()            
            self.status="Loaded"
            
        except Exception, e:
            logger.handleWarning("Unable to load project %s: %s" % (fileName, str(e)))
            

    @logFun("Saving project")
    def save(self, fileName):
        import shelve
        try:
            logger.info("File :\t%s" % fileName)
            shelf=shelve.open(fileName, protocol=-1)
            shelf['fileName']=fileName
            for k,v in self.items():
                shelf[k]=v

            shelf.close()
            self.status="Saved"

        except  Exception, e:
            logger.handleWarning("Unable to save project %s: %s" % (fileName, str(e)))


    def addRefSet(self, refSet):
        self['refSet']=refSet
        self.status="Modified"

    def addGO(self, GO):
        self['GO']=GO
        self.status="Modified"

    def addFA(self, FA):
        if not self.has_key('allFA'):
            self['allFA']=list()

        self['allFA'].append(FA)
        self.status="Modified"

    def getFA(self, name):
        if not self.has_key('allFA'):
            return None

        ret=None
        for FA in self['allFA']:
            if FA.name==name:
                ret=FA

        return ret        

    def removeFA(self, name):

        if not self.has_key('allFA'):
            return -1

        rm=-1
        for idFA,FA in enumerate(self['allFA']):
            if FA.name==name:
                rm=idFA

        if not rm==-1:
            self['allFA'].pop(rm)
            self.status="Modified"

        return rm

    def getLoadedFA(self):
        return [FA for FA in self['allFA'] if not FA.isEmpty()]

    def applyStat(self, statistics):
        ret=False
        if hasattr(self['analyseFA'], statistics):
            getattr(self['analyseFA'], statistics)(self.getLoadedFA())
            self.status="Modified"
            ret=True

        return ret
        
