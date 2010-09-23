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
    
    ranks = set(x for x in tax.rankIterator())
    results = [seq for seq in entries]
    indexbyseq={}
    
    for seq in results:
        s = str(seq)
        if s in indexbyseq:
            indexbyseq[s].add(seq)
        else:
            indexbyseq[s]=set([seq])


    print '%-20s\t%10s\t%10s\t%7s' % ('rank','taxon_ok','taxon_total','percent')
    
    for rank,rankid in ranks:
        if rank != 'no rank':
            indexbytaxid={}
            for seq in results:
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None: 
                    if t in indexbytaxid:
                        indexbytaxid[t].add(str(seq))
                    else:
                        indexbytaxid[t]=set([str(seq)])
                        
            taxoncount=0
            taxonok=0            
            for taxon in indexbytaxid:
                taxlist = set()
                for tag in indexbytaxid[taxon]:
                    taxlist |=set(tax.getTaxonAtRank(x['taxid'],rankid) for x in indexbyseq[tag])
                taxoncount+=1
                if len(taxlist)==1:
                    taxonok+=1
            if taxoncount:
                print '%-20s\t%10d\t%10d\t%8.2f' % (rank,taxonok,taxoncount,float(taxonok)/taxoncount*100)
            
            
    
    