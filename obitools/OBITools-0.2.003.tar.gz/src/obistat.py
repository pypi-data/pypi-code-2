#!/usr/local/bin/python
'''
Created on 2 fevr. 2010

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.format.options import addInputFormatOption
import sys

def addStatOptions(optionManager):
    optionManager.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of"
                                  " attribute used for categorizing sequences")
    
    optionManager.add_option('-m','--min',
                             action="append", dest="minimum",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute minimum of attribute")
    
    optionManager.add_option('-M','--max',
                             action="append", dest="maximum",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute maximum of attribute")

    optionManager.add_option('-a','--mean',
                             action="append", dest="mean",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute mean of attribute")

    
def statistics(values,attribute,func):
    stat={}
    lstat={}
    
    for var in attribute:
        if var in values:
            stat[var]={}
            lstat[var]=0
            for c in values[var]:
                v = values[var][c]
                m = func(v)
                stat[var][c]=m
                lm=len(str(m))
                if lm > lstat[var]:
                    lstat[var]=lm
                
    return stat,lstat

def minimum(values,options):
    return statistics(values, options.minimum, min)
    

def maximum(values,options):
    return statistics(values, options.maximum, max)

def mean(values,options):
    def average(v):
        s = reduce(lambda x,y:x+y,v,0)
        return float(s)/len(v)
    return statistics(values, options.mean, average)


if __name__ == "__main__":
    optionParser = getOptionManager([addStatOptions,addInputFormatOption])
    
    (options, entries) = optionParser()
    
    options.statistics = set(options.minimum) | set(options.maximum) | set(options.mean)
    total = 0
    catcount={}
    values={}
    lcat=0
    
    for s in entries:
        category = []
        for c in options.categories:
            if c in s:
                v = s[c]
                lv=len(str(v))
                if lv > lcat:
                    lcat=lv
                category.append(v)
            else:
                category.append(None)
                if 4 > lcat:
                    lcat=4
        category=tuple(category)
        catcount[category]=catcount.get(category,0)+1
        for var in options.statistics:
            if var in s:
                v = s[var]
                if var not in values:
                    values[var]={}
                if category not in values[var]:
                    values[var][category]=[]
                values[var][category].append(v)
                
    
    mini,lmini = minimum(values, options)
    maxi,lmaxi = maximum(values, options)
    avg ,lavg  = mean(values, options)
    
            
    pcat  = "%%-%ds" % lcat
    if options.minimum:
        minvar= "min_%%-%ds" % max(len(x) for x in options.minimum)
    else:
        minvar= "%s"
        
    if options.maximum:
        maxvar= "max_%%-%ds" % max(len(x) for x in options.maximum)
    else:
        maxvar= "%s"
        
    if options.mean:
        meanvar= "mean_%%-%ds" % max(len(x) for x in options.mean)
    else:
        meanvar= "%s"
        
    hcat = "\t".join([pcat % x for x in options.categories]) + "\t" +\
           "\t".join([minvar % x for x in options.minimum])  + "\t" +\
           "\t".join([maxvar % x for x in options.maximum])  + "\t" +\
           "\t".join([meanvar % x for x in options.mean]) + \
           "\t   count" 
    print hcat
    for c in catcount:
        for v in c:
            print pcat % str(v)+"\t",
        for m in options.minimum:
            print (("%%%dd" % lmini[m]) % mini[m][c])+"\t",
        for m in options.maximum:
            print (("%%%dd" % lmaxi[m]) % maxi[m][c])+"\t",
        for m in options.mean:
            print (("%%%df" % lavg[m]) % avg[m][c])+"\t",
        print "%7d" %catcount[c]
                    

