#!/usr/local/bin/python
'''
Created on 6 juil. 2010

@author: coissac
'''
from obitools.format.options import addInOutputOption, printOutput
from obitools.options import getOptionManager
from obitools.format.sequence import autoSequenceIterator

def addSelectOptions(optionManager):
    
    optionManager.add_option('-i','--identifier',
                             action="store", dest="identifier",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing sample sequences to select on "
                                  "on the base of their identifier")




if __name__ == '__main__':
    optionParser = getOptionManager([addSelectOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    
    idset=set(x.id for x in  autoSequenceIterator(options.identifier))
    
    for seq in entries:
        if seq.id in idset:
            printOutput(options,seq)
        
