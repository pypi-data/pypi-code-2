#!/usr/bin/python

from __future__ import division

# Written by Manuel A. Rivas
# Updated 09.02.2009

# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$



from optparse import OptionParser
import array
import numpy
import math
import sys,re
from rpy2.rpy_classic import *
from SAMpileuphelper import *
import os

def main(argv = None):
    if not argv:
        argv = sys.argv
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    parser.add_option("-f","--force",
                      action="store_true",dest="force",
                      default=False,
                      help="proceed even with bad extensions")
    parser.add_option("--pif")
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--dbsnp")
    parser.add_option("--skipannot")
    parser.add_option("--chr")
    parser.add_option("--bqthr")
    parser.add_option("--mqthr")
    parser.add_option("--module")
    parser.add_option("--sndb")
    parser.add_option("--snplist",
                      default="snplist.alleles.readyannot")
    parser.add_option("--iterations",
                      default = 10)
    parser.add_option("--outputdir")
    parser.add_option("--out",
                      default = "EMFreqAssoc.out")
    parser.add_option("--dosage",
                      default = "snps.dosage")
    (options, args) = parser.parse_args()
  

    if not options.force:
        set_default_mode(BASIC_CONVERSION)
        epsilon = .00000001
        pathnamedosage = os.path.join(options.outputdir,str(options.dosage))
        pathname = os.path.join(options.outputdir,str(options.out))
        pathnamedosagepool = os.path.join(options.outputdir,str(options.dosage) + '.pool')
        dosagefilecasecontrol = open(pathnamedosage,'w+')
        dosagepool = open(pathnamedosagepool,'w+')
        #casetotchroms = int(options.casechrom)
        #controltotchroms = int(options.controlchrom)
        #totchroms = int(options.chromosomes)
        snplist = {}
        snplistallele = {}
        snpfile = open(options.snplist,'r')
        casemap = {}
        controlmap = {}
        casecounts = {}
        controlcounts = {}
        extension = '.combined.error.coverage.calls'
        caseref = {}
        casenonref = {}
        snpscases = {}
        snpscontrols = {}
        expectedcases = {}
        expectedcontrols = {}
        expectedpopulation = {}
       # controlind = int(options.controlinds)
      #  controlchrom = controlind*2
       # caseind = int(options.caseinds)
       # casechrom = caseind*2
       # totalchrom = int(casechrom)*len(casemap) + int(controlchrom)*len(controlmap)
        casemapbwd = {}
        controlmapbwd = {}
        iterations = int(options.iterations)
        casefile = {}
        controlfile = {}
        indcasefile = {}
        indcontrolfile = {}
        chromcasefile = {}
        chromcontrolfile = {}
        poolfile = open(options.pif,'r')
        poolfile = poolfile.readlines()
        
        casetotchroms = 0
        controltotchroms = 0
        totchroms = 0
        
        for linef in poolfile[1:]:
            linef = linef.rstrip()
            linef = linef.split()
            fname = linef[0]
            phenotype = int(linef[1])
            inds = int(linef[2])
            chroms = int(linef[3])
            totchroms += chroms
            if phenotype == 0:
                controlfile[fname] = fname
                indcontrolfile[fname] = inds
                chromcontrolfile[fname] = chroms
                controltotchroms += chroms
            elif phenotype == 1:
                casefile[fname] = fname
                indcasefile[fname] = inds
                chromcasefile[fname] = chroms
                casetotchroms += chroms
        
        snpfileread = snpfile.readlines()
        for snpline in snpfileread[1:]:
            snpline = snpline.rstrip()
            snpline = snpline.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            if "chr" in chr:
                chroffsetsnp = str(chr) + ':' + str(pos)
            else:
                chroffsetsnp = "chr" + str(chr) + ':' + str(pos)
            snplist[chroffsetsnp] = chroffsetsnp
            snplistallele[chroffsetsnp,'ref'] = snpline[5][0]
            snplistallele[chroffsetsnp,'nonref'] = snpline[5][1]

        i = 0
        j = 0
        for caselinefile in casefile.keys():
            casemap[caselinefile] = i
            casemapbwd[i] = caselinefile
            casef = str(caselinefile) + str(extension)
            if '.calls' not in casef:
                parser.error("Expecting arguments to be .calls files.")
            f = open(casef,'r')
            print "Processing Case File %s ... " % f
            f = f.readlines()
            for line in f[1:]:
                line = line.split()
                chroffset = line[0]
                if "chr" in chroffset:
                    pass
                else:
                    chroffset = "chr" + str(chroffset)
                ref_base = line[1]
                coveragefwd = int(line[8])
                coveragerev = int(line[15])
                lod = float(line[21])
                alternate_allele = str(line[16])
                reference_allele = str(line[15])
                coverage = int(line[18])
                ref_index = return_ref_index(ref_base)
                alt_index = return_ref_index(alternate_allele)
                allele_counts = return_allele_counts_calls(line)
                allele_countsfwd = return_allele_counts_callsfwd(line)
                allele_countsrev = return_allele_counts_callsrev(line)
                if chroffset in snplist:
                    ref_indexglobal = return_ref_index(snplistallele[chroffset,'ref'])
                    alt_indexglobal = return_ref_index(snplistallele[chroffset,'nonref'])
                    snpscases[chroffset,i,'reffwd'] = allele_countsfwd[ref_indexglobal]
                    snpscases[chroffset,i,'refrev'] = allele_countsrev[ref_indexglobal]
                    snpscases[chroffset,i,'ref'] = allele_counts[ref_indexglobal]
                    snpscases[chroffset,i,'nonreffwd'] = allele_countsfwd[alt_indexglobal]
                    snpscases[chroffset,i,'nonrefrev'] = allele_countsrev[alt_indexglobal]
                    snpscases[chroffset,i,'nonref'] = allele_counts[alt_indexglobal]
                    snpscases[chroffset,i,'lod'] = lod
                    snpscases[chroffset,i,'coverage'] = coverage
                    snpscases[chroffset,i,'coveragefwd'] = coveragefwd
                    snpscases[chroffset,i,'coveragerev'] = coveragerev
            i += 1
        for controllinefile in controlfile.keys():
            controlmap[controllinefile] = j
            controlmapbwd[j] = controllinefile
            controlf = str(controllinefile) + str(extension)
            if '.calls' not in controlf:
                parser.error("Expecting arguments to be .calls files.")
            fc = open(controlf,'r')
            print "Processing Control File %s ... " % fc
            fc = fc.readlines()
            for linec in fc[1:]:
                linec = linec.split()
                chroffset = linec[0]
                if "chr" in chroffset:
                    pass
                else:
                    chroffset = "chr" + str(chroffset)
                ref_base = linec[1]
                coveragefwd = int(linec[8])
                coveragerev = int(linec[15])
                coverage = int(linec[18])
                lod = float(linec[21])
                alternate_allele = str(linec[16])
                reference_allele = str(linec[15])
                ref_index = return_ref_index(ref_base)
                alt_index = return_ref_index(alternate_allele)
                allele_counts = return_allele_counts_calls(linec)
                allele_countsfwd = return_allele_counts_callsfwd(linec)
                allele_countsrev = return_allele_counts_callsrev(linec)
                if chroffset in snplist:
                    ref_indexglobal = return_ref_index(snplistallele[chroffset,'ref'])
                    alt_indexglobal = return_ref_index(snplistallele[chroffset,'nonref'])
                    snpscontrols[chroffset,j,'reffwd'] = allele_countsfwd[ref_indexglobal]
                    snpscontrols[chroffset,j,'refrev'] = allele_countsrev[ref_indexglobal]
                    snpscontrols[chroffset,j,'ref'] = allele_counts[ref_indexglobal]
                    snpscontrols[chroffset,j,'nonreffwd'] = allele_countsfwd[alt_indexglobal]
                    snpscontrols[chroffset,j,'nonrefrev'] = allele_countsrev[alt_indexglobal]
                    snpscontrols[chroffset,j,'nonref'] = allele_counts[alt_indexglobal]
                    snpscontrols[chroffset,j,'lod'] = lod
                    snpscontrols[chroffset,j,'coverage'] = coverage
                    snpscontrols[chroffset,j,'coveragefwd'] = coveragefwd
                    snpscontrols[chroffset,j,'coveragerev'] = coveragerev
            j += 1
