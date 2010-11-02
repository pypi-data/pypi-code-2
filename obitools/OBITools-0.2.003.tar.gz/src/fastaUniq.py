#!/usr/local/bin/python


from obitools.fasta import fastaIterator,formatFasta
from obitools.utils.bioseq import uniqSequence,uniqPrefixSequence
from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
from obitools.utils import deprecatedScript

def addUniqOptions(optionManager):
    optionManager.add_option('-m','--merge',
                             action="append", dest="merge",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="ecoPCR taxonomy Database "
                                  "name")
    
    optionManager.add_option('-i','--no-merge-ids',
                             action="store_false", dest="mergeids",
                             default=True,
                             help="don't add the merged id data to output")
    
    optionManager.add_option('-p','--prefix',
                             action="store_true", dest="prefix",
                             default=False,
                             help="two sequences are identical if the shortest one"
                                  " is a prefix of the longest")
    

if __name__=='__main__':
#    try:
#        import psyco
#        psyco.full()
#    except ImportError:
#        pass

#    root.setLevel(DEBUG)

    deprecatedScript('obiuniq')

    optionParser = getOptionManager([addUniqOptions,addTaxonomyDBOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    taxonomy=loadTaxonomyDatabase(options)
    
    if options.prefix:
        usm = uniqPrefixSequence
    else:
        usm= uniqSequence

    uniqSeq=usm(entries,taxonomy,options.merge,options.mergeids)
 
    for seq in uniqSeq:         
        print formatFasta(seq) 
