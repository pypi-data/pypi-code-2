import struct
import sys

from itertools import count,imap

from obitools.ecopcr import EcoPCRDBFile
from obitools.utils import universalOpen
from obitools.utils import ColumnFile

class Taxonomy(object):
    def __init__(self):
        '''
        The taxonomy database constructor
        
        @param path: path to the ecoPCR database including the database prefix name
        @type path: C{str}
        '''
        self._speciesidx = self._ranks.index('species')
        self._genusidx   = self._ranks.index('genus')
        self._familyidx   = self._ranks.index('family')
        self._orderidx   = self._ranks.index('order')
        self._nameidx=dict((x[0],x[2]) for x in self._name)

    def findTaxonByTaxid(self,taxid):
        if taxid is None:
            return None
        taxid = self._index[taxid]
        
        if taxid is None:
            return None

        return self._taxonomy[taxid]
    
    def findTaxonByName(self,name):
        return self._taxonomy[self._nameidx[name]]
    
    
    
    def findRankByName(self,rank):
        try:
            return self._ranks.index(rank)
        except ValueError:
            return None
        
    def findIndex(self,taxid):
        return self._index[taxid]


    #####
    #
    # PUBLIC METHODS
    #
    #####


    def subTreeIterator(self, taxid):
        "return subtree for given taxonomic id "
        idx = self._index[taxid]
        yield self._taxonomy[idx]
        for t in self._taxonomy:
            if t[2] == idx:
                for subt in self.subTreeIterator(t[0]):
                    yield subt
    
    def parentalTreeIterator(self, taxid):
        """
           return parental tree for given taxonomic id starting from
           first ancester to the root.
        """
        taxon=self.findTaxonByTaxid(taxid)
        if taxon is not None:
            while taxon[2]!= 0: 
                yield taxon
                taxon = self._taxonomy[taxon[2]]
            yield self._taxonomy[0]
        else:
            raise StopIteration
        
    def isAncestor(self,parent,taxid):
        return parent in [x[0] for x in self.parentalTreeIterator(taxid)]
    
    def lastCommonTaxon(self,*taxids):
        if not taxids:
            return None
        if len(taxids)==1:
            return taxids[0]
         
        if len(taxids)==2:
            t1 = [x[0] for x in self.parentalTreeIterator(taxids[0])]
            t2 = [x[0] for x in self.parentalTreeIterator(taxids[1])]
            t1.reverse()
            t2.reverse()
            
            count = min(len(t1),len(t2))
            i=0
            while(i < count and t1[i]==t2[i]):
                i+=1
            i-=1
            
            return t1[i]
        
        ancetre = taxids[0]
        for taxon in taxids[1:]:
            ancetre = self.lastCommonTaxon(ancetre,taxon)
            
        return ancetre
    
    def betterCommonTaxon(self,error=1,*taxids):
        lca = self.lastCommonTaxon(*taxids)
        idx = self._index[lca]
        sublca = [t[0] for t in self._taxonomy if t[2]==idx]
        dist={}
        return sublca
    
    def getScientificName(self,taxid):
        return self.findTaxonByTaxid(taxid)[3]
    
    def getRankId(self,taxid):
        return self.findTaxonByTaxid(taxid)[1]
    
    def getRank(self,taxid):
        return self._ranks[self.getRankId(taxid)]
    
    def getTaxonAtRank(self,taxid,rankid):
        if isinstance(rankid, str):
            rankid=self._ranks.index(rankid)
        try:
            return [x[0] for x in self.parentalTreeIterator(taxid)
                    if x[1]==rankid][0]
        except IndexError:
            return None
        
    def getSpecies(self,taxid):
        return self.getTaxonAtRank(taxid, self._speciesidx)
    
    def getGenus(self,taxid):
        return self.getTaxonAtRank(taxid, self._genusidx)
    
    def getFamily(self,taxid):
        return self.getTaxonAtRank(taxid, self._familyidx)
    
    def getOrder(self,taxid):
        return self.getTaxonAtRank(taxid, self._orderidx)
    
    def rankIterator(self):
        for x in imap(None,self._ranks,xrange(len(self._ranks))):
            yield x

    def groupTaxa(self,taxa,groupname):
        t=[self.findTaxonByTaxid(x) for x in taxa]
        a=set(x[2] for x in t)
        assert len(a)==1,"All taxa must have the same parent"
        newtaxid=max([2999999]+[x[0] for x in self._taxonomy if x[0]>=3000000 and x[0]<4000000])+1
        newidx=len(self._taxonomy)
        if 'MOTU' not in self._ranks:
            self._ranks.append('MOTU')
        rankid=self._ranks.index('MOTU')
        self._taxonomy.append((newtaxid,rankid,a.pop(),groupname))
        for x in t:
            x[2]=newidx