###############################
# E-M Routine
#
#
##############################
        nonreffwdcnts = {}
        nonrefrevcnts = {}
        reffwdcnts = {}
        refrevcnts = {}
        snpcasescnts = {}
        snpcontrolscnts = {}
        populationfrequency = {}
        populationfrequencyfwd = {}
        populationfrequencyrev = {}
        
        casefrequency = {}
        controlfrequency = {}
        varcasefrequency = {}
        varcontrolfrequency = {}
        probabilityvectorscase = {}
        probabilityvectorscontrols = {}
        for key in snplist.keys():
            ref_counts = 0
            alt_counts = 0
            reffwdcnts[key] = 0
            refrevcnts[key] = 0
            nonreffwdcnts[key] = 0
            nonrefrevcnts[key] = 0
            for i in range(0,len(casemap)):
                if (key,i,'ref') in snpscases:
                    ref_counts += snpscases[key,i,'ref']
                    alt_counts += snpscases[key,i,'nonref']
                    reffwdcnts[key] += snpscases[key,i,'reffwd']
                    refrevcnts[key] += snpscases[key,i,'refrev']
                    nonreffwdcnts[key] += snpscases[key,i,'nonreffwd']
                    nonrefrevcnts[key] += snpscases[key,i,'nonrefrev']
            for j in range(0,len(controlmap)):
                if (key,j,'ref') in snpscontrols:
                    ref_counts += snpscontrols[key,j,'ref']
                    alt_counts += snpscontrols[key,j,'nonref']
                    reffwdcnts[key] += snpscontrols[key,j,'reffwd']
                    refrevcnts[key] += snpscontrols[key,j,'refrev']
                    nonreffwdcnts[key] += snpscontrols[key,j,'nonreffwd'] 
                    nonrefrevcnts[key] += snpscontrols[key,j,'nonrefrev']
            #populationfrequency[key,0] = alt_counts/(alt_counts + ref_counts)
            populationfrequency[key,0] = .4
            populationfrequencyfwd[key,0] = .4
            populationfrequencyrev[key,0] = .4
            observedallelesdict = {}
            observedallelescasesdict = {}
            observedallelescontrolsdict = {}
            for iter in range(1,iterations):
                expectedaltcnts = 0 
                expectedaltcntsfwd = 0
                expectedaltcntsrev = 0
                observedalleles = 0
                expectedaltcasecnts = 0
                observedallelescases = 0
                expectedaltcontrolscnts = 0
                observedallelescontrols = 0

                variancealtcnts = 0
                for k in range(0,len(casemap)):
                    postprobarray = []
                    postprobarrayfwd = []
                    postprobarrayrev = []
                    postprobarraynorm = []
                    postprobarraynormfwd = []
                    postprobarraynormrev = []
                    if (key,k,'coverage') in snpscases and snpscases[key,k,'coverage'] > 0:
                        observedalleles += int(chromcasefile[casemapbwd[k]])
                        observedallelescases += int(chromcasefile[casemapbwd[k]])
                        if key in observedallelesdict and iter == 1:
                            observedallelesdict[key] += int(chromcasefile[casemapbwd[k]])
                            if key in observedallelescasesdict:
                             
                                observedallelescasesdict[key] += int(chromcasefile[casemapbwd[k]])
                            else: 
                                observedallelescasesdict[key] = 0
                                observedallelescasesdict[key] += int(chromcasefile[casemapbwd[k]])
                        elif iter == 1:
                            observedallelesdict[key] = 0
                            observedallelesdict[key] += int(chromcasefile[casemapbwd[k]])
                            observedallelescasesdict[key] = 0
                            observedallelescasesdict[key] += int(chromcasefile[casemapbwd[k]])
                        for l in range(0,(int(chromcasefile[casemapbwd[k]]) + 1)):
                            if l == 0:
                                postprobarray.append(r.dbinom(snpscases[key,k,'nonref'],snpscases[key,k,'coverage'],.001)[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequency[key,iter-1])[0])
                                postprobarrayfwd.append(r.dbinom(snpscases[key,k,'nonreffwd'],snpscases[key,k,'coveragefwd'],.001)[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequencyfwd[key,iter-1])[0])
                                postprobarrayrev.append(r.dbinom(snpscases[key,k,'nonrefrev'],snpscases[key,k,'coveragerev'],.001)[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequencyrev[key,iter-1])[0])
                            else:
                                postprobarray.append(r.dbinom(snpscases[key,k,'nonref'],snpscases[key,k,'coverage'],l/(int(chromcasefile[casemapbwd[k]])))[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequency[key,iter-1])[0])
                                postprobarrayfwd.append(r.dbinom(snpscases[key,k,'nonreffwd'],snpscases[key,k,'coveragefwd'],l/(int(chromcasefile[casemapbwd[k]])))[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequencyfwd[key,iter-1])[0])
                                postprobarrayrev.append(r.dbinom(snpscases[key,k,'nonrefrev'],snpscases[key,k,'coveragerev'],l/(int(chromcasefile[casemapbwd[k]])))[0]*r.dbinom(l,(int(chromcasefile[casemapbwd[k]])),populationfrequencyrev[key,iter-1])[0])
                        if iter == (iterations - 1):
                            probabilityvectorscase[key,k] = numpy.zeros((1,len(postprobarray)))
                            dosagepool.write(str(key) + ' ' + str(casemapbwd[k]) + ' ' )
                        for i in range(0,len(postprobarray)):
                            postprobarraynorm.append(postprobarray[i]/numpy.sum(postprobarray))
                            postprobarraynormfwd.append(postprobarrayfwd[i]/numpy.sum(postprobarrayfwd))
                            postprobarraynormrev.append(postprobarrayrev[i]/numpy.sum(postprobarrayrev))
                            
                            if iter == (iterations - 1):
                                probabilityvectorscase[key,k][0][i] += postprobarray[i]/numpy.sum(postprobarray)
                                dosagepool.write(str(probabilityvectorscase[key,k][0][i]) + ' ')

                        if iter == (iterations - 1):
                            dosagepool.write('\n')
                        expectedpoolinit = 0
                        expectedpoolinitfwd = 0
                        expectedpoolinitrev = 0
                        variancepostprobinit = 0
                        for i in range(0,len(postprobarraynorm)):
                            expectedpoolinit += i*postprobarraynorm[i]
                            expectedpoolinitfwd += i*postprobarraynormfwd[i]
                            expectedpoolinitrev += i*postprobarraynormrev[i]
                        expectedaltcnts += expectedpoolinit
                        expectedaltcntsfwd += expectedpoolinitfwd
                        expectedaltcntsrev += expectedpoolinitrev
                        expectedaltcasecnts += expectedpoolinit
                        for i in range(0,len(postprobarraynorm)):
                            variancepostprobinit += postprobarraynorm[i]*math.pow((i - expectedpoolinit),2)
                        variancealtcnts += 1/100*variancepostprobinit
                variancealtcnts = variancealtcnts
                varcasefrequency[key,iter] = variancealtcnts
                variancealtcnts = 0
                for k in range(0,len(controlmap)):
                    postprobarray = []
                    postprobarrayfwd = []
                    postprobarrayrev = []
                    postprobarraynorm = []
                    postprobarraynormfwd = []
                    postprobarraynormrev = []
                    if (key,k,'coverage') in snpscontrols and snpscontrols[key,k,'coverage'] > 0:
                        observedalleles += int(chromcontrolfile[controlmapbwd[k]])
                        observedallelescontrols += int(chromcontrolfile[controlmapbwd[k]])
                        if key in observedallelesdict and iter == 1:
                            observedallelesdict[key] += int(chromcontrolfile[controlmapbwd[k]])
                            if key in observedallelescontrolsdict:
                                observedallelescontrolsdict[key] += int(chromcontrolfile[controlmapbwd[k]])
                            else: 
                                observedallelescontrolsdict[key] = 0
                                observedallelescontrolsdict[key] += int(chromcontrolfile[controlmapbwd[k]])
                        elif iter == 1:
                            observedallelesdict[key] = 0
                            observedallelesdict[key] += int(chromcontrolfile[controlmapbwd[k]])
                            observedallelescontrolsdict[key] = 0
                            observedallelescontrolsdict[key] += int(chromcontrolfile[controlmapbwd[k]])
                        for l in range(0,int(chromcontrolfile[controlmapbwd[k]])+1):
                            if l == 0:
                                postprobarray.append(r.dbinom(snpscontrols[key,k,'nonref'],snpscontrols[key,k,'coverage'],.001)[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequency[key,iter-1])[0])
                                postprobarrayfwd.append(r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],.001)[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequencyfwd[key,iter-1])[0])
                                postprobarrayrev.append(r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],.001)[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequencyrev[key,iter-1])[0])
                            else:
                                postprobarray.append(r.dbinom(snpscontrols[key,k,'nonref'],snpscontrols[key,k,'coverage'],l/(int(chromcontrolfile[controlmapbwd[k]])))[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequency[key,iter-1])[0])
                                postprobarrayfwd.append(r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],l/(int(chromcontrolfile[controlmapbwd[k]])))[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequencyfwd[key,iter-1])[0])
                                postprobarrayrev.append(r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],l/(int(chromcontrolfile[controlmapbwd[k]])))[0]*r.dbinom(l,(int(chromcontrolfile[controlmapbwd[k]])),populationfrequencyrev[key,iter-1])[0])
                       
                        if iter == (iterations - 1):
                            probabilityvectorscontrols[key,k] = numpy.zeros((1,len(postprobarray)))
                            dosagepool.write(str(key) + ' ' + str(controlmapbwd[k]) + ' ' )
                        for i in range(0,len(postprobarray)):
                            postprobarraynorm.append(postprobarray[i]/numpy.sum(postprobarray))
                            postprobarraynormfwd.append(postprobarrayfwd[i]/numpy.sum(postprobarrayfwd))
                            postprobarraynormrev.append(postprobarrayrev[i]/numpy.sum(postprobarrayrev))
                        
                            if iter == (iterations - 1):
                                probabilityvectorscontrols[key,k][0][i] += postprobarray[i]/numpy.sum(postprobarray)
                                dosagepool.write(str(probabilityvectorscontrols[key,k][0][i]) + ' ')
                                
                        if iter == (iterations - 1):
                            dosagepool.write('\n')
                                
                        expectedpoolinit = 0
                        expectedpoolinitfwd = 0
                        expectedpoolinitrev = 0
                        variancepostprobinit = 0
                        for i in range(0,len(postprobarraynorm)):
                            expectedpoolinit += i*postprobarraynorm[i]
                            expectedpoolinitfwd += i*postprobarraynormfwd[i]
                            expectedpoolinitrev += i*postprobarraynormrev[i]
                        expectedaltcnts += expectedpoolinit
                        expectedaltcntsfwd += expectedpoolinitfwd
                        expectedaltcntsrev += expectedpoolinitrev
                        expectedaltcontrolscnts += expectedpoolinit
                        for i in range(0,len(postprobarraynorm)):
                            variancepostprobinit += postprobarraynorm[i]*math.pow((i - expectedpoolinit),2)
                        variancealtcnts += 1/100*variancepostprobinit
               
                variancealtcnts = variancealtcnts
                varcontrolfrequency[key,iter] = variancealtcnts
                if key in observedallelesdict:
                    populationfrequency[key,iter] = expectedaltcnts/(observedallelesdict[key])
                    populationfrequencyfwd[key,iter] = expectedaltcntsfwd/(observedallelesdict[key])
                    populationfrequencyrev[key,iter] = expectedaltcntsrev/(observedallelesdict[key])
                else:
                    populationfrequency[key,iter] = expectedaltcnts/totchroms
                    populationfrequencyfwd[key,iter] = expectedaltcntsfwd/totchroms
                    populationfrequencyrev[key,iter] = expectedaltcntsrev/totchroms
                if key in observedallelescasesdict:
                  #  print "in key"
                  #  print key,iter
                    
                    casefrequency[key,iter] = expectedaltcasecnts/observedallelescasesdict[key]
                else:
                   # print key,iter
                   # print casetotchroms
                    if len(casemap) > 0:
                        casefrequency[key,iter] = expectedaltcasecnts/casetotchroms
                if key in observedallelescontrolsdict:
                    controlfrequency[key,iter] = expectedaltcontrolscnts/observedallelescontrolsdict[key]
                else:
                    if len(controlmap) > 0:
                        controlfrequency[key,iter] = expectedaltcontrolscnts/controltotchroms
        summarytest = open(pathname,'w')
        summarytest.write('chr:position chi_square_stat_LRT LRT_pval chi_sq_MLE_genotype pval_MLE_genotype pop_nr_freq case_nr_freq con_nr_freq LOD_strand freq_fwd freq_rev\n')
        for key in snplist.keys():
            
            exfwd = math.ceil(populationfrequencyfwd[key,iterations-1])
            exrev = math.ceil(populationfrequencyrev[key,iterations-1])
            nonreffwd = nonreffwdcnts[key]
            nonrefrev = nonrefrevcnts[key]
            reffwd = reffwdcnts[key]
            refrev = refrevcnts[key]

            likelihoodfinal = 0 
            likelihoodnull = [0]*(len(casemap) + len(controlmap))
            likelihoodfwd = 0
            likelihoodrev = 0
            likelihoodnullfwd = [0]*(len(casemap) + len(controlmap))
            likelihoodnullrev = [0]*(len(casemap) + len(controlmap))
            likelihoodalt1 = [0]*(len(casemap) + len(controlmap))
            likelihoodalt2 = [0]*(len(casemap) + len(controlmap))
            weightscasetmp = 0
            weightscontrolstmp = 0
            if (key,0) in probabilityvectorscase:
                weightscasetmp = 1
                weightscase = return_prob_weights(key,probabilityvectorscase,snpscases,casemap)
            if (key,0) in probabilityvectorscontrols:
                #weightscasetmp = 1
                weightscontrols = return_prob_weights(key,probabilityvectorscontrols,snpscontrols,controlmap)
                weightscontrolstmp = 1
            if (key,0) in probabilityvectorscase and (key,0) in probabilityvectorscontrols:    
                weightscasetmp = 1
                weightscontrolstmp = 1
