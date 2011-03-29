#!/usr/local/bin/python
'''
Created on 1 nov. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.sample import weigthedSample
from obitools.format.options import addInOutputOption, sequenceWriterGenerator

def addSampleOptions(optionManager):
    optionManager.add_option('-s','--sample-size',
                             action="store", dest="size",
                             metavar="###",
                             type="int",
                             default=None,
                             help="Size of the generated sample"
                             )
 


if __name__ == '__main__':

    optionParser = getOptionManager([addSampleOptions,addInOutputOption]
                                    )
    
    (options, entries) = optionParser()
    
    db = [s for s in entries]
    
    if options.size is None:
        options.size=len(db)
        
    distribution = {}
    idx=0
    
    for s in db:
        if 'count' in s:
            count = s['count']
        else:
            count = 1
        distribution[idx]=count
        idx+=1
        
    sample =weigthedSample(distribution, options.size)

    writer = sequenceWriterGenerator(options)
    
    for idx in sample:
        seq = db[idx]
        seq['count']=sample[idx]
        writer(seq)
        
        