class EcoTaxonomyDB(Taxonomy,EcoPCRDBFile):
    '''
    A taxonomy database class
    '''
    
    
    def __init__(self,path):
        '''
        The taxonomy database constructor
        
        @param path: path to the ecoPCR database including the database prefix name
        @type path: C{str}
        '''
        self._path = path
        self._taxonFile =  "%s.tdx" % self._path
        self._ranksFile =  "%s.rdx" % self._path
        self._namesFile =  "%s.ndx" % self._path
        self._aliasFile =  "%s.adx" % self._path
        
        print >> sys.stderr,"Reading binary taxonomy database...",
        
        self.__readNodeTable()
        
        print >> sys.stderr," ok"
        
        Taxonomy.__init__(self)
        

    #####
    #
    # Iterator functions
    #
    #####
                   
    def __ecoNameIterator(self):
        for record in self._ecoRecordIterator(self._namesFile):
            lrecord = len(record)
            lnames  = lrecord - 16
            (isScientificName,namelength,classLength,indextaxid,names)=struct.unpack('> I I I I %ds' % lnames, record)
            name=names[:namelength]
            classname=names[namelength:]
            yield (name,classname,indextaxid)
    
    
    def __ecoTaxonomicIterator(self):
        for record in self._ecoRecordIterator(self._taxonFile):
            lrecord = len(record)
            lnames  = lrecord - 16
            (taxid,rankid,parentidx,nameLength,name)=struct.unpack('> I I I I %ds' % lnames, record)
            yield  (taxid,rankid,parentidx,name)
                
    def __ecoRankIterator(self):
        for record in self._ecoRecordIterator(self._ranksFile):
            yield  record
    
    def __ecoAliasIterator(self):
        for record in self._ecoRecordIterator(self._aliasFile):
            (taxid,index) = struct.unpack('> I I',record)
            yield taxid,index
            
    #####
    #
    # Indexes
    #
    #####
    
    def __ecoNameIndex(self):
        indexName = [x for x in self.__ecoNameIterator()]
        return indexName

    def __ecoRankIndex(self):
        rank = [r for r in self.__ecoRankIterator()]
        return rank

    def __ecoTaxonomyIndex(self):
        taxonomy = []
        
        try :
            index = dict(self.__ecoAliasIterator())
            print >> sys.stderr, " [Alias file found] ",
            buildIndex=False
        except:
            print >> sys.stderr, " [Alias file not found] ",
            index={}
            i = 0;
            buildIndex=True
            
            
        for x in self.__ecoTaxonomicIterator():
            taxonomy.append(x)
            if buildIndex:
                index[x[0]] = i 
                i+=1
        return taxonomy, index

    def __readNodeTable(self):
        self._taxonomy, self._index = self.__ecoTaxonomyIndex()
        self._ranks = self.__ecoRankIndex()
        self._name = self.__ecoNameIndex()
    

class TaxonomyDump(Taxonomy):  
        
    def __init__(self,taxdir):
        
        self._path=taxdir
        self._readNodeTable('%s/nodes.dmp' % taxdir)
        
        print >>sys.stderr,"Adding scientific name..."
    
        self._name=[]
        for taxid,name,classname in self._nameIterator('%s/names.dmp' % taxdir):
            self._name.append((name,classname,self._index[taxid]))
            if classname == 'scientific name':
                self._taxonomy[self._index[taxid]].append(name)
            
        print >>sys.stderr,"Adding taxid alias..."
        for taxid,current in self._mergedNodeIterator('%s/merged.dmp' % taxdir):
            self._index[taxid]=self._index[current]
        
        print >>sys.stderr,"Adding deleted taxid..."
        for taxid in self._deletedNodeIterator('%s/delnodes.dmp' % taxdir):
            self._index[taxid]=None
            
    def _taxonCmp(t1,t2):
        if t1[0] < t2[0]:
            return -1
        elif t1[0] > t2[0]:
            return +1
        return 0
    
    _taxonCmp=staticmethod(_taxonCmp)
    
    def _bsearchTaxon(self,taxid):
        taxCount = len(self._taxonomy)
        begin = 0
        end   = taxCount 
        oldcheck=taxCount
        check = begin + end / 2
        while check != oldcheck and self._taxonomy[check][0]!=taxid :
            if self._taxonomy[check][0] < taxid:
                begin=check
            else:
                end=check
            oldcheck=check
            check = (begin + end) / 2
            
            
        if self._taxonomy[check][0]==taxid:
            return check
        else:
            return None
            
    
    
    def _readNodeTable(self,file):
    
        file = universalOpen(file)
        
        nodes = ColumnFile(file, 
                           sep='|', 
                           types=(int,int,str,
                                  str,str,bool,
                                  int,bool,int,
                                  bool,bool,bool,str))
        print >>sys.stderr,"Reading taxonomy dump file..."
            # (taxid,rank,parent)
        taxonomy=[[n[0],n[2],n[1]] for n in nodes]
        print >>sys.stderr,"List all taxonomy rank..."    
        ranks =list(set(x[1] for x in taxonomy))
        ranks.sort()
        rankidx = dict(map(None,ranks,xrange(len(ranks))))
        
        print >>sys.stderr,"Sorting taxons..."
        taxonomy.sort(TaxonomyDump._taxonCmp)

        self._taxonomy=taxonomy
    
        print >>sys.stderr,"Indexing taxonomy..."
        index = {}
        for t in self._taxonomy:
            index[t[0]]=self._bsearchTaxon(t[0])
        
        print >>sys.stderr,"Indexing parent and rank..."
        for t in self._taxonomy:
            t[1]=rankidx[t[1]]
            t[2]=index[t[2]]
         
        self._ranks=ranks
        self._index=index 

    def _nameIterator(self,file):
        file = universalOpen(file)
        names = ColumnFile(file, 
                           sep='|', 
                           types=(int,str,
                                  str,str))
        for taxid,name,unique,classname,white in names:
            yield taxid,name,classname
                        
    def _mergedNodeIterator(self,file):
        file = universalOpen(file)
        merged = ColumnFile(file, 
                           sep='|', 
                           types=(int,int,str))
        for taxid,current,white in merged:
                yield taxid,current
      
    def _deletedNodeIterator(self,file):
        file = universalOpen(file)
        deleted = ColumnFile(file, 
                           sep='|', 
                           types=(int,str))
        for taxid,white in deleted:
                yield taxid
        
#####
#
#
# Binary writer
#
#
#####

def ecoTaxonomyWriter(prefix, taxonomy):

    def ecoTaxPacker(tx):
        
        namelength = len(tx[3])
        
        totalSize = 4 + 4 + 4 + 4 + namelength
        
        packed = struct.pack('> I I I I I %ds' % namelength, 
                             totalSize, 
                             tx[0],
                             tx[1],
                             tx[2], 
                             namelength,
                             tx[3])
        
        return packed
    
    def ecoRankPacker(rank):
        
        namelength = len(rank)
        
        packed = struct.pack('> I %ds' % namelength,
                             namelength,
                             rank)
        
        return packed
    
    def ecoAliasPacker(taxid,index):
        
        totalSize = 4 + 4
        try:
            packed = struct.pack('> I I i',
                                 totalSize,
                                 taxid,
                                 index)
        except struct.error,e:
            print >>sys.stderr,(totalSize,taxid,index)
            print >>sys.stderr,"Total size : %d  taxid : %d  index : %d" %(totalSize,taxid,index)
            raise e
         
        return packed
                    
    def ecoNamePacker(name):
        
        namelength = len(name[0])
        classlength= len(name[1])
        totalSize =  namelength + classlength + 4 + 4 + 4 + 4
        
        packed = struct.pack('> I I I I I %ds %ds' % (namelength,classlength),
                             totalSize,
                             int(name[1]=='scientific name'),
                             namelength,
                             classlength,
                             name[2],
                             name[0],
                             name[1])
        
        return packed
        
    
    def ecoTaxWriter(file,taxonomy):
        output = open(file,'wb')
        output.write(struct.pack('> I',len(taxonomy)))
        
        for tx in taxonomy:
            output.write(ecoTaxPacker(tx))
    
        output.close()
        
    def ecoRankWriter(file,ranks):
        output = open(file,'wb')
        output.write(struct.pack('> I',len(ranks)))
            
        for rank in ranks:
            output.write(ecoRankPacker(rank))
    
        output.close()
    
    def ecoAliasWriter(file,index):
        output = open(file,'wb')
        output.write(struct.pack('> I',len(index)))
        
        for taxid in index:
            i=index[taxid]
            if i is None:
                i=-1
            output.write(ecoAliasPacker(taxid, i))
    
        output.close()
    
    def nameCmp(n1,n2):
        name1=n1[0].upper()
        name2=n2[0].upper()
        if name1 < name2:
            return -1
        elif name1 > name2:
            return 1
        return 0
    
    
    def ecoNameWriter(file,names):
        output = open(file,'wb')
        output.write(struct.pack('> I',len(names)))
    
        names.sort(nameCmp)
        
        for name in names:
            output.write(ecoNamePacker(name))
    
        output.close()
        
    
    ecoRankWriter('%s.rdx' % prefix, taxonomy._ranks)
    ecoTaxWriter('%s.tdx' % prefix, taxonomy._taxonomy)
    ecoNameWriter('%s.ndx' % prefix, taxonomy._name)
    ecoAliasWriter('%s.adx' % prefix, taxonomy._index)