#            LRTassoc = return_LRT_assoc(observedallelescasesdict[key],observedallelescontrolsdict[key],weightscase,weightscontrols,populationfrequency[key,iterations-1],casefrequency[key,iterations-1],controlfrequency[key,iterations-1])
            if key in observedallelescasesdict:
                casechromtot = int(observedallelescasesdict[key])
            else:
                casechromtot = 0
            if key in observedallelescontrolsdict:
                controlchromtot = int(observedallelescontrolsdict[key])
               
            else:
                controlchromtot = 0
            if weightscasetmp == 1 and weightscontrolstmp == 1:
                if  not isinstance(weightscase,dict) and not isinstance(weightscontrols,dict):
                    LRTassoc = 2*return_LRT_assoc(casetotchroms,controltotchroms,weightscase,weightscontrols,populationfrequency[key,iterations-1],casefrequency[key,iterations-1],controlfrequency[key,iterations-1])
                    dosagefilecasecontrol.write(str(key) + ' ' + 'Case' + ' ' + str(LRTassoc) + ' ')
                    for caseprob in range(0,len(weightscase[0])):
                        dosagefilecasecontrol.write(str(weightscase[0][caseprob]) + ' ')
                    dosagefilecasecontrol.write('\n')
                    dosagefilecasecontrol.write(str(key) + ' ' + 'Control' + ' ' + str(LRTassoc) + ' ')
                    for controlprob in range(0,len(weightscontrols[0])):
                        dosagefilecasecontrol.write(str(weightscontrols[0][controlprob]) + ' ')
                    dosagefilecasecontrol.write('\n')
            elif len(casemap) == 0 and weightscontrolstmp == 1:
                LRTassoc = 0
                dosagefilecasecontrol.write(str(key) + ' ' + 'Control' + ' ' + str(LRTassoc) + ' ')
                for controlprob in range(0,len(weightscontrols[0])):
                    dosagefilecasecontrol.write(("%4.4g ") % (weightscontrols[0][controlprob]))
                dosagefilecasecontrol.write('\n')
            elif len(controlmap) == 0 and weightscasetmp == 1:
                LRTassoc = 0
                dosagefilecasecontrol.write(str(key) + ' ' + 'Case' + ' ' + str(LRTassoc) + ' ')
                for caseprob in range(0,len(weightscase[0])):
                    dosagefilecasecontrol.write(("%4.4g ") % (weightscase[0][caseprob]))
                dosagefilecasecontrol.write('\n')
            else:
                LRTassoc = 0            
            
            
            for j in range(0,len(casemap)):
                if (key,j,'nonref') in snpscases and snpscases[key,j,'coverage'] > 0:
                    for m in range(0,int(chromcasefile[casemapbwd[j]]) + 1):
                        if m == 0:
                            factor = .002
                        else:
                            factor = 0
                        likelihoodfinal += r.log10(r.dbinom(snpscases[key,j,'nonref'],snpscases[key,j,'coverage'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],casefrequency[key,iterations-1])[0])[0]
                        likelihoodfwd += r.log10(r.dbinom(snpscases[key,j,'nonreffwd'],snpscases[key,j,'coveragefwd'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequency[key,iterations-1])[0])[0]
                        likelihoodrev += r.log10(r.dbinom(snpscases[key,j,'nonrefrev'],snpscases[key,j,'coveragerev'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequency[key,iterations-1])[0])[0]
                        likelihoodnullfwd[j] += r.dbinom(snpscases[key,j,'nonrefrev'],snpscases[key,j,'coveragerev'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequency[key,iterations-1])[0]
                        likelihoodnullrev[j] += r.dbinom(snpscases[key,j,'nonreffwd'],snpscases[key,j,'coveragefwd'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequency[key,iterations-1])[0]
                    likelihoodnull[j] = likelihoodnullfwd[j]*likelihoodnullrev[j]
            for k in range(0,len(controlmap)):
                if (key,k,'nonref') in snpscontrols and snpscontrols[key,k,'coverage'] > 0:
                    for m in range(0,int(chromcontrolfile[controlmapbwd[k]]) + 1):
                        if m == 0:
                            factor = .002
                        else:
                            factor = 0
                        likelihoodfinal += r.log10(r.dbinom(snpscontrols[key,k,'nonref'],snpscontrols[key,k,'coverage'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],controlfrequency[key,iterations-1])[0])[0]
                        likelihoodfwd += r.log10(r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequency[key,iterations-1])[0])[0]
                        likelihoodrev += r.log10(r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequency[key,iterations-1])[0])[0]
                        likelihoodnullfwd[k + len(casemap)] += r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequency[key,iterations-1])[0]
                        likelihoodnullrev[k + len(casemap)]  += r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequency[key,iterations-1])[0]
                    likelihoodnull[k + len(casemap) ] = likelihoodnullfwd[k + len(casemap)]*likelihoodnullrev[k + len(casemap)]
            likelihoodalt1fwd = [0]*(len(controlmap) + len(casemap))
            likelihoodalt2rev = [0]*(len(controlmap) + len(casemap))      
            for j in range(0,len(casemap)):
                if (key,j,'nonref') in snpscases and snpscases[key,j,'coverage']:
                    for m in range(0,int(chromcasefile[casemapbwd[j]]) + 1):
                        if m == 0:
                            factor = .002
                        else:
                            factor = 0
                        likelihoodfinal -= r.log10(r.dbinom(snpscases[key,j,'nonref'],snpscases[key,j,'coverage'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequency[key,iterations-1])[0])[0]
                       # likelihoodfwd -= r.log10(r.dbinom(snpscases[key,j,'nonreffwd'],snpscases[key,j,'coveragefwd'],.002))
                       # likelihoodrev -= r.log10(r.dbinom(snpscases[key,j,'nonrefrev'],snpscases[key,j,'coveragerev'],.002))
                        likelihoodalt1fwd[j] += r.dbinom(snpscases[key,j,'nonreffwd'],snpscases[key,j,'coveragefwd'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequencyfwd[key,iterations-1])[0]
                        
                        likelihoodalt2rev[j] += r.dbinom(snpscases[key,j,'nonrefrev'],snpscases[key,j,'coveragerev'],m/chromcasefile[casemapbwd[j]] + factor)[0]*r.dbinom(m,chromcasefile[casemapbwd[j]],populationfrequencyrev[key,iterations-1])[0]
                    likelihoodalt1fwd[j] = likelihoodalt1fwd[j]*r.dbinom(snpscases[key,j,'nonrefrev'],snpscases[key,j,'coveragerev'],.002)[0]
                    likelihoodalt2rev[j] = likelihoodalt2rev[j]*r.dbinom(snpscases[key,j,'nonreffwd'],snpscases[key,j,'coveragefwd'],.002)[0]
                    

                    
            for k in range(0,len(controlmap)):
                if (key,k,'nonref') in snpscontrols and snpscontrols[key,k,'coverage']:
                    for m in range(0,int(chromcontrolfile[controlmapbwd[k]]) + 1):
                        if m == 0:
                            factor = .002
                        else:
                            factor = 0
                        likelihoodfinal -= r.log10(r.dbinom(snpscontrols[key,k,'nonref'],snpscontrols[key,k,'coverage'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequency[key,iterations-1])[0])[0]
                      #  likelihoodfwd -= r.log10(r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],.002))
                      #  likelihoodrev -= r.log10(r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],.002))
                        likelihoodalt1fwd[k + len(casemap)] += r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequencyfwd[key,iterations-1])[0]
                       # likelihoodalt1 += r.log10(r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],.001))
                        likelihoodalt2rev[k + len(casemap)]  += r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],m/chromcontrolfile[controlmapbwd[k]] + factor)[0]*r.dbinom(m,chromcontrolfile[controlmapbwd[k]],populationfrequencyrev[key,iterations-1])[0]
                       # likelihoodalt2 += r.log10(r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'],.001))
                    likelihoodalt1fwd[k + len(casemap) ] = likelihoodalt1fwd[k + len(casemap)]*r.dbinom(snpscontrols[key,k,'nonrefrev'],snpscontrols[key,k,'coveragerev'],.002)[0]
                    likelihoodalt2rev[k + len(casemap) ] = likelihoodalt2rev[k + len(casemap)]*r.dbinom(snpscontrols[key,k,'nonreffwd'],snpscontrols[key,k,'coveragefwd'], .002)[0]
