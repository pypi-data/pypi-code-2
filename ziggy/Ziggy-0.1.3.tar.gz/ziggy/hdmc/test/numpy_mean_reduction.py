#! /usr/bin/env python
'''
Created on Jul 29, 2010

@author: dwmclary
'''
import numpy
from scipy import stats
import warnings
import sys
import re
warnings.simplefilter('ignore', DeprecationWarning)

def read_map_input(file, sep=":"):
    for line in file:
        if re.search(":", line):
            lint = line.split(sep)
            type = lint[0]
            if type == "mu" or type =="var":
                data = float(lint[1])
            elif type == "x":
                data = numpy.array(map(float, lint[1].split(",")))
            yield type, data

def main():
    mean_data = read_map_input(sys.stdin)
    
    means = []
    vars = []
    samples = []
    for type, data in mean_data:
        if type == "mu":
            means.append(data)
        elif type == "var":
            vars.append(data)
        elif type == "x":
            samples.append(data)
            
    #get the mean of means
    mu_mu = numpy.mean(numpy.array(means))
    print "mean of means: "+str(mu_mu)
    
    #perform a ks-test on all samples:
    all_samples = numpy.array(samples).flatten()
    print all_samples
    #print 'KS-statistic D = %6.3f pvalue = %6.4f' % stats.kstest(all_samples, 'norm')
    
    #perform a ks-test on each sample:
    for s in range(len(samples)):
        print 'Sample '+str(s)+': KS-statistic D = %6.3f pvalue = %6.4f' % stats.kstest(samples[s], 'norm')
    

if __name__ == '__main__':
    main()
