#!/usr/bin/env python
from AIGO import logger

from AIGO.ReferenceSet import RefSet
from AIGO.FunctionalAnnotation import FuncAnnot
from AIGO.go.OBO import readGOoboXML

from AIGO.Analyse import AnalyseFA
from AIGO.Report import ReportFA

from AIGO.utils.Execute import batchExecute

refSet = RefSet(organism="platypus", fileName="platypus.refSet", refType="Text")
G = readGOoboXML("go_daily-termdb.obo-xml")
FA = FuncAnnot("platypusProject", refSet, G, organism="platypus")
FA.read("platypus.gaf", "GAF") 

analyseFA = AnalyseFA()

analyseFA.largestSet([FA])
logger.info("Largest sets of annotations:")
logger.info("\t%d for %s" % (FA['largestSet']['All_aspects_of_GO'], FA.name))

batchList=["coverage",  "richness", "numberAnnot", "redundancy", "specificity", "informationContent"]
batchExecute(batchList, analyseFA, [FA])

reportFA = ReportFA(outDir=None, name="platypusProject", organism="platypus")
reportFA.printStatistics([FA] ,batchList)