#===============================================================================
#            for i in range(0,len(likelihoodalt1fwd)):
#                if r.log10(likelihoodalt1fwd[i])[0] == float('-inf'):
#                    likelihoodalt1fwd[i] = -1000
#                elif r.log10(likelihoodalt1fwd[i])[0] == float('inf'):
#                    likelihoodalt1fwd[i] = 1000
#            for i in range(0,len(likelihoodalt2rev)):
#                if r.log10(likelihoodalt2rev[i])[0] == float('-inf'):
#                    likelihoodalt2rev[i] = -1000
#                elif r.log10(likelihoodalt2rev[i])[0] == float('inf'):
#                    likelihoodalt2rev[i] = 1000
#            for i in range(0,len(likelihoodnull)):
#                if r.log10(likelihoodnull[i])[0] == float('-inf'):
#                    likelihoodnull[i] = -1000
#                elif r.log10(likelihoodnull[i])[0] == float('inf'):
#                    likelihoodnull[i] = 1000
#===============================================================================
           # print key,likelihoodalt1fwd
           # print "\n"
           # print likelihoodalt2rev
           # print "\n"
           # print likelihoodnull
           # print "\n"
            likelihoodalt1 = numpy.prod(likelihoodalt1fwd)
            likelihoodalt2 = numpy.prod(likelihoodalt2rev)
            likelihoodnullhyp = numpy.prod(likelihoodnull)                                                                                                                         
