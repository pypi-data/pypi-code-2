"""
Statistics.py

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

from  pylab import *

from AIGO import logger, logFun

AIGO_UNIT_PERCENT="(in %)"
AIGO_UNIT_NONE=   ""
    
class RegisterStatistics(list):
    @logFun("Preparing the registration of statistics functions")
    def __init__(self):
        
        self.all=list()
        self.name=dict()
        self.unit=dict()
        self.types=dict()

    def add(self, statistics, name, unit="", types=None):
        logger.info("Registering statistics function %s" % statistics)
        
        self.all.append(statistics)
        self.name[statistics]=name
        self.unit[statistics]=unit
        self.types[statistics]=types

    def isRegistered(self, statistics):
        return self.name.has_key(statistics)

    def getAll(self):
        return self.all

    def getStat(self, name):
        for statistics in self.all:
            if self.name[statistics]==name:
                return statistics
        return None

    def getName(self, statistics):
        return self.name[statistics]

    def getNames(self, allStatistics):
        return [self.name[statistics] for statistics in allStatistics]

    def getUnit(self,statistics):
        return self.unit[statistics]

    def getTypes(self, statistics):
        return self.types[statistics]

    def hasType(self, statistics, statType):
        return statType in self.types[statistics]

    def statOfType(self, statType):
        return [statistics for statistics in self.all if statType in self.type[statistics]]


registerStat=RegisterStatistics()

registerStat.add("obsolete",            "Not used",                  types="Analyse", unit=AIGO_UNIT_PERCENT)
registerStat.add("unconnected",         "Obsolescence",              types="Analyse", unit=AIGO_UNIT_PERCENT)
registerStat.add("removeUnconnected",   "Remove Obsolete",           types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("redundancy",          "Redundancy",                types="Analyse", unit=AIGO_UNIT_PERCENT)
registerStat.add("removeRedundancy",    "Remove Redundancy",         types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("coverage",            "Coverage",                  types="Analyse", unit=AIGO_UNIT_PERCENT)
registerStat.add("richness",            "Richness",                  types="Analyse", unit=AIGO_UNIT_PERCENT)
registerStat.add("numberAnnot",         "Number of Annotations",     types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("coherence",           "Coherence",                 types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("compactness",         "Compactness",               types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("specificity",         "Specificity",               types="Analyse", unit=AIGO_UNIT_NONE)
registerStat.add("informationContent",  "Information Content",       types="Analyse", unit=AIGO_UNIT_NONE)

registerStat.add("venn",                "Coverage",                  types="Compare", unit=AIGO_UNIT_PERCENT)
registerStat.add("funcSim",             "Functional Similarity",     types="Compare", unit=AIGO_UNIT_NONE)





