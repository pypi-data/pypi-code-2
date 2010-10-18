#!/usr/bin/python

from __future__ import division

# Written by Manuel A. Rivas
# Updated 07.13.2009

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
    parser.add_option("--bqthr",
                      default=22,
                      help="Base Quality Threshold Parameter")
    parser.add_option("--mqthr",
                      help="Read Mapping Quality Threshold Parameter",
                      default=1)
    parser.add_option("--pif",
                      help="Pool Info File")
    parser.add_option("--ncpu")
    # come back to this
    # Why do i need to specify this in SyzygyWrapper (make edits)
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--skipannot")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--sndb")
    parser.add_option("--outputdir")
    parser.add_option("--module")
    parser.add_option("--chr")
    parser.add_option("--dbsnp",
                      help="dbSNP File",
                      default="/seq/dirseq/rivas/Rivasglioma/dbsnp/basepos.snpshg18.dbsnp")
    (options, args) = parser.parse_args()
    

    if not options.force:
        set_default_mode(BASIC_CONVERSION)
        dbsnp = {}
        mcratefref = {}
        mcratefnonref = {}
        mcraterref = {}
        epsilon = .0000001
        mcraternonref = {}
        
        qthr = int(options.bqthr)
        mapqthr = int(options.mqthr)
        mcrateuniversalfwd = []
        mcrateuniversalrev = []
        mcrateuniversalfwddb = []
        mcrateuniversalrevdb = []
        mcratefrefdbsnp = {}
        mcratefnonrefdbsnp = {}
        mcraterrefdbsnp = {}
        mcraternonrefdbsnp = {}
        dbsnpfile = options.dbsnp
        dbsnp = populate_dbsnp_dictionary(dbsnp,dbsnpfile)
        poolfile = open(options.pif,'r')
        poolfile = poolfile.readlines()
        for linef in poolfile[1:]:
            linef = linef.rstrip()
            linef = linef.split()
            fname = str(linef[0]) + '.pileup'     
            fnamer = fname + str(qthr) + '.r.miscallrate.plots%03d.pdf'
            r.pdf(file=fnamer)
            filesummary = os.path.join(options.outputdir,str(fname) + ".bq" + str(qthr) + ".mq" + str(mapqthr) + ".bes")
            outsummary = open(filesummary,'w+')
            fileoutput = os.path.join(options.outputdir,fname + '.' + str(qthr) +'thresholded.coverage')
            coverageexp = []
            coveragethresholded = []
            miscallratefwd = []
            miscallratefwdthresholded = []
            miscallraterev = []
            miscallraterevthresholded = []
            coverageproportion = []
            miscallratefwdthresholdeddbsnp = []
            miscallraterevthresholdeddbsnp = []
            if '.pileup' not in fname:
                parser.error("Expecting arguments to be .pileup files.")
            f = open(fname,'r')
            outf = open(fileoutput,'w')
            outf.write('chr' + ' ' + 'offset' + ' ' + 'loc ' + 'ref_base ' + 'ref_idx ' + 'afwd ' + 'cfwd ' + 'gfwd ' + 'tfwd ' + 'dfwd ' + 'ifwd ' + 'arev ' + 'crev ' + 'grev ' + 'trev ' + 'drev ' + 'irev'+'\n')
            print "Processing %s..." % fname
            for line in f:
                line = line.rstrip()
                line = line.split('\t')
                chr = line[0]
                position = int(line[1]) 
                if "chr" in chr:
                    chroffset =  str(chr) + ":" + str(position)
                else:
                    chroffset = "chr" + str(chr) + ":" + str(position)
                reference_allele = line[2]
                reference_allele = reference_allele.upper()
                if reference_allele == 'A':
                    ref_index = 0
                elif reference_allele == 'C':
                    ref_index = 1
                elif reference_allele == 'G':
                    ref_index = 2
                elif reference_allele == 'T':
                    ref_index = 3
                coverage = line[3]
                allele_calls = line[4]
                base_quals = line[5]
                map_quals = line[-1]
                map_quals_list = list(map_quals)
                base_quals_list = list(base_quals)
                allele_calls_list =list(allele_calls)
                map_quals_strings = ascii_list(map_quals_list)
                base_quals_strings = ascii_list(base_quals_list)
                allele_calls_strings = allele_calls_list
                base_qualsthreshold_strings = return_q_list(qthr,base_quals_strings)
                allele_calls_threshold_strings = return_alleleq_list_SAM(mapqthr,qthr,base_quals_strings,map_quals_strings,allele_calls_strings)
             #   debug.write(str(fname) + ' ' + str(chroffset) + ' ' + str(len(allele_calls_threshold_strings)) + ' ' + str(len(map_quals_strings)) + ' ' + str(len(base_quals_strings)) + ' ' + '\n' + str(base_quals_list) + '\n' + str(map_quals_list) + '\n' + str(map_quals_strings) + '\n' + str(base_quals_strings) + '\n' + str(allele_calls_threshold_strings) + '\n')
                allele_counts_thresholded = return_acgtdi_list_SAM(ref_index,allele_calls_threshold_strings)
                outf.write(str(chr) + ' ' + str(position) + ' ' + str(chroffset) + ' ' + str(reference_allele) + ' ' + str(ref_index) + ' ' + str(allele_counts_thresholded[0]) + ' ' + str(allele_counts_thresholded[1]) + ' ' + str(allele_counts_thresholded[2]) + ' ' + str(allele_counts_thresholded[3]) + ' ' + str(allele_counts_thresholded[4]) + ' ' + str(allele_counts_thresholded[5]) + ' ' + str(allele_counts_thresholded[6]) + ' ' + str(allele_counts_thresholded[7]) + ' ' + str(allele_counts_thresholded[8]) + ' ' + str(allele_counts_thresholded[9]) + ' ' + str(allele_counts_thresholded[10]) + ' ' + str(allele_counts_thresholded[11]) + '\n')
                if chroffset in dbsnp:
                    mcratefrefdbsnp[chroffset] = allele_counts_thresholded[ref_index]                                                                                                                                                
                    mcratefnonrefdbsnp[chroffset] = sum(allele_counts_thresholded[0:6]) - allele_counts_thresholded[ref_index]                                                                                                       
                    mcraterrefdbsnp[chroffset] = allele_counts_thresholded[ref_index+6]                                                                                                                                              
                    mcraternonrefdbsnp[chroffset] = sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) - allele_counts_thresholded[ref_index+6]                                                                        
                    if sum(allele_counts_thresholded[0:6]) > 0 and sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) > 0:                                                                                             
                        miscallratefwdthresholdeddbsnp.append((sum(allele_counts_thresholded[0:6]) - allele_counts_thresholded[ref_index])/(sum(allele_counts_thresholded[0:6])))                                                    
                        miscallraterevthresholdeddbsnp.append((sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) - allele_counts_thresholded[ref_index+6])/(sum(allele_counts_thresholded[6:len(allele_counts_thresholded)])))                                              
                else :                
                    mcratefref[chroffset] = allele_counts_thresholded[ref_index]
                    mcratefnonref[chroffset] = sum(allele_counts_thresholded[0:6]) - allele_counts_thresholded[ref_index]
                    mcraterref[chroffset] = allele_counts_thresholded[ref_index+6]
                    mcraternonref[chroffset] = sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) - allele_counts_thresholded[ref_index+6]
                    if sum(allele_counts_thresholded[0:6]) > 0 and sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) > 0:
                        miscallratefwdthresholded.append((sum(allele_counts_thresholded[0:6]) - allele_counts_thresholded[ref_index])/(sum(allele_counts_thresholded[0:6])))
                        miscallraterevthresholded.append((sum(allele_counts_thresholded[6:len(allele_counts_thresholded)]) - allele_counts_thresholded[ref_index+6])/(sum(allele_counts_thresholded[6:len(allele_counts_thresholded)])))
                    
                    coverageexp.append(len(allele_calls_list))
                    coveragethresholded.append(sum(allele_counts_thresholded))
                    covgprop = sum(allele_counts_thresholded)/len(allele_calls_list)
               
                    coverageproportion.append(sum(allele_counts_thresholded)/(len(allele_calls_list)))
            avgmiscallraterev = numpy.mean(computeaveragemcrate(miscallraterevthresholded))
            medianmiscallraterev = numpy.median(computeaveragemcrate(miscallraterevthresholded))
            avgmiscallratefwd = numpy.mean(computeaveragemcrate(miscallratefwdthresholded))
            medianmiscallratefwd = numpy.median(computeaveragemcrate(miscallratefwdthresholded))
            outsummary.write(fname + ' has fwd average miscall rate of:' + '\t' + str(avgmiscallraterev) + '\t' + str(avgmiscallratefwd) + '\n') 
            outsummary.write(fname + ' has fwd median miscall rate of:' + '\t' + str(medianmiscallraterev) + '\t' + str(medianmiscallratefwd) + '\n')
            r.plot(miscallratefwdthresholded,miscallraterevthresholded,xlim = r.c(0,1),ylim = r.c(0,1),main = "%s" % fname,xlab = "Forward Miscall rate", ylab = "Reverse Miscall rate")                                             
            r.points(miscallratefwdthresholdeddbsnp,miscallraterevthresholdeddbsnp,col = "blue",pch = 18)                                                                                                                            
            r.plot(miscallratefwdthresholded,miscallraterevthresholded,xlim = r.c(0,.1),ylim = r.c(0,.1),main = "%s" % fname,xlab = "Forward Miscall Rate",ylab = "Reverse Miscall Rate")                                            
            r.points(miscallratefwdthresholdeddbsnp,miscallraterevthresholdeddbsnp,col = "blue",pch = 18)                                                                                                                            
            r.plot(miscallratefwdthresholded,miscallraterevthresholded,xlim = r.c(0,.01),ylim = r.c(0,.01),main = "%s" % fname,xlab = "Forward Miscall Rate",ylab = "Reverse Miscall Rate")                                          
            r.points(miscallratefwdthresholdeddbsnp,miscallraterevthresholdeddbsnp,col = "blue",pch = 18)   
            r.dev_off()
            outsummary.write(fname + ' has Med/Average Coverage of:' + '\t' + str(numpy.median(coverageexp)) + ' ' + str(numpy.mean(coverageexp)) + '\n')
            outsummary.write(fname + ' has Standard Deviation Coverage of:' + '\t' + str(numpy.std(coverageexp)) + '\n')
            outsummary.write(fname + ' has Truncated Med/Average Coverage of:' + '\t' + str(numpy.median(coveragethresholded)) + ' ' + str(numpy.mean(coveragethresholded)) + '\t' + "at Q-val filter of:" + '\t' + str(qthr) + '\n')
            outsummary.write(fname + ' has Truncated Standard Deviation Coverage of:' + '\t' + str(numpy.std(coveragethresholded)) + '\t' + "at Q-val filter of:" + '\t' + str(qthr) + '\n')
            outsummary.write(fname + ' has' + '\t'+ str((len([i for i in coverageproportion if i >= .80])/(len(coverageproportion)))*100) + '\t' + '% of bases recovered with greater than 80% of original coverage'+'\n')
            outsummary.write(fname + ' has' + '\t' + str((len([i for i in coverageproportion if i < .80 and i > .60])/(len(coverageproportion)))*100) + '\t' + '% of bases recovered with greater than 60% of bases but less than 80% of original coverage'+'\n')
            outsummary.write(fname + ' has' + '\t' + str((len([i for i in coverageproportion if i < .40])/(len(coverageproportion)))*100) + '\t' + '% of bases recovered with less than 40% of original coverage'+'\n')
        filenamefinal = os.path.join(options.outputdir,"miscallrate.universal."+ str(qthr) + "%03d.pdf")
        r.pdf(filenamefinal)
        for key in mcratefref:
            mcrateuniversalfwd.append(mcratefnonref[key]/(mcratefref[key] + mcratefnonref[key] + epsilon))
            mcrateuniversalrev.append(mcraternonref[key]/(mcraterref[key] + mcraternonref[key] + epsilon))
        for key in mcratefrefdbsnp:
            mcrateuniversalfwddb.append(mcratefnonrefdbsnp[key]/(mcratefrefdbsnp[key] + mcratefnonrefdbsnp[key] + epsilon))
            mcrateuniversalrevdb.append(mcraternonrefdbsnp[key]/(mcraterrefdbsnp[key] + mcratefnonrefdbsnp[key] + epsilon))
        outsummary.write(fname + ' has rev average miscall rate of:' + '\t' + str(numpy.mean(list(mcrateuniversalfwd)))+ str(numpy.mean(list(mcrateuniversalrev))) + '\n')
        r.plot(mcrateuniversalfwd,mcrateuniversalrev,xlim = r.c(0,1),ylim = r.c(0,1),main = "Miscall Rate %s" % qthr,xlab = "Forward miscall rate",ylab = "Reverse miscall rate")
        r.points(mcrateuniversalfwddb,mcrateuniversalrevdb,col = "blue", pch = 18)
        r.plot(mcrateuniversalfwd,mcrateuniversalrev,xlim = r.c(0,.1),ylim = r.c(0,.1),main = "Miscall Rate %s" % qthr,xlab = "Forward miscall rate",ylab = "Reverse miscall rate")
        r.points(mcrateuniversalfwddb,mcrateuniversalrevdb,col = "blue", pch = 18)
        r.plot(mcrateuniversalfwd,mcrateuniversalrev,xlim = r.c(0,.01),ylim = r.c(0,.01),main = "Miscall Rate %s" % qthr,xlab = "Forward miscall rate",ylab = "Reverse miscall rate")
        r.points(mcrateuniversalfwddb,mcrateuniversalrevdb,col = "blue", pch = 18)
        r.dev_off()
if __name__ == "__main__":
    main()