#===============================================================================
#            if '-inf' in str(likelihoodalt1):
#                likelihoodalt1 = -10000
#            elif 'inf' in str(likelihoodalt1):
#                likelihoodalt1 = 10000
#            if '-inf' in str(likelihoodalt2):
#                likelihoodalt2 = -10000
#            elif 'inf' in str(likelihoodalt2):
#                likelihoodalt2 = 10000
#===============================================================================
            
            strandLOD1 = r.log10(likelihoodalt1)[0] - r.log10(likelihoodnullhyp)[0]
            strandLOD2 = r.log10(likelihoodalt2)[0] - r.log10(likelihoodnullhyp)[0]
            strandLOD = max(strandLOD1,strandLOD2)
            if '-inf' in str(strandLOD):
                strandLOD = -10000
            elif 'inf' in str(strandLOD):
                strandLOD = 10000
#===============================================================================
#            likelihoodf = 2*likelihoodfinal
#            chisqpval = 1- r.pchisq(likelihoodf,df = 1)
#===============================================================================

            if len(casemap) > 0 and len(controlmap) > 0:
           # chisqstat = math.pow((casefrequency[key,iterations-1] - controlfrequency[key,iterations-1]),2)/(((1/observedallelescontrols + 1/observedallelescases)*(populationfrequency[key,iterations-1]*(1-populationfrequency[key,iterations-1]))) + 1/(len(casemap) + len(controlmap))*(varcasefrequency[key,iterations-1] + varcontrolfrequency[key,iterations-1]))
                chisqstat2 = math.pow((casefrequency[key,iterations-1] - controlfrequency[key,iterations-1]),2)/(((1/controltotchroms + 1/casetotchroms)*(populationfrequency[key,iterations-1]*(1-populationfrequency[key,iterations-1]))))
            #  chisqstat3 = math.pow((casefrequency[key,iterations-1] - controlfrequency[key,iterations-1]),2)/(((1/observedallelescontrols + 1/observedallelescases)*(1/(len(casemap) + len(controlmap)))*(varcasefrequency[key,iterations-1] + varcontrolfrequency[key,iterations-1])))
