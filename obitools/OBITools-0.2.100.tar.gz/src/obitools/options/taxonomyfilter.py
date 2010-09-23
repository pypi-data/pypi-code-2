from obitools.ecopcr.taxonomy import Taxonomy, EcoTaxonomyDB, TaxonomyDump, ecoTaxonomyWriter


def addTaxonomyDBOptions(optionManager):
    optionManager.add_option('-d','--database',
                             action="store", dest="taxonomy",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR taxonomy Database "
                                  "name")
    optionManager.add_option('-t','--taxonomy-dump',
                             action="store", dest="taxdump",
                             metavar="<FILENAME>",
                             type="string",
                             help="NCBI Taxonomy dump repository "
                                  "name")

    
def addTaxonomyFilterOptions(optionManager):
    addTaxonomyDBOptions(optionManager)
    optionManager.add_option('--require-rank',
                             action="append", 
                             dest='requiredRank',
                             metavar="<RANK_NAME>",
                             type="string",
                             default=[],
                             help="select sequence with taxid tag containing "
                                  "a parent of rank <RANK_NAME>")
     
    optionManager.add_option('-r','--required',
                             action="append", 
                             dest='required',
                             metavar="<TAXID>",
                             type="int",
                             default=[],
                             help="required taxid")
     
    optionManager.add_option('-i','--ignore',
                             action="append", 
                             dest='ignored',
                             metavar="<TAXID>",
                             type="int",
                             default=[],
                             help="ignored taxid")
     
def loadTaxonomyDatabase(options):
    if options.taxonomy is not None or options.taxdump is not None:
        if options.taxdump is not None:
            taxonomy = TaxonomyDump(options.taxdump)
            if isinstance(options.taxonomy, str):
                ecoTaxonomyWriter(options.taxonomy,taxonomy)
                options.ecodb=options.taxonomy
        elif isinstance(options.taxonomy, Taxonomy):
            taxonomy = options.taxonomy
        elif isinstance(options.taxonomy, str):
            taxonomy = EcoTaxonomyDB(options.taxonomy)
            options.ecodb=options.taxonomy
        options.taxonomy=taxonomy
    return options.taxonomy
    
def taxonomyFilterGenerator(options):
    loadTaxonomyDatabase(options)
    if options.taxonomy is not None:
        taxonomy=options.taxonomy
        def taxonomyFilter(seq):
            def annotateAtRank(seq,rank):
                if 'taxid' in seq and seq['taxid'] is not None:
                    rtaxid= taxonomy.getTaxonAtRank(seq['taxid'],rank)
                    return rtaxid
                return None
            good = True
            if 'taxid' in seq:
                taxid = seq['taxid']
#                print taxid,
                if options.requiredRank:
                    taxonatrank = reduce(lambda x,y: x and y,
                                         (annotateAtRank(seq,rank) is not None
                                            for rank in options.requiredRank),True)
                    good = good and taxonatrank 
#                    print >>sys.stderr, " Has rank : ",good,
                if options.required:
                    good = good and reduce(lambda x,y: x or y,
                                  (taxonomy.isAncestor(r,taxid) for r in options.required),
                                  False)
#                    print " Required : ",good,
                if options.ignored:
                    good = good and not reduce(lambda x,y: x or y,
                                  (taxonomy.isAncestor(r,taxid) for r in options.ignored),
                                  False)
#                    print " Ignored : ",good,
#                print " Global : ",good
                    
            return good
            
            
    else:
        def taxonomyFilter(seq):
            return True
 
    return taxonomyFilter
       
def taxonomyFilterIteratorGenerator(options):
    taxonomyFilter = taxonomyFilterGenerator(options)
    
    def filterIterator(seqiterator):
        for seq in seqiterator:
            if taxonomyFilter(seq):
                yield seq
                
    return filterIterator