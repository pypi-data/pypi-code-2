def addSequenceEditTagOptions(optionManager):
    
    optionManager.add_option('-R','--rename-tag',
                             action="append", 
                             dest='renameTags',
                             metavar="<OLD_NAME:NEW_NAME>",
                             type="string",
                             default=[],
                             help="change tag name from OLD_NAME to NEW_NAME")

    optionManager.add_option('--delete-tag',
                             action="append", 
                             dest='deleteTags',
                             metavar="<TAG_NAME>",
                             type="string",
                             default=[],
                             help="delete tag TAG_NAME")

    optionManager.add_option('-S','--set-tag',
                             action="append", 
                             dest='setTags',
                             metavar="<TAG_NAME:PYTHON_EXPRESSION>",
                             type="string",
                             default=[],
                             help="Add a new tag named TAG_NAME with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('--set-identifier',
                             action="store", 
                             dest='setIdentifier',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence identifier with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('-T','--set-definition',
                             action="store", 
                             dest='setDefinition',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence definition with "
                                  "a value computed from PYTHON_EXPRESSION")
    
    optionManager.add_option('-O','--only-valid-python',
                             action="store_true", 
                             dest='onlyValid',
                             default=False,
                             help="only valid python expressions are allowed")
    
    optionManager.add_option('-C','--clear',
                             action="store_true", 
                             dest='clear',
                             default=False,
                             help="clear all tags associated to the sequences")
    
    optionManager.add_option('-k','--keep',
                             action='append',
                             dest='keep',
                             default=[],
                             type="string",
                             help="only keep this tag")
    
    optionManager.add_option('--length',
                             action="store_true", 
                             dest='length',
                             default=False,
                             help="add seqLength tag with sequence length")
    
    optionManager.add_option('--with-taxon-at-rank',
                             action='append',
                             dest='taxonrank',
                             default=[],
                             type="string",
                             help="add taxonomy annotation at a speciefied rank level")
    
  


def sequenceTaggerGenerator(options):
    toDelete = options.deleteTags[:]
    toRename = [x.split(':',1) for x in options.renameTags if len(x.split(':',1))==2]
    toSet    = [x.split(':',1) for x in options.setTags if len(x.split(':',1))==2]
    newId    = options.setIdentifier
    newDef   = options.setDefinition
    clear    = options.clear
    keep     = set(options.keep)
    length   = options.length
    if options.taxonomy is not None:
        annoteRank=options.taxonrank
    else:
        annoteRank=[]
    
    def sequenceTagger(seq):
        if clear or keep:
            ks = seq.keys()
            for k in ks:
                if k not in keep:
                    del seq[k]
        else:
            for i in toDelete:
                if i in seq:
                    del seq[i]                
            for o,n in toRename:
                if o in seq:
                    seq[n]=seq[o]
                    del seq[o]
        for i,v in toSet:
            try:
                val = eval(v,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = v
            seq[i]=val
            
        if length:
            seq['seqLength']=len(seq)
            
        if newId is not None:
            try:
                val = eval(newId,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newId
            seq.id=val
        if newDef is not None:
            try:
                val = eval(newDef,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newDef
            seq.definition=val
        for rank in annoteRank:
            if 'taxid' in seq:
                taxid = seq['taxid']
                if taxid is not None:
                    rtaxid = options.taxonomy.getTaxonAtRank(taxid,rank)
                    if rtaxid is not None:
                        scn = options.taxonomy.getScientificName(rtaxid)
                    else:
                        scn=None
                    seq[rank]=rtaxid
                    seq["%s_name"%rank]=scn 
        return seq
    
    return sequenceTagger