#===============================================================================
#            pvals3 = 1-r.pchisq(chisqstat3,1)
#            pvals = 1-r.pchisq(chisqstat,1)
#            pvals2 = 1-r.pchisq(chisqstat2,1)
#===============================================================================
            else:
                LRTassoc = 0
                chisqstat2 = 0
            likelihoodalt1 = str(float(int(math.pow(10,2)*likelihoodalt1))/math.pow(10,2))
            likelihoodalt2 = str(float(int(math.pow(10,2)*likelihoodalt2))/math.pow(10,2))
            strandLOD = str(float(int(math.pow(10,2)*strandLOD))/math.pow(10,2))
                                                                                                         
           # chisqstatstr = str(float(int(math.pow(10,2)*chisqstat))/(math.pow(10,2)))
            chisqstatstr2 = str(float(int(math.pow(10,2)*chisqstat2))/(math.pow(10,2)))
            popfreqstr = str(float(int(math.pow(10,4)*populationfrequency[key,iterations-1]))/(math.pow(10,4)))
            if len(casemap) == 0:
                casefreqstr = str(0)
            else:
                casefreqstr = str(float(int(math.pow(10,4)*casefrequency[key,iterations-1]))/(math.pow(10,4)))
            if len(controlmap) == 0:
                controlfreqstr = str(0)
            else:
                controlfreqstr = str(float(int(math.pow(10,4)*controlfrequency[key,iterations-1]))/(math.pow(10,4)))
           # summarytest.write(str(key) + ' ' +  str(likelihoodf) + ' ' + str(chisqpval) +  ' ' + str(chisqstat2) + ' ' + str(pvals2) + ' ' + str(chisqstat3) + ' ' + str(pvals3) + ' ' + str(chisqstat) + ' ' + str(pvals) +  ' ' +  popfreqstr + ' ' +  casefreqstr + ' ' + controlfreqstr + ' ' + str(populationfrequencyfwd[key,iterations-1]) + ' ' + str(populationfrequencyrev[key,iterations-1]) +  ' ' + str(likelihoodalt1) + ' ' + str(likelihoodalt2) + ' ' + str(strandLOD) + ' ' + str(LRTassoc) + '\n')
           # summarytest.write(str(key) + ' ' +  str(chisqstat2)  + ' ' + str(LRTassoc) + '\n')
            summarytest.write(str(key) + ' ' + str(chisqstatstr2) + ' ' + str(LRTassoc) + ' ' + popfreqstr + ' ' + casefreqstr + ' ' + controlfreqstr + ' ' + str(strandLOD) + ' ' + str(populationfrequencyfwd[key,iterations-1]) + ' ' + str(populationfrequencyrev[key,iterations-1]) + '\n')

        summarytest.close()
        dosagefilecasecontrol.close()
        dosagepool.close()

if __name__ == "__main__":
    main()


