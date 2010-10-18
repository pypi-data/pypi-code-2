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
from rpy2.rpy_classic import *
from SAMpileuphelper import *
from statslib import *
import sys,re
import os

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
    parser.add_option("--dosage",
                      default="snps.dosage")
    parser.add_option("--summaryfile",
                      default="PooledExperiment.summary")
    parser.add_option("--dbsnp")
    parser.add_option("--tgf")
    parser.add_option("--hg")
    parser.add_option("--samtoolspath")
    parser.add_option("--skipannot")
    parser.add_option("--mqthr")
    parser.add_option("--module")
    parser.add_option("--chr")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--outputdir")
    parser.add_option("--bqthr")
    parser.add_option("--alpha",
                      default = .05)
    parser.add_option("--SLOD",
                      default = 5)
    
    
    
    parser.add_option("--out",
                      help = "Outputs Table and Plots of Statistics",
                      default = "RareTest.Calpha")
    parser.add_option("--rarethr",
                      help = "Rare Variant Frequency Threshold",
                      default = .049)
    parser.add_option("--plots",
                      help = "Boolean : TRUE or FALSE to generate diagnostic plots", 
                      default = "TRUE")
    parser.add_option("--bds",
                      help = "Parameter to add extra boundary values to assignments", 
                      default = 25)
    
    (options, args) = parser.parse_args()
   
   
    if not options.force: 
        set_default_mode(BASIC_CONVERSION)
        alpha = float(options.alpha)
        snpsall = {}
        caseall = {}
        dbsnp ={}
        rarelist = {}
        rarethr = float(options.rarethr)
        bounds = int(options.bds)
        minvariant = 2
        snpdict = {}
        
        slctgenebds = {}
        genechr = {}
        summarypath = os.path.join(options.outputdir,str(options.summaryfile))
        summaryread = open(summarypath,'r').readlines()
        pifread = open(options.pif,'r').readlines()
        allchroms = 0
        casechrom = 0
        controlchrom = 0
        for pifline in pifread[1:]:
            pifline = pifline.rstrip()
            pifline = pifline.split()
            bam = pifline[0]
            phenotype = int(pifline[1])
            inds = int(pifline[2])
            chroms = int(pifline[3])
            allchroms += chroms
            if phenotype == 0:
                controlchrom += chroms
            elif phenotype == 1:
                casechrom += chroms
        maxvariant = int(numpy.ceil(float(options.rarethr)*(allchroms)))
        
        for summaryline in summaryread[1:]:
            summaryline = summaryline.rstrip()
            summaryline = summaryline.split()
            if "chr" in summaryline[0]:
                chroffsetsnp = summaryline[0]
                gene = summaryline[2]
                type = summaryline[3]
                (chr,position) = chroffsetsnp.split(":")
                position = int(position)
                SLOD = float(summaryline[15])
                fisher = float(summaryline[16])
                filterflag = int(summaryline[17])
                snpdict[chroffsetsnp,'SLOD'] = SLOD
                snpdict[chroffsetsnp,'fisher'] = fisher
              
                if float(SLOD) < float(options.SLOD) and float(fisher) > .1 and filterflag == 0:
                    genechr[gene]  = chr
                    if gene in slctgenebds:
                        slctgenebds[gene].append(position)
                    else:
                        slctgenebds[gene] = []
                        slctgenebds[gene].append(position)
                    snpdict[chroffsetsnp,'cases'] = int(numpy.round(float(summaryline[9])*casechrom))
                    snpdict[chroffsetsnp,'control'] = int(numpy.round(float(summaryline[10])*controlchrom))
                    snpsall[chroffsetsnp] = int(snpdict[chroffsetsnp,'cases']) + int(snpdict[chroffsetsnp,'control'])
                    caseall[chroffsetsnp] = int(snpdict[chroffsetsnp,'cases'])
            elif ":" in summaryline[0]:
                chroffsetsnp = "chr" + summaryline[0]
                SLOD = float(summaryline[15])
                fisher = float(summaryline[16])
                snpdict[chroffsetsnp,'SLOD'] = SLOD
                snpdict[chroffsetsnp,'fisher'] = fisher
              
                if float(SLOD) < 5 and float(fisher) > .1:
                    snpdict[chroffsetsnp,'cases'] = int(numpy.round(float(summaryline[9])*casechrom))
                    snpdict[chroffsetsnp,'control'] = int(numpy.round(float(summaryline[10])*controlchrom))
                    snpsall[chroffsetsnp] = int(snpdict[chroffsetsnp,'cases']) + int(snpdict[chroffsetsnp,'control'])
                    caseall[chroffsetsnp] = int(snpdict[chroffsetsnp,'cases'])
                
            else:
                pass       
       # dosagepath = os.path.join(options.outputdir,str(options.dosage))
       # snpdosageread = open(dosagepath,'r')
       
        #snpfileread = snpdosageread.readlines()
        if options.plots == "TRUE": 
            r.pdf(options.out + '.pdf')
        else:
            pass
        """
         @Read SNP File 
        """
        
        rarelist = return_rarelist(snpsall,minvariant,maxvariant)
        exonfileread = open(options.tgf,'r')
        exonfileread = exonfileread.readlines()
        outfilewrite = open(options.out,'w')
        outfilemix = open(options.out + '.mix','w')
        outfilegenewrite = open(options.out + '.gene','w')
        outfilegenemix = open(options.out + '.mix.gene','w')
        significantregionswrite = open(options.out + '.regions' , 'w')
        outfilegenewrite.write('exonid\tchr\tstart\tend\tcalphastat\tpval\tmixtureweight\tprobcomponent\n')
        outfilegenemix.write('chr:offset\tcalphastat\tpval\tcases\tcontrol\tMix1W1 Mix2W1 Mix2W2 Mix3W1 Mix3W2 Mix3W3\n')
       
        #Remove Comment after attempt 
        #phatest = return_phat(rarelist,snpsall,caseall)
       
        phatest = casechrom/(casechrom + controlchrom)
        thetaest = reparameterize(phatest)
     
            
        """
         Compute the Calpha Statistic for Pooled Sequencing Data -- Initialize with Genes, then Exons
        """
        for key in slctgenebds.keys():
            probarray = r.seq(0,1,.01)
            feature = key
            if "chr" in genechr[feature]:
                chr = genechr[feature]
            else:
                chr = "chr" + str(genechr[feature])
            print slctgenebds[feature]
            start = int(numpy.min(slctgenebds[feature])) - 3
            stop = int(numpy.max(slctgenebds[feature])) + 3
            size = stop - start
            print feature,start,stop
            rarelistregion = {}
            rarelistregion = return_rarelist_region(rarelist,start,stop,chr,bounds)
            
            (mnum, calphastatnum) = Calpha_GenTnewF(snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds)
            
            (std,calphastatdenom) = Calpha_GenCnew(snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds)
            
            if len(rarelistregion.keys()) >= 1:
                (weightsprobdict,probcompvec,mixtureweight) = return_EM_paramsfixedneut(probarray,snpsall,caseall,chr,start,stop,rarelistregion,minvariant,maxvariant,thetaest,phatest,bounds)
            else:
                probcompvec = []
                mixtureweight = []
            
           # print std
           # print calphastatnum,calphastatdenom
            calphastat = calphastatnum/numpy.sqrt(calphastatdenom)
            meanstat = 1/2*numpy.sqrt(calphastatdenom)
            pval = 1 - r.pnorm(calphastat)[0]
        
            
            outfilegenewrite.write(("%s %s %s %s %4.4g %4.3g") % (feature,chr,start,stop,calphastat,pval))
            for i in mixtureweight:
                for j in i: 
                    
                    outfilegenewrite.write(("%4.3g ") % (j))
                outfilegenewrite.write(" ")
            outfilegenewrite.write("\t")
            for i in probcompvec:
           
                for j in i:
                    
                    outfilegenewrite.write(("%4.3g ") % (j))
                outfilegenewrite.write(" ")
           
            
            
            for key in rarelistregion.keys():
                outfilegenemix.write(("%s %4.4g %4.4g %4.4g %4.4g %4.4g %3.3g %3.3g %3.3g %3.3g %3.3g %3.3g %3.3g\n") % (key,calphastat,pval,caseall[key],snpsall[key]-caseall[key],weightsprobdict['1',key,'1'],weightsprobdict['2',key,'1b'],weightsprobdict['2',key,'2b'] ,weightsprobdict['2',key,'1d'] ,weightsprobdict['2',key,'2d'] ,weightsprobdict['3',key,'1'] ,weightsprobdict['3',key,'2'],weightsprobdict['3',key,'3'] ))
                
            """
            Generate Homogeneity and Residual Plots
            """
            probarray = r.seq(0,1,.01)
             
            (gradientarray1,gradientarray2a,gradientarray2b,gradientarray3) = return_gradient(probarray,snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds,probcompvec,mixtureweight)
            Kmixture = ChooseKGradDiag(pval,alpha,gradientarray1,gradientarray2a,gradientarray2b,gradientarray3,probarray,probcompvec)
            outfilegenewrite.write(str(Kmixture) + "\n")
            if options.plots == "TRUE":
                
                #  r.plot(mixturenumbers,diagnosticseffects, main = "Diagnostic Plot for Rare Variant Effects %s,%s" % (feature,calpha) , xlim = r.c( 0 ,5), xlab = "Mixture Numbers", ylab = "Diagnostic Numbers")
                r.plot(probarray,gradientarray1, main = "Gradient Descent K = 1%s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray2a, main = "Gradient Descent K = 2 Ben %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray2b, main = "Gradient Descent K = 2 Det %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray3, main = "Gradient Descent K = 3 Ben %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
    #Exons
        for exonline in exonfileread[1:]:
            probarray = r.seq(0,1,.01)
            exonline = exonline.rstrip()
            exonline = exonline.split()
            feature = exonline[0]
            if "chr" in exonline[1]:
                chr = exonline[1]
            else:
                chr = "chr" + str(exonline[1])
            
            start = int(exonline[2])
            stop = int(exonline[3])
            size = exonline[4]
            rarelistregion = {}
            rarelistregion = return_rarelist_region(rarelist,start,stop,chr,bounds)
            
            # Let's remove this for now . We will come back to this in a bit. 
            #(calphanum,calphadenom) = stat_calpha(snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds)
            
            
            
            (mnum,calphastatnum) = Calpha_GenTnewF(snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds)
    
            (std,calphastatdenom) = Calpha_GenCnew(snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds)
            
            if len(rarelistregion.keys()) >= 1:
                (weightsprobdict,probcompvec,mixtureweight) = return_EM_params(probarray,snpsall,caseall,chr,start,stop,rarelistregion,minvariant,maxvariant,thetaest,phatest,bounds)
            else:
                probcompvec = []
                mixtureweight = []
            
            #calphastat = calphanum/numpy.sqrt(calphadenom)
            
            calphastat = calphastatnum/numpy.sqrt(calphastatdenom)
            pval = 1 - r.pnorm(calphastat)[0]
        
            
        
            
            outfilewrite.write(("%s %s %s %s %4.4g %4.3g") % (feature,chr,start,stop,calphastat,pval))
            for i in mixtureweight:
                for j in i:  
                    outfilewrite.write(("%4.3g ") % (j))
                outfilewrite.write(" ")
            outfilewrite.write("\t")
            for i in probcompvec:
                for j in i:
                    outfilewrite.write(("%4.3g ") % (j))
                outfilewrite.write(" ")
           
            
            
            for key in rarelistregion.keys():
                outfilemix.write(("%s %4.4g %4.4g %4.4g %4.4g %4.4g %3.3g %3.3g %3.3g %3.3g %3.3g %3.3g %3.3g\n") % (key,calphastat,pval,caseall[key],snpsall[key]-caseall[key],weightsprobdict['1',key,'1'],weightsprobdict['2',key,'1b'],weightsprobdict['2',key,'2b'] ,weightsprobdict['2',key,'1d'] ,weightsprobdict['2',key,'2d'] ,weightsprobdict['3',key,'1'] ,weightsprobdict['3',key,'2'],weightsprobdict['3',key,'3'] ))
                
            """
            Generate Homogeneity and Residual Plots
            """
            probarray = r.seq(0,1,.01)
             
            (gradientarray1,gradientarray2a,gradientarray2b,gradientarray3) = return_gradient(probarray,snpsall,caseall,chr,start,stop,rarelist,minvariant,maxvariant,thetaest,phatest,bounds,probcompvec,mixtureweight)
            Kmixture = ChooseKGradDiag(pval,alpha,gradientarray1,gradientarray2a,gradientarray2b,gradientarray3,probarray,probcompvec)
            outfilewrite.write(str(Kmixture) + "\n")
            if options.plots == "TRUE":
                
                #  r.plot(mixturenumbers,diagnosticseffects, main = "Diagnostic Plot for Rare Variant Effects %s,%s" % (feature,calpha) , xlim = r.c( 0 ,5), xlab = "Mixture Numbers", ylab = "Diagnostic Numbers")
                r.plot(probarray,gradientarray1, main = "Gradient Descent K = 1%s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray2a, main = "Gradient Descent K = 2 Ben %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray2b, main = "Gradient Descent K = 2 Det %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                r.plot(probarray,gradientarray3, main = "Gradient Descent K = 3 Ben %s, %s" % (feature, calphastat)  , xlab = "Binomial p" , ylab = "Gradient", xlim = r.c(0,1), type = "l")
                
                
                
        if options.plots == "TRUE":
            r.dev_off()
        outfilewrite.close()
        outfilemix.close()
        outfilegenewrite.close()
        outfilegenemix.close()
        
            
if __name__ == "__main__":
    main()     
        
        