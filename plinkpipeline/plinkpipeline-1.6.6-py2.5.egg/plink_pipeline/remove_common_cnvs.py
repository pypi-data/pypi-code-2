##!/util/bin/python
#
#import sys
#
#print sys.path
#sys.exit(1)
#
#import numpy
#from numpy import *
#import scipy
#import pylab
#
#def computeMax(stringVals):
#    max = -inf
#    for s in stringVals:
#        f = float(s)
#        if(f>max):
#            max = f
#    return max
#
#overlap_dist = float(sys.argv[3])
#overlap_pct = float(sys.argv[4])
#
##load common cnps:
#commoncnps = pylab.load(sys.argv[5],skiprows=1)
##only keep those CNPs with an allele frequency above 2% in at least one pop:
#cnpstotoss = zeros(shape(commoncnps)[0])
#freqfile = open(sys.argv[6],'r')
#freqfile.readline()
#for line in freqfile:
#    values = line.split()
#    if(computeMax(values[4:]) < 0.02):
#        cnpstotoss[where(commoncnps[:,0]==int(values[0]))] = 1
#freqfile.close()
#commoncnps = commoncnps[cnpstotoss==0,1:4]
#
##remove segments that appear to be in common cnp list:
#cnvfile = open(sys.argv[1],'r')
#outfile = open(sys.argv[2],'w')
#for line in cnvfile:
#    values = line.split()
#    #find out if this is a common event or not:
#    #-->in order to filter out small events that are broken pieces of a large CNP, instead of taking the union, just take the size of the test CNV
#    #-->also, require it to be within overlap_dist on outside (i.e. if larger), but anywhere in the middle (i.e. if smaller)
#    chrcnps = commoncnps[commoncnps[:,0]==float(values[3]),:]
#    bigstart = chrcnps[:,1].clip(float(values[4]),Inf)
#    smallstart = chrcnps[:,1].clip(0,float(values[4]))
#    bigend = chrcnps[:,2].clip(float(values[5]),Inf)
#    smallend = chrcnps[:,2].clip(0,float(values[5]))
#    overlap = smallend-bigstart
#    #union = bigend-smallstart
#    union = float(values[5])-float(values[4])
#    #startdiff = bigstart-smallstart
#    startdiff = chrcnps[:,1]-float(values[4])
#    #enddiff = bigend-smallend
#    enddiff = float(values[5]) - chrcnps[:,2]
#    if(not((((overlap/union)>overlap_pct) & (startdiff<overlap_dist) & (enddiff<overlap_dist)).any())):
#        print >> outfile, line,
#
#
