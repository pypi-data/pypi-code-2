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
import os
def main(argv=None):
    if not argv:
        argv = sys.argv
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-f","--force",
                      action="store_true",dest="force",
                      default=False,
                      help="proceed even with bad extensions")
    parser.add_option("--pif")
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--chr")
    parser.add_option("--ref")
    parser.add_option("--skipannot")
    parser.add_option("--sndb",
                      default = "false")
    parser.add_option("--ncpu")
    parser.add_option("--dbsnp")
    parser.add_option("--bqthr")
    parser.add_option("--sndout",
                      default = 'sndlod.2b')
    parser.add_option("--nonsynonymous", 
                      default="snplist.alleles.ns")
    parser.add_option("--synonymous",
                      default="snplist.alleles.syn")
    parser.add_option("--noncoding",
                      default="snplist.alleles.nc")
    parser.add_option("--utrs",
                      default = "snplist.alleles.utr")
    parser.add_option("--utrsncnt",
                      default="snplist.alleles.utrncnt")
    parser.add_option("--emsummary",
                      default = "EMFreqAssoc.out")
    parser.add_option("--snplist",
                      default="snplist.alleles.readyannot")
    parser.add_option("--fishertablehigh",
                      default="snplist.alleles.high")
    parser.add_option("--module")
    parser.add_option("--fishertablepoor",
                      default="snplist.alleles.poor")
    parser.add_option("--out",
                      default = "PooledExperiment.summary")
    parser.add_option("--outputdir")
    (options, args) = parser.parse_args()


    if not options.force:
        snplist = {}
        snplistallele = {}
        ns = {}
        syn = {}
        utrs = {}
        nc = {}
        utrsnc = {}
        em = {}
        fisherdict = {}
        snpsdict = {}
        snpsrecflt = {}
        emf = open(options.emsummary,'r')
        for emfline in emf:
            emfline = emfline.split()
            chroffset = emfline[0]
            em[chroffset,'chroffset'] = chroffset
            chisqstat = str(emfline[1])
            em[chroffset,'chisqstat'] = chisqstat
            lrtstat = str(emfline[2])
            em[chroffset,'lrtstat'] = lrtstat
            popnrfreq = str(emfline[3])
            em[chroffset,'popnrfreq'] = popnrfreq
            casenrfreq = str(emfline[4])
            em[chroffset,'casenrfreq'] = casenrfreq
            connrfreq = str(emfline[5])
            em[chroffset,'connrfreq'] = connrfreq
            LODstrand = str(emfline[6])
            em[chroffset,'lodstrand'] = LODstrand
            cntsfwd = str(emfline[7])
            em[chroffset,'cntsfwd'] = cntsfwd
            cntsrev = str(emfline[8])
            em[chroffset,'cntsrev'] = cntsrev
        if options.skipannot == "true":
            pass
        else:
            utrf = open(options.utrs,'r')
            for utrline in utrf:
                utrline = utrline.rstrip()
                utrline = utrline.split()
                if len(utrline) > 0:
                    chr = utrline[0]
                    position = utrline[1]
                    chroffset = "chr" + str(chr) + ":" + str(position)
                    utrs[chroffset,'chroffset'] = chroffset
                    gene = utrline[2]
                    utrs[chroffset,'gene'] = str(gene)
                    bc = utrline[3]
                    utrs[chroffset,'bchange'] = str(bc)
                    dist = str(utrline[6])
                    if len(utrline) > 7:
                        rs = str(utrline[7])
                    else:
                        rs = 'NA'
                    utrs[chroffset,'dist'] = dist
                    utrs[chroffset,'rs'] = rs
                    snpsdict[chroffset,'rs'] = rs
            noncodingf = open(options.noncoding,'r')
            for noncodingline in noncodingf:
                noncodingline = noncodingline.rstrip()
                noncodingline = noncodingline.split()
                if len(noncodingline) > 0:
                    chr = noncodingline[0]
                    position = noncodingline[1]
                    chroffset = "chr" + str(chr) + ":" + str(position)
                    nc[chroffset,'chroffset'] = chroffset
                    bc = noncodingline[2]
                    nc[chroffset,'bchange'] = str(bc) 
                    if len(noncodingline) > 4:
                        rs = str(noncodingline[4])
                    else: 
                        rs = 'NA'
                    nc[chroffset,'rs'] = rs
                    snpsdict[chroffset,'rs'] = rs
    

            utrsncntf = open(options.utrsncnt,'r')
            for utrsncntline in utrsncntf:
                utrsncntline = utrsncntline.rstrip()
                utrsncntline = utrsncntline.split()
                if len(utrsncntline) > 0:
                    chr = utrsncntline[0]
                    position = utrsncntline[1]
                    chroffset = "chr" + str(chr) + ":" + str(position)
                    utrsnc[chroffset,'chroffset'] = chroffset
                    gene = utrsncntline[2]
                    utrsnc[chroffset,'gene'] = str(gene)
                    bc = utrsncntline[3]
                    utrsnc[chroffset,'bchange'] = str(bc)
                    dist = str(utrsncntline[7])
                    if len(utrsncntline) > 8:
                        rs = str(utrsncntline[8])
                    else:
                        rs = 'NA'
                    utrsnc[chroffset,'dist'] = dist
                    utrsnc[chroffset,'rs'] = rs
                    snpsdict[chroffset,'rs'] = rs

        fisherhigh = open(options.fishertablehigh,'r')
        fisherdict = {}
        for fisherline in fisherhigh:
            fisherline = fisherline.rstrip()
            fisherline = fisherline.split()
            if "chr" in chroffset:
                chroffset = fisherline[0]
            else:
                chroffset = "chr" + fisherline[0]
           # bool = fisherline[1]
            medlrtstat = fisherline[1]
            if chroffset in fisherdict:
                fisherdict[chroffset].append(medlrtstat)
            else:
                fisherdict[chroffset] = []
                fisherdict[chroffset].append(medlrtstat)
        
        fisherpoor = open(options.fishertablepoor,'r')
        for fisherline in fisherpoor:
            fisherline = fisherline.rstrip()
            fisherline = fisherline.split()
            if "chr" in chroffset:
                chroffset = fisherline[0]
            else:
                chroffset = "chr" + fisherline[0]
           # bool = fisherline[1]
            medlrtstat = fisherline[1]
            if chroffset in fisherdict:
                fisherdict[chroffset].append(medlrtstat)
            else:
                fisherdict[chroffset] = []
                fisherdict[chroffset].append(medlrtstat)
        



        if options.skipannot == "true":
            pass
        else:
            nonsyn = open(options.nonsynonymous,'r')
            for nonsynline in nonsyn:
                nonsynline = nonsynline.rstrip()
                nonsynline = nonsynline.split()
                if len(nonsynline) > 0:
                    chr = nonsynline[0]
                    position = nonsynline[1]
                    chroffset = "chr" + str(chr) + ":" + str(position)
                    ns[chroffset,'chroffset'] = chroffset
                    gene = nonsynline[2]
                    ns[chroffset,'gene'] = str(gene)
                    bc = nonsynline[3]
                    ns[chroffset,'bchange'] = str(bc)
                    annot = nonsynline[4]
                   
                    ns[chroffset,'annot'] = str(annot)
                    if len(nonsynline) > 5:
                        rs = nonsynline[5]
                    else:
                        rs = 'NA'
                    ns[chroffset,'rs'] = str(rs)
                    snpsdict[chroffset,'rs'] = rs
            synf = open(options.synonymous,'r')
            for synline in synf:
                synline = synline.rstrip()
                synline = synline.split()
                if len(synline) > 0:
                    chr = synline[0]
                    position = synline[1]
                    if "chr" in chr:
                        chroffset = str(chr) + ":" + str(position)
                    else:
                        chroffset = "chr" + str(chr) + ":" + str(position)
                    syn[chroffset,'chroffset'] = chroffset
                    gene = synline[2]
                    syn[chroffset,'gene'] = str(gene)
                    bc = synline[3]
                    syn[chroffset,'bchange'] = str(bc)
                    annot = synline[4]
                  
                    syn[chroffset,'annot'] = str(annot)
                    if len(synline) > 5:
                        rs = synline[5]
                    else:
                        rs = 'NA'
                    syn[chroffset,'rs'] = str(rs)
                    snpsdict[chroffset,'rs'] = rs
                
        sndlst = {}
        if options.sndb == 'true':
            sndfilepath = os.path.join(options.outputdir,options.sndout)
            sndfileread = open(sndfilepath,'r')
            for line in sndfileread:
                line = line.rstrip()
                line = line.split()
                chroffset = line[0]
                sndfwd = line[1]
                sndrev = line[2]
                sndcomb = line[3]
                sndlst[chroffset] = chroffset
                sndlst[chroffset,'fwd'] = sndfwd
                sndlst[chroffset,'rev'] = sndrev
                sndlst[chroffset,'comb'] = float(sndcomb)
        outpath = os.path.join(options.outputdir,str(options.out))
        outfile = open(outpath,'w')
        outfile.write('chr:position alleles gene type rs# base_chg annot dist pop_nr_freq f_nr_case f_nr_con chisqstat_assoc lrt_stat f+ f- SLOD p_val\n')
        snpfile = open(options.snplist,'r')
        snpfileread = snpfile.readlines()
        exptsummary = {}
        highS = 0
        highdbS = 0
        highNS = 0
        highSyn = 0
        low2bS = 0
        low2bdbS = 0
        low2bNS = 0
        low2bSyn = 0
        lowS = 0
        lowdbS = 0
        lowNS = 0
        lowSyn = 0
        medS = 0
        meddbS = 0
        medNS = 0
        medSyn = 0
        medCS = 0 
        medCdbS = 0
        medCNS = 0 
        medCSyn = 0
        propN = {}
        propN['TC','high'] = 0
        propN['CT','high'] = 0
        propN['CT','medC'] = 0
        propN['TC','medC'] = 0
        propN['TC','med'] = 0
        propN['CT','med'] = 0
        propN['TC','low'] = 0
        propN['CT','low'] = 0
        propN['TC','low2b'] = 0
        propN['CT','low2b'] = 0  
        propN['GA','high'] = 0
        propN['AG','high'] = 0
        propN['GA','med'] = 0
        propN['AG','med'] = 0
        propN['GA','medC'] = 0
        propN['AG','medC'] = 0
        propN['GA','low2b'] = 0
        propN['AG','low2b'] = 0
        
        propN['GA','low'] = 0
        propN['AG','low'] = 0
        propN['CA','high'] = 0
        propN['AC','high'] = 0
        propN['CA','med'] = 0
        propN['AC','med'] = 0
        propN['CA','medC'] = 0
        propN['AC','medC'] = 0 
        propN['CA','low'] = 0
        propN['AC','low'] = 0
        propN['CA','low2b'] = 0
        propN['AC','low2b'] = 0
        
        propN['CG','high'] = 0
        propN['GC','high'] = 0
        propN['CG','med'] = 0
        propN['GC','med'] = 0
        propN['CG','medC'] = 0
        propN['GC','medC'] = 0
        propN['CG','low'] = 0
        propN['GC','low'] = 0
        propN['CG','low2b'] = 0
        propN['GC','low2b'] = 0        
        
        propN['GT','high'] = 0
        propN['TG','high'] = 0
        propN['GT','med'] = 0
        propN['TG','med'] = 0
        propN['GT','medC'] = 0
        propN['TG','medC'] = 0
        propN['GT','low'] = 0
        propN['TG','low'] = 0
        propN['GT','low2b'] = 0
        propN['TG','low2b'] = 0        
        
        propN['TA','high'] = 0
        propN['AT','high'] = 0
        propN['TA','med'] = 0
        propN['AT','med'] = 0
        propN['TA','medC'] = 0
        propN['AT','medC'] = 0
        propN['TA','low'] = 0
        propN['AT','low'] = 0
        propN['TA','low2b'] = 0
        propN['AT','low2b'] = 0       
        
        clusters = {}
        # We are going to populate a dictionary with fisher < .1 filtered from summary . Include only fisher > .1.
        snpcandidfisher = {}
        for snpline in snpfileread[1:]:
            snpline = snpline.rstrip()
            snpline = snpline.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            chroffsetsnp = str(chr) + ':' + str(pos)
            snplist[chroffsetsnp] = chroffsetsnp
            snplistallele[chroffsetsnp,'ref'] = snpline[5][0]
            snplistallele[chroffsetsnp,'nonref'] = snpline[5][1]
            if (float(fisherdict[chroffsetsnp][0]) >= .1):
                snpcandidfisher[chroffsetsnp] = chroffsetsnp
        for snpline in snpfileread[1:]:
            snpline = snpline.rstrip()
            snpline = snpline.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            snplistallele[chroffsetsnp,'ref'] = snpline[5][0]
            snplistallele[chroffsetsnp,'nonref'] = snpline[5][1]
            chroffsetsnp = str(chr) + ':' + str(pos)
            if chroffsetsnp in exptsummary:
                pass
            else:
                exptsummary[chroffsetsnp] = em[chroffsetsnp,'lodstrand']
                refallele = snplistallele[chroffsetsnp,'ref']
                transition = str(snplistallele[chroffsetsnp,'ref']) + str(snplistallele[chroffsetsnp,'nonref'])
                if float(exptsummary[chroffsetsnp]) > 5 or (float(fisherdict[chroffsetsnp][0]) < .1):
                    snpsrecflt[chroffsetsnp] = 1

                    lowS += 1
                    if (chroffsetsnp,'rs') in snpsdict:
                        if "rs" in snpsdict[chroffsetsnp,'rs']:
                            lowdbS += 1
                    if (refallele,'low') in propN:
                        propN[refallele,'low'] += 1
                    else:
                        propN[refallele,'low'] = 0
                        propN[refallele,'low'] += 1
                    if (transition,'low') in propN:
                        propN[transition,'low'] += 1
                    else:
                        propN[transition,'low'] = 0
                        propN[transition,'low'] += 1
                    if (chroffsetsnp,'chroffset') in ns:
                        lowNS += 1

                    elif (chroffsetsnp,'chroffset') in syn:
                        lowSyn += 1
                elif options.sndb == 'true' and chroffsetsnp in sndlst and sndlst[chroffsetsnp,'comb'] >= 5:
                    low2bS += 1
                    snpsrecflt[chroffsetsnp] = 1
                    if (chroffsetsnp,'rs') in snpsdict:
                        if "rs" in snpsdict[chroffsetsnp,'rs']:
                            low2bdbS += 1
                    if (refallele,'low2b') in propN:
                        propN[refallele,'low2b'] += 1
                    else:
                        propN[refallele,'low2b'] = 0
                        propN[refallele,'low2b'] += 1
                    if (transition,'low2b') in propN:
                        propN[transition,'low2b'] += 1
                    else:
                        propN[transition,'low2b'] = 0
                        propN[transition,'low2b'] += 1
                    if (chroffsetsnp,'chroffset') in ns:
                        low2bNS += 1

                    elif (chroffsetsnp,'chroffset') in syn:
                        low2bSyn += 1
                        
                elif checkcluster(chroffsetsnp,snpcandidfisher,clusters) == 'true':
                    medCS += 1
                    snpsrecflt[chroffsetsnp] = 2
                    if (chroffsetsnp,'rs') in snpsdict:
                        if "rs" in snpsdict[chroffsetsnp,'rs']:
                            medCdbS += 1
                    if (refallele,'medC') in propN:
                        propN[refallele,'medC'] += 1
                    else:
                        propN[refallele,'medC'] = 0
                        propN[refallele,'medC'] += 1
                    if (transition,'medC') in propN:
                        propN[transition,'medC'] += 1
                    else:
                        propN[transition,'medC'] = 0
                        propN[transition,'medC'] += 1
                    if (chroffsetsnp,'chroffset') in ns:
                        medCNS += 1
                    elif (chroffsetsnp,'chroffset') in syn:
                        medCSyn += 1
                    
                    
                    
                elif (float(exptsummary[chroffsetsnp]) < 0) and (float(fisherdict[chroffsetsnp][0]) >= .1):
                    highS += 1
                    snpsrecflt[chroffsetsnp] = 0
                    if (chroffsetsnp,'rs') in snpsdict:
                        if "rs" in snpsdict[chroffsetsnp,'rs']:
                            highdbS += 1
                    if (refallele,'high') in propN:
                        propN[refallele,'high'] += 1
                    else:
                        propN[refallele,'high'] = 0
                        propN[refallele,'high'] += 1
                    if (transition,'high') in propN:
                        propN[transition,'high'] += 1
                    else:
                        propN[transition,'high'] = 0
                        propN[transition,'high'] += 1
                    if (chroffsetsnp,'chroffset') in ns:
                        
                        highNS += 1
                    elif (chroffsetsnp,'chroffset') in syn:
                        highSyn += 1
                elif float(exptsummary[chroffsetsnp]) >= 0 and float(exptsummary[chroffsetsnp]) <= 5 and (float(fisherdict[chroffsetsnp][0]) >= .1):
                    snpsrecflt[chroffsetsnp] = 3
                    medS += 1
                    if (chroffsetsnp,'rs') in snpsdict:
                        if "rs" in snpsdict[chroffsetsnp,'rs']:
                            meddbS += 1
                    if (refallele,'med') in propN:
                        propN[refallele,'med'] += 1
                    else:
                        propN[refallele,'med'] = 0
                        propN[refallele,'med'] += 1
                    if (transition,'med') in propN:
                        propN[transition,'med'] += 1
                    else:
                        propN[transition,'med'] = 0
                        propN[transition,'med'] += 1
                    if (chroffsetsnp,'chroffset') in ns:
                        medNS += 1

                    elif (chroffsetsnp,'chroffset') in syn:
                        medSyn += 1



            em[chroffsetsnp,'chisqstat'] = float(em[chroffsetsnp,'chisqstat'])
            em[chroffsetsnp,'lrtstat'] = abs(float(em[chroffsetsnp,'lrtstat']))
            em[chroffsetsnp,'cntsfwd'] = float(em[chroffsetsnp,'cntsfwd'])
            em[chroffsetsnp,'cntsrev'] = float(em[chroffsetsnp,'cntsrev'])
            if (chroffsetsnp,'chroffset') in ns:
                outfile.write(ns[chroffsetsnp,'chroffset'] + ' ' + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + ns[chroffsetsnp,'gene'] + ' '  + 'ns' + ' ' + ns[chroffsetsnp,'rs'] + ' ' + ns[chroffsetsnp,'bchange'] + ' ' + ns[chroffsetsnp,'annot'] + ' ' + 'NA' + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' ' + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev'])  +  em[chroffsetsnp,'lodstrand'] + ' ' + str(fisherdict[chroffsetsnp][0]))
            elif (chroffsetsnp,'chroffset') in syn:
                outfile.write(syn[chroffsetsnp,'chroffset'] + ' ' + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + syn[chroffsetsnp,'gene'] + ' '  + 's' + ' ' + syn[chroffsetsnp,'rs'] + ' ' + syn[chroffsetsnp,'bchange'] + ' ' + syn[chroffsetsnp,'annot'] + ' ' + 'NA' + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' '  + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev']) + em[chroffsetsnp,'lodstrand'] +  ' ' + str(fisherdict[chroffsetsnp][0]) )

            elif (chroffsetsnp,'chroffset') in utrs:
                outfile.write(utrs[chroffsetsnp,'chroffset'] + ' ' + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + utrs[chroffsetsnp,'gene'] + ' '  + 'utrsnc' + ' ' + utrs[chroffsetsnp,'rs'] + ' ' + utrs[chroffsetsnp,'bchange'] + ' ' + 'NA' + ' ' + utrs[chroffsetsnp,'dist'] + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' ' + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev']) + em[chroffsetsnp,'lodstrand'] +  ' ' + str(fisherdict[chroffsetsnp][0]) )

            elif (chroffsetsnp,'chroffset') in utrsnc:
                outfile.write(utrsnc[chroffsetsnp,'chroffset'] + ' '  + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + utrsnc[chroffsetsnp,'gene'] + ' '  + 'utrsnc' + ' ' + utrsnc[chroffsetsnp,'rs'] + ' ' + utrsnc[chroffsetsnp,'bchange'] + ' ' + 'NA' + ' ' + utrsnc[chroffsetsnp,'dist'] + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' ' + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev']) + em[chroffsetsnp,'lodstrand'] +  ' ' + str(fisherdict[chroffsetsnp][0]) )

            elif (chroffsetsnp,'chroffset') in nc:
                outfile.write(nc[chroffsetsnp,'chroffset'] + ' ' + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + 'NA' + ' '  + 'nc' + ' ' + nc[chroffsetsnp,'rs'] + ' ' + nc[chroffsetsnp,'bchange'] + ' ' + 'NA' + ' ' + 'NA' + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' ' + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev']) + em[chroffsetsnp,'lodstrand'] +  ' ' + str(fisherdict[chroffsetsnp][0]) )
            else:
                snpsdict[chroffsetsnp,'rs'] = 'NA'
                outfile.write(str(chroffsetsnp) + ' ' + str(snplistallele[chroffsetsnp,'ref'] + snplistallele[chroffsetsnp,'nonref']) + ' ' + 'NA' + ' '  + 'NA' + ' ' + 'NA' + ' ' + 'NA' + ' ' + 'NA' + ' ' + 'NA' + ' ' + em[chroffsetsnp,'popnrfreq'] + ' ' + em[chroffsetsnp,'casenrfreq'] + ' ' + em[chroffsetsnp,'connrfreq'] + ' ' + ("%4.4g %4.4g %4.4g %4.4g ") % (em[chroffsetsnp,'chisqstat'],em[chroffsetsnp,'lrtstat'],em[chroffsetsnp,'cntsfwd'] ,em[chroffsetsnp,'cntsrev']) + em[chroffsetsnp,'lodstrand'] +  ' ' + str(fisherdict[chroffsetsnp][0]) )
            if options.sndb == 'true':
                outfile.write('\t' + str(sndlst[chroffsetsnp,'fwd']) + ' ' + str(sndlst[chroffsetsnp,'rev']) + ' ' + str(sndlst[chroffsetsnp,'comb']) + '\t' + str(snpsrecflt[chroffsetsnp]) + '\n')
            else:
                outfile.write('\t' + str(snpsrecflt[chroffsetsnp]) + '\n')
        if options.sndb == 'true':
            dbsnplow2b = low2bdbS/(low2bS + 1)*100
            nsslow2b = low2bNS/(low2bSyn + 1)
            translow2b = (propN['TC','low2b'] + propN['CT','low2b'] + propN['GA','low2b'] + propN['AG','low2b'])/(propN['AC','low2b'] + propN['CA','low2b'] + propN['CG','low2b'] + propN['GC','low2b'] + propN['GT','low2b'] + propN['TG','low2b'] + propN['TA','low2b'] + propN['AT','low2b'] + 1)
            
        dbsnphigh = highdbS/(highS + 1)*100
        dbsnpmedC = medCdbS/(medCS + 1)*100
        dbsnpmed = meddbS/(medS + 1)*100
        dbsnplow = lowdbS/(lowS + 1)*100
        nsshigh = highNS/(highSyn + 1) 
        nssmedC = medCNS/(medCSyn + 1)
        nssmed =  medNS/(medSyn + 1)
        nsslow =  lowNS/(lowSyn + 1)
        transhigh = (propN['TC','high'] + propN['CT','high'] + propN['GA','high'] + propN['AG','high'])/(propN['AC','high'] + propN['CA','high'] + propN['CG','high'] + propN['GC','high'] + propN['GT','high'] + propN['TG','high'] + propN['TA','high'] + propN['AT','high'] + 1)
        transmed = (propN['TC','med'] + propN['CT','med'] + propN['GA','med'] + propN['AG','med'])/(propN['AC','med'] + propN['CA','med'] + propN['CG','med'] + propN['GC','med'] + propN['GT','med'] + propN['TG','med'] + propN['TA','med'] + propN['AT','med'] + 1)
        transmedC = (propN['TC','medC'] + propN['CT','medC'] + propN['GA','medC'] + propN['AG','medC'])/(propN['AC','medC'] + propN['CA','medC'] + propN['CG','medC'] + propN['GC','medC'] + propN['GT','medC'] + propN['TG','medC'] + propN['TA','medC'] + propN['AT','medC'] + 1)
        translow = (propN['TC','low'] + propN['CT','low'] + propN['GA','low'] + propN['AG','low'])/(propN['AC','low'] + propN['CA','low'] + propN['CG','low'] + propN['GC','low'] + propN['GT','low'] + propN['TG','low'] + propN['TA','low'] + propN['AT','low'] + 1)
        if options.sndb == 'true':
            outfile.write('Summary of Experiment\n')
            outfile.write('type\thigh( S < 0)\tlow(0 <= S <= 5)\tlow(Clusters_FLT)\tlow(2bLOD_FLT)\tFLT((S> 5)or(medpval<.1))\n')
            outfile.write('Counts-' +  ("%4.4g\n")  % (highS + medS + medCS + low2bS +  lowS))
            outfile.write('Counts-' +  ("%4.4g\t%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (highS,medS,medCS,low2bS,lowS))
            outfile.write('dbsnp-\t' + ("%4.4g\t%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (dbsnphigh,dbsnpmed,dbsnpmedC,dbsnplow2b,dbsnplow))
            outfile.write('ns/s-\t' +  ("%4.4g\t%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (nsshigh,nssmed,nssmedC,nsslow2b,nsslow)) 
            outfile.write('transition/Transversion-\t' + ("%4.4g\t%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (transhigh,transmed,transmedC,translow2b,translow)) 
        else:
            outfile.write('Summary of Experiment\n')
            outfile.write('type\thigh( S < 0)\tlow(0 <= S <= 5)\tlow(Clusters)\tFLT((S> 5)or(medpval<.1))\n')
            outfile.write('Counts-' +  ("%4.4g\n")  % (highS + medS + medCS + lowS))
            outfile.write('Counts-' +  ("%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (highS,medS,medCS,lowS))
            outfile.write('dbsnp-\t' + ("%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (dbsnphigh,dbsnpmed,dbsnpmedC,dbsnplow))
            outfile.write('ns/s-\t' +  ("%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (nsshigh,nssmed,nssmedC,nsslow)) 
            outfile.write('transition/Transversion-\t' + ("%4.4g\t%4.4g\t%4.4g\t%4.4g\n") % (transhigh,transmed,transmedC,translow)) 
        outfile.write('Codes for Filters: 0 - Very High Quality, 1 - Poor Quality (SLOD , 2bLOD, strand), 2 - In Cluster, 3 - Moderate Quality\n')
if __name__ == "__main__":
    main()


