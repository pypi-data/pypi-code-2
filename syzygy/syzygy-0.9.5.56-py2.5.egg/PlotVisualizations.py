
#!/usr/bin/python

from __future__ import division


# Written by Manuel A. Rivas
# Updated 08.11.2009

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
#import rpy2.robjects as robjects
import pp
import time
import os
from os import popen

def main(argv=None):
    if not argv:
        argv = sys.argv
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    parser.add_option("-f","--force",
                      action="store_true",dest="force",
                      default=False,
                      help="proceed even with bad extensions")
  
    parser.add_option("--pif")
    parser.add_option("--skipannot")
    parser.add_option("--module")
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--bqthr")
    parser.add_option("--chr")
    parser.add_option("--mqthr")
    parser.add_option("--sndb")
    parser.add_option("--dbsnp")
    parser.add_option("--heatmap",
                      default="heatmap.exon.matrix")
    parser.add_option("--pf",
                      default = "PooledExperiment.pf")
    parser.add_option("--outputdir")
    (options, args) = parser.parse_args()
    
    if not options.force: 
        set_default_mode(BASIC_CONVERSION)
        powerfile = open(options.pf,'r')
        powerfile = powerfile.readlines()
        poolfile = open(options.pif,'r').readlines()
        pooldesc = {}
        coveragehelp = {}
        chromosomeavg = 0
        pools = 0
        tgfread = open(options.tgf,'r').readlines()
        exonmap = {}
        for line in tgfread[1:]:
            line = line.rstrip()
            line = line.split()
            feature = line[0]
            chr = line[1]
            start = int(line[2])
            end = int(line[3])
            if "chr" in chr:
                chrom = chr
            else:
                chrom = "chr" + str(chr)
            for i in range(start - 5, end + 6):
                chroffset = chrom + ":" + str(i)
                exonmap[chroffset] = feature
        coverageexon = {}
        exoncov = {}
        for line in poolfile[1:]:
            pools += 1
            line = line.rstrip()
            line = line.split()
            bampool = line[0]
            phenotype = int(line[1])
            inds = int(line[2])
            chroms = int(line[3])
            chromosomeavg += chroms
            pooldesc[bampool,'name'] = bampool
            pooldesc[bampool,'phenotype'] = phenotype
            pooldesc[bampool,'inds'] = inds
            pooldesc[bampool,'chroms'] = chroms 
            fname = str(line[0]) + '.combined.error.coverage.calls'
            filenamer = open(fname,'r')
            filenameread = filenamer.readlines()
            for line in filenameread[1:]:
                line = line.rstrip()
                line = line.split()
                if "chr" in line[0]:
                    chroffset = line[0]
                else:
                    chroffset = "chr" + str(line[0])
                ref_base = line[1]
                ref_allele = str(line[16])
                alt_allele = str(line[17])
                allelespos = str(ref_allele) + str(alt_allele)
                coverage = int(line[18])
                if chroffset in coveragehelp:
                    coveragehelp[chroffset].append(coverage)
                else:
                    coveragehelp[chroffset] = []
                    coveragehelp[chroffset].append(coverage)
                if chroffset in exonmap:
                    if (exonmap[chroffset],bampool) in coverageexon: 
                        coverageexon[exonmap[chroffset],bampool].append(coverage)
                    else:
                        coverageexon[exonmap[chroffset],bampool] = []
                        coverageexon[exonmap[chroffset],bampool].append(coverage)
                        exoncov[exonmap[chroffset]] = exonmap[chroffset]
                    
                lodfwd = float(line[19])
                lodrev = float(line[20])
                lod = float(line[21])
                fisherflag = line[22]
        chromosomemean = chromosomeavg/pools       
        header = powerfile[0]
     
        header = header.rstrip()
       
        header = header.split()
      
        poolmap = {}
        for i in range(2,len(header)):
            print header[i]
            poolmap[i] = header[i]
        powermiss = {}
        powerdict = {}
        powerexon = {}
        exons =  {}
        for powerline in powerfile[1:]:
            powerline = powerline.rstrip()
            powerline = powerline.split()
            chroffset = powerline[0]
            exon = powerline[1]
            exons[exon] = exon
            powerlist = [float(j) for j in powerline[2:]]
            case = []
            control = []
    
            for i in range(2,len(powerline)):
                if pooldesc[poolmap[i],'phenotype'] == 1:
                    case.append(powerlist[i-2])
                elif pooldesc[poolmap[i],'phenotype'] == 0:
                    control.append(powerlist[i-2])
                
                
                if poolmap[i] in powerdict:
                    powerdict[poolmap[i]].append(powerlist[i-2])
                    
                else:
                    powerdict[poolmap[i]] = []
                    powerdict[poolmap[i]].append(powerlist[i-2])
                
                if (exon,poolmap[i]) in powerexon:
                    powerexon[exon,poolmap[i]].append(powerlist[i-2])
                else:
                    powerexon[exon,poolmap[i]] = []
                    powerexon[exon,poolmap[i]].append(powerlist[i-2])
            if len(case) > 0:
                if 'case' in powermiss and len(powermiss['case']) > 0:
                    powermiss['case'].append(pmisspower(case))
                else:
                    powermiss['case'] = []
                    powermiss['case'].append(pmisspower(case))
            if len(control) > 0:
                if 'control' in powermiss and len(powermiss['control']) > 0:
                    powermiss['control'].append(pmisspower(control))
                else:
                    powermiss['control'] = []
                    powermiss['control'].append(pmisspower(control))
            
            
        casexprobmiss = r.seq(0,100,10)
        powerxseq = r.seq(0,100,10)
        caseypropsites = []
        controlxprobmiss = r.seq(0,100,10)
        controlypropsites = []
        poolpropsites = {}
        r.pdf('Power%03d.pdf')
        legendtext = []
        legendcol = []
        heatmapwrite = os.path.join(options.outputdir,options.heatmap)
        heatmapcovwrite = os.path.join(options.outputdir,options.heatmap)
        heatmapw = open(heatmapwrite,'w')
        heatmapcovw = open(heatmapcovwrite + '.cov','w')
        heatmapw.write("Exon ")
        heatmapcovw.write("Exon ")
        for keymap in poolmap.keys():
            heatmapw.write(str(poolmap[keymap]) + " ")
            heatmapcovw.write(str(poolmap[keymap]) + " ")
        heatmapw.write("\n")
        heatmapcovw.write("\n")
        for keyexon in exons.keys():
            
            heatmapw.write(str(keyexon) + " ")
            if keyexon in exoncov.keys():
                heatmapcovw.write(str(keyexon) + " ")
            for keymap in poolmap.keys():
                if (keyexon,poolmap[keymap]) in coverageexon:
                    heatmapcovw.write(("%4.4g ") % (len([i for i in coverageexon[keyexon,poolmap[keymap]] if int(i) >= int(pooldesc[poolmap[keymap],'chroms'])])/len(coverageexon[keyexon,poolmap[keymap]])))
                elif keyexon in exoncov.keys(): 
                    heatmapcovw.write(("%4.4g ") % (0))
                heatmapw.write(("%4.4g ") % (numpy.mean(powerexon[keyexon,poolmap[keymap]])/float(100)))
            heatmapw.write("\n")
            if keyexon in exoncov.keys():
                heatmapcovw.write("\n")
        ltynum = 0
        for key in poolmap.keys():
           
            poolpropsites[poolmap[key]] = []
            
            for i in range(0,len(powerxseq)):
                poolpropsites[poolmap[key]].append(len([j for j in powerdict[poolmap[key]] if int(j) >= int(powerxseq[i])])/len(powerdict[poolmap[key]])*100)
                                                        
            if key == 2:
                legendtext.append(str(poolmap[key]))
                legendcol.append(r.ceiling(653/key)[0])
                r.plot(powerxseq,poolpropsites[poolmap[key]],xlim = r.c(0,100),ylim = r.c(0,100), xlab = "Power to Detect a Singleton (>=)", ylab = "Proportion of Sites", col = r.c(r.ceiling(653/key)), lwd = 2, type = "l" )
            else:
                legendtext.append(str(poolmap[key]))
                legendcol.append(r.ceiling(653/key)[0])
                r.lines(powerxseq,poolpropsites[poolmap[key]], col = r.c(r.ceiling(653/key)), lwd = 3 )
            ltynum += 1  
        r.legend(0,40,r.c(legendtext),fill = r.c(legendcol),lwd = 2,cex = 0.55)
        if 'case' in powermiss:
            for i in range(0,len(casexprobmiss)):
                caseypropsites.append(len([j for j in powermiss['case'] if j >= casexprobmiss[i]])/len(powermiss['case'])*100)
        if 'control' in powermiss:
            for i in range(0,len(controlxprobmiss)):
                controlypropsites.append(len([j for j in powermiss['control'] if j >= controlxprobmiss[i]])/len(powermiss['control'])*100)
        
        if 'case' in powermiss and 'control' in powermiss:
            r.plot(casexprobmiss,caseypropsites,xlim = r.c(0,100),ylim = r.c(0,100),xlab = "Probability to miss a singleton", ylab = "Proportion of Sites",col = "red", lwd = 3,type = "l")
            r.lines(controlxprobmiss,controlypropsites,col = "blue", lwd = 2)
            r.legend(75,100,r.c("Case","Control"),col = r.c("red","blue"),lwd = 3)
        elif 'case' in powermiss:
            r.plot(casexprobmiss,caseypropsites,xlim = r.c(0,100),ylim = r.c(0,100),xlab = "Probability to Miss a Singleton", ylab = "Proportion of Sites",col = "red", lwd = 3, type = "l")
            r.legend(75,100,r.c("Case"),col = r.c("red"),lwd = 3)
        elif 'control' in powermiss:
            r.plot(controlxprobmiss,controlypropsites,xlim = r.c(0,100),ylim = r.c(0,100),xlab = "Probability to Miss a Singleton", ylab = "Proportion of Sites",col = "blue", lwd = 2,type = "l")
            r.legend(75,100,r.c("Control"),col = r.c("blue"),lwd = 3)
        r.dev_off()
    
    
    
    
    
    
    



if __name__ == "__main__":
    main()