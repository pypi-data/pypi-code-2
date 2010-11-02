#!/usr/local/bin/python

from obitools.ecopcr import taxonomy
from obitools.ecopcr import sequence
from obitools.ecopcr import EcoPCRFile

from obitools.options import getOptionManager



def addTaxonomyOptions(optionManager):
        
    optionManager.add_option('-d','--ecopcrdb',
                             action="store", dest="db",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR Database "
                                  "name")

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyOptions],
                                    entryIterator=EcoPCRFile
                                    )
    
    (options, entries) = optionParser()
    
    tax = taxonomy.EcoTaxonomyDB(options.db)
    seqd= sequence.EcoPCRDBSequenceIterator(options.db,taxonomy=tax)
    
    ranks = set(x for x in tax.rankIterator())
    
    listtaxonbyrank = {}
    
    for seq in seqd:
        for rank,rankid in ranks:
            if rank != 'no rank':
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None:
                    if rank in listtaxonbyrank:
                        listtaxonbyrank[rank].add(t)
                    else:
                        listtaxonbyrank[rank]=set([t])
                        
    stats = dict((x,len(listtaxonbyrank[x])) for x in listtaxonbyrank)
    
    listtaxonbyrank = {}
        
    for seq in entries:
        for rank,rankid in ranks:
            if rank != 'no rank':
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None:
                    if rank in listtaxonbyrank:
                        listtaxonbyrank[rank].add(t)
                    else:
                        listtaxonbyrank[rank]=set([t])

    dbstats= dict((x,len(listtaxonbyrank[x])) for x in listtaxonbyrank)
    
    ranknames = [x[0] for x in ranks]
    ranknames.sort()
    
    print '%-20s\t%10s\t%10s\t%7s' % ('rank','ecopcr','db','percent')
    
    for r in ranknames:
        if  r in dbstats and dbstats[r]:
            print '%-20s\t%10d\t%10d\t%8.2f' % (r,dbstats[r],stats[r],float(dbstats[r])/stats[r]*100)
            
     

