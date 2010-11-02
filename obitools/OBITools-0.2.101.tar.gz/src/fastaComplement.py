#!/usr/local/bin/python
'''
-----------------------------------
 fastaComplement.py
-----------------------------------
fastaComplement.py <fastafile>
    complement and reverse all sequence in the fasta file
-----------------------------------"
-h    --help                       : print this help
-----------------------------------"
'''


from obitools.fasta import fastaNucIterator,formatFasta
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.utils import deprecatedScript


if __name__=='__main__':
    
    deprecatedScript('obicomplement')
    
    optionParser = getOptionManager([addSequenceFilteringOptions],
                                    entryIterator=fastaNucIterator
                                    )
    
    (options, entries) = optionParser()
    
    goodFasta = filterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            print formatFasta(seq.complement())
        else:
            print formatFasta(seq)

            