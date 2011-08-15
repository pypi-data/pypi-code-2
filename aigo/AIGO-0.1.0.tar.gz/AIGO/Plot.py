"""
Plot.py

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

from numpy import *
from pylab import *

import new

from itertools import combinations, product

from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D


from AIGO import allAspect, logger, logFun
from AIGO.utils.Plot import createColorMap, surface2D, surface3D, multiBar, venn_2S, venn_3S, venn_NS
from AIGO.utils.Venn import VennDiagram

from AIGO.Statistics import registerStat as rS   


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class PlotFA(object):

    def __init__(self, **args):

        rc("font", family="sans-serif", size=16)
        
        self.__dict__["ext"] = "png"
        
        # set any keyword valued parameters
        for k,v in args.items():
            self.__dict__[k] = v
              
    @logFun("Plotting statistics for several FA")
    def Multiple(self, allFA,  statistics=None, figName=None, lloc="upper right", doGrid=False):
        lLabel=[aspect.replace("_", " ") for aspect in allAspect]

        logger.info("\t%s" % statistics)

        lBar=list()
        for aspect in allAspect:
            data=[]
            for FA in allFA:
                if type(FA[statistics][aspect]) == list:
                    data.append(mean(FA[statistics][aspect]))
                else:
                    data.append(FA[statistics][aspect])
            lBar.append( data )
            
        multiBar(lBar, lLabel, [FA.name for FA in allFA],
                 self.xlabel, "%s %s" % (rS.getName(statistics), rS.getUnit(statistics)),
                 lloc=lloc, grid=doGrid)

        if figName is None:
            figName="%s/Multi_%s_%s.%s" % (self.outDir, statistics, self.name, self.ext)
            
        savefig(figName)

        return figName
        

#------------------------------------------------------------------------------
    @logFun("Plotting the distribution of the size of annotation sets")
    def numberAnnotHisto2D(self, allFA, maxRange=20, doGrid=False, tit=None, **kargs):
        
        for aspect in allAspect:
            if aspect=='All_aspects_of_GO':
                continue

            bins=list(arange(0.5, maxRange))

            allValue=list()
            for FA in allFA:
                data=FA['numberAnnot'][aspect]
                v,b=histogram(data, bins)
                v=list(v)
                v.append(len(filter(lambda x: x>=maxRange, data)))
                allValue.append(v)

            ticLabel=[str(int(b+0.5)) for b in bins[:-1]]
            ticLabel.append(">=%d" % maxRange)

            if tit==None:
                ntit="Distribution of the size of annotation sets in %s" % aspect.replace("_", " ")
            else:
                ntit=tit
            
            multiBar(allValue, [FA.name for FA in allFA], ticLabel,
                     "Number of annotations", "Number of gene products",
                     lloc="upper right",
                     tit=ntit,
                     grid=doGrid)

            figName="%s/Histo2D_NumberAnnot_%s_%s.%s" % (self.outDir, self.name, aspect, self.ext)
            savefig(figName)

    @logFun("Plotting the distribution of the coherence of annotation sets")
    def coherenceHisto2D(self, allFA, doGrid=False, tit=None, **kargs):

        for aspect in allAspect:
            if aspect=='All_aspects_of_GO':
                continue
            
            bins=list(arange(0.,1.1, 0.1))

            allValue=list()
            for FA in allFA:
                data=FA['coherence'][aspect]
                v,b=histogram(data, bins)
                allValue.append(v)

            ticLabel=["[%.1f,%.1f)" % (s,e) for s,e in zip(bins[0:-1],bins[1:]) ]
            if tit==None:
                ntit="Distribution of the coherence of annotation sets in %s" % aspect.replace("_", " ")
            else:
                ntit=tit
            multiBar(allValue, [FA.name for FA in allFA], ticLabel,
                     "Coherence", "Number of gene products",
                     lloc="upper left",
                     tit=ntit,
                     grid=doGrid)

            figName="%s/Histo2D_Coherence_%s_%s.%s" % (self.outDir, self.name, aspect, self.ext)
            savefig(figName)

#------------------------------------------------------------------------------

    def Histo3D(self, allFA, statistics=None, figName=None, ylab="", angle=3, xmin=0, xmax=5, **kargs):
        for aspect in allAspect:
            if aspect=='All_aspects_of_GO':
                continue

            zdata= [FA[statistics][aspect] for FA in allFA]

            surface3D([FA.name for FA in allFA], zdata, xmin=min,xmax=xmax, xlab=getStatName(statistics), ylab=ylab, tit=aspect.replace("_"," "), angle=3)
            if figName is None:
                figName="%s/Histo3D_%s_%s_%s.%s" % (self.outDir, statistics, self.name, aspect, self.ext)

            savefig(figName)

        return figName
        
        
#------------------------------------------------------------------------------

    def venn2(self, compareFA, allFA, figName=None, tit=None, **kargs):
        for aspect in allAspect:
            figNameNormal="%s/Venn2_%s_%s.%s" % (self.outDir, self.name, aspect, self.ext)
            figNameProportional="%s/Venn2_proportional_%s_%s.%s" % (self.outDir, self.name, aspect, self.ext)
            d = VennDiagram(compareFA['venn2'][aspect])
            d.plot_normal(figNameNormal)
            d.plot_proportional(figNameProportional)
            
    def venn(self, compareFA, allFA, allFigName=None, fontsize=16, tit=None, **kargs):

        if allFigName is None:
            allFigName=dict()
            for aspect in allAspect:
                allFigName[aspect]="%s/Venn_%s_%s.%s" % (self.outDir, self.name, aspect, self.ext)
        
        for aspect in allAspect:
            if tit == None:
                ntit="Compare Coverage for %s" % aspect.replace("_", " ")
            else:
                ntit=tit
            if len(allFA)==2: 
                venn_2S(compareFA['venn'][aspect], tit=ntit, fontsize=fontsize)
            elif len(allFA)==3:
                venn_3S(compareFA['venn'][aspect], tit=ntit, fontsize=fontsize)
            else:
                #raise NotImplementedError()
                venn_NS(compareFA['venn'][aspect], tit=ntit)

            savefig(allFigName[aspect])
            
        return allFigName

    def funcSim(self, compareFA, allFA, allFigName=None, tit=None, **kargs):

        if allFigName is None:
            allFigName=dict()
            for aspect in allAspect:
                allFigName[aspect]=dict()
                for twoFAs in combinations(allFA, 2):
                    #Order the two FAs
                    FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))
                    
                    allFigName[aspect][(FA1.name, FA2.name)]="%s/funcSim_%s_%s_%s_%s.%s" % (self.outDir, self.name, aspect, FA1.name, FA2.name, self.ext)
        
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue

            for twoFAs in combinations(allFA, 2):
                
                #Order the two FAs
                FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))
                
                allD1, allD2 =zip(*compareFA['funcSim'][aspect][(FA1.name, FA2.name)].values())

                if tit==None:
                    ntit="Compare Semantic Similarity for %s" % aspect.replace("_", " ")
                else:
                    ntit=tit

                surface2D(allD1, allD2, yname=FA1.name, xname=FA2.name, tit=ntit)
                
                figName=allFigName[aspect][(FA1.name, FA2.name)]
                savefig(figName)
                
        return allFigName

    def funcSymSim(self, compareFA, allFA, allFigName=None, symFunc=lambda D:((array(D[0])+array(D[1]))/2.), tit=None, **kargs):

        if allFigName is None:
            allFigName=dict()
            for aspect in allAspect:
                allFigName[aspect]=dict()
                for twoFAs in combinations(allFA, 2):
                    #Order the two FAs
                    FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))
                    
                    allFigName[aspect][(FA1.name, FA2.name)]="%s/funcSymSim_%s_%s_%s_%s.%s" % (self.outDir, self.name, aspect, FA1.name, FA2.name, self.ext)

        for aspect in allAspect:
            #if aspect=="All_aspects_of_GO":
            #    continue

            for twoFAs in combinations(allFA, 2):
                
                #Order the two FAs
                FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))
                
                data=map(symFunc,compareFA['funcSim'][aspect][(FA1.name, FA2.name)].values())

                fig=figure()
                ax=fig.add_subplot(1,1,1)
                ax.set_xlabel("Similarity")
                ax.set_ylabel("Number of functional annotation sets")
                if tit==None:
                    ntit = "Functional similarity of annotations between %s and %s"% (FA1.name, FA2.name)
                else:
                    ntit=tit
                    
                ax.set_title(ntit)
                ax.hist(data, bins=20)

                if grid:
                    ax.yaxis.grid()

                if isinteractive():
                    fig.show()

                figName=allFigName[aspect][(FA1.name, FA2.name)]
                savefig(figName)

        return allFigName

    def recall(self, compareFA, allFA, figName=None, tit=None, **kargs):

        GS=allFA[0]
        
        allMean, allStd, allAsp=list(), list(), list()
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue
            
            allAsp.append(aspect)
            oneMean, oneStd=list(), list()
            for FA in allFA[1:]:
                oneMean.append(mean(compareFA['recall'][aspect][(FA.name, 'EXP2')].values()))
                oneStd.append(std(compareFA['recall'][aspect][(FA.name, 'EXP2')].values()))
            allMean.append(oneMean)
            allStd.append(oneStd)

        multiBar(allMean, allAsp, [FA.name for FA in allFA[1:]], self.xlabel, "Verspoor Hierarchical recall", lloc="upper right", grid=True)

        if figName is None:
            figName="%s/recall_%s.%s" % (self.outDir, GS.name, self.ext)
        
        savefig(figName)

        return figName

    def precision(self, compareFA, allFA, figName=None, **kargs):

        GS=allFA[0]

        allMean, allStd, allAsp=list(), list(), list()
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue
            
            allAsp.append(aspect)
            oneMean, oneStd=list(), list()
            for FA in allFA[1:]:
                oneMean.append(mean(compareFA['precision'][aspect][(FA.name, 'EXP2')].values()))
                oneStd.append(std(compareFA['precision'][aspect][(FA.name, 'EXP2')].values()))
            allMean.append(oneMean)
            allStd.append(oneStd)

        multiBar(allMean, allAsp, [FA.name for FA in allFA[1:]], self.xlabel, "Verspoor Hierarchical precision", lloc="upper right", grid=True)

        if figName is None:
            figName="%s/precision_%s.%s" % (self.outDir, GS.name, self.ext)
        
        savefig(figName)

        return figName

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#           Register plotting functions
#------------------------------------------------------------------------------
class decoStat(object):

    def __init__(self, statistics):
        self.statistics = statistics

    def __call__(self, f):

        def wrapped_f(*args, **kargs):
            return f(*args, statistics=self.statistics, **kargs)

        wrapped_f.__name__=self.statistics
        
        return wrapped_f


class RegisterPlotFunction(object):
    @logFun("Preparing the registration of plot functions")
    def __init__(self, cls):
        self.all=list()
        self.allTypes=set()
        self.types=dict()
        self.cls=cls

    def getMultiPlotFunction(self, statistics):
        @decoStat(statistics)
        def newMultiPlotFunction(*args, **kargs):
            return  PlotFA.Multiple(*args, **kargs)

        return newMultiPlotFunction

    def getHisto3DPlotFunction(self, statistics):
        @decoStat(statistics)
        def newHisto3DPlotFunction(*args, **kargs):
            return  PlotFA.Histo3D(*args, **kargs)

        return newHisto3DPlotFunction
    
    def add(self, statistics, plotType):
        logger.info("Registering plot function %s" % statistics)
        
        if not rS.isRegistered(statistics):
            logger.handleWarning("Caution, the statistics is unknown : %s" % statistics)
            return False

        self.all.append(statistics)
        
        if plotType=="Multiple":
            newPlotFunc = self.getMultiPlotFunction(statistics)
            newPlotFunc = new.instancemethod(newPlotFunc, None, self.cls)
            setattr(self.cls, newPlotFunc.__name__, newPlotFunc)
        elif plotType=="Histo3D":
            newPlotFunc = self.getHisto3DPlotFunction(statistics)
            newPlotFunc = new.instancemethod(newPlotFunc, None, self.cls)
            setattr(self.cls, "%sHisto3D" % newPlotFunc.__name__, newPlotFunc)
        else:
            logger.handleWarning("Caution, the statistics plot type is unknown : %s" % plotType)
            pass

        self.types.setdefault(statistics, set()).add(plotType)
        self.allTypes.add(plotType)

        return True


    def isRegistered(self, statistics):
        return self.name.has_key(statistics)

    def getAll(self):
        return self.all

    def getAllTypes(self):
        return list(self.allTypes)

    def getType(self, statistics):
        return list(self.types[statistics])

    def hasType(self, statistics, plotType):
        return plotType in self.types[statistics]

    def statOfType(self, plotType):
        return [statistics for statistics in self.all if plotType in self.types[statistics]]



registerPlot=RegisterPlotFunction(PlotFA)

for statistics in ["obsolete", "unconnected", "coverage",  "richness", "numberAnnot", "coherence", "redundancy", "compactness", "specificity", "informationContent"]:
    registerPlot.add(statistics, "Multiple")


for statistics in [ "numberAnnot", "coherence", "compactness", "specificity", "informationContent"]:
    registerPlot.add(statistics, "Histo3D")

#------------------------------------------------------------------------------
