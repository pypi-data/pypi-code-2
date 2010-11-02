'''
obitools main module.

@author: Eric Coissac
@contact: eric@coissac.eu
@license: CeCILL 2.0


obitools module provides base class for sequence manipulation.

All biological sequences must be subclass of L{obitools.BioSequence}.
Some biological sequences are defined as transformation of other
biological sequences. For example Reversed complemented sequences
are a transformation of a L{obitools.NucSequence}. This particular
type of sequences are subclasses of the L{obitools.WrappedBioSequence}.


G{packagetree obitools}

'''

from weakref import ref

from obitools.utils.iterator import uniqueChain
from itertools import chain

try:
    from functools import partial
except:
    #
    # Add for compatibility purpose with Python < 2.5
    #
    def partial(func, *args, **keywords):
        def newfunc(*fargs, **fkeywords):
            newkeywords = keywords.copy()
            newkeywords.update(fkeywords)
            return func(*(args + fargs), **newkeywords)
        newfunc.func = func
        newfunc.args = args
        newfunc.keywords = keywords
        return newfunc


from obitools.sequenceencoder import DNAComplementEncoder
from obitools.location import Location

class WrapperSetIterator(object):
    def __init__(self,s):
        self._i = set.__iter__(s)
    def next(self):
        return self._i.next()()
    def __iter__(self):
        return self
    
class WrapperSet(set):
    def __iter__(self):
        return WrapperSetIterator(self)
 

class BioSequence(object):
    '''
    BioSequence class is the base class for biological
    sequence representation.
    
    It provides storage of :
    
        - the sequence itself, 
        - an identifier,
        - a definition an manage 
        - a set of complementary information on a key / value principle.
    
    BioSequence is an abstract class and must be instanciated
    from its subclasses
    '''
    
    def __init__(self,id,seq,definition=None,evaluated=True,**info):
        '''
        BioSequence constructor.
        
        C{obitools.BioSequence} is an abstract class, this constructor
        can only be called by a subclass constructor.
        
        @param id: sequence identifier
        @type id:  str
 
        @param seq: the sequence
        @type seq:  str

        @param definition: sequence definition (optional)
        @type definition: str

        @param info: extra named parameters can be added to associate complementary
        data to the sequence
        
        '''
        
        assert type(self)!=BioSequence,"obitools.BioSequence is an abstract class"
        
        self._seq=str(seq).lower()
        self._info = dict(info)
        self._eval = {}
        for k in self._info:
            self._eval[k]=evaluated
        self.definition=definition
        self.id=id
        self._hasTaxid=None
        
    def clone(self):
        seq = type(self)(self.id,
                         str(self),
                         definition=self.definition
                         )
        seq._info=dict(self.getTags())
        seq._eval=dict(self._eval)
        seq._hasTaxid=self._hasTaxid
        return seq
        
    def getDefinition(self):
        '''
        Sequence definition getter.
        
            @return: the sequence definition
            @rtype: str
            
        '''
        return self._definition

    def setDefinition(self, value):
        '''
        Sequence definition setter.
        
            @param value: the new sequence definition
            @type value: C{str}
            @return: C{None}
        '''
        self._definition = value

    def getId(self):
        '''
        Sequence identifier getter
        
            @return: the sequence identifier
            @rtype: C{str}
        '''
        return self._id

    def setId(self, value):
        '''
        Sequence identifier setter.
        
        @param value: the new sequence identifier
        @type value:  C{str}
        @return: C{None}
        '''
        self._id = value

    def getStr(self):
        '''
        Return the sequence as a string
        
            @return: the string representation of the sequence
            @rtype: str
        '''
        return self._seq
    
    def getSymbolAt(self,position):
        '''
        Return the symbole at C{position} in the sequence
        
        @param position: the desired position. Position start from 0
                         if position is < 0 then they are considered
                         to reference the end of the sequence.
        @type position: C{int}
        
        @return: a one letter string
        @rtype: C{str}
        '''
        return str(self)[position]
    
    def getSubSeq(self,location):
        '''
        return a subsequence as described by C{location}.
        
        The C{location} parametter can be a L{obitools.location.Location} instance,
        an interger or a python C{slice} instance. If C{location}
        is an iterger this method is equivalent to L{getSymbolAt}.
        
        @param location: the positions of the subsequence to return
        @type location: C{Location} or C{int} or C{slice}
        @return: the subsequence
        @rtype: a single character as a C{str} is C{location} is an integer,
                a L{obitools.SubSequence} instance otherwise.
        '''
        if isinstance(location,Location):
            return location.extractSequence(self)
        elif isinstance(location, int):
            return self.getSymbolAt(location)
        elif isinstance(location, slice):
            return SubSequence(self,location)

        raise TypeError,'key must be a Location, an integer or a slice'  
    
    def getKey(self,key):
        if not self._eval[key]:
            self._eval[key]=True
            try:
                self._info[key]=eval(self._info[key])
            except:
                pass
        return self._info[key]
            
    def extractTaxon(self):
        '''
        Extract Taxonomy information from the sequence header.
        This method by default return None. It should be subclassed
        if necessary as in L{obitools.seqdb.AnnotatedSequence}.
        
            @return: None
        '''
        self._hasTaxid=self.hasKey('taxid')
        return None
        
    def __str__(self):
        return self.getStr()
    
    def __getitem__(self,key):
        if isinstance(key, str):
            if key=='taxid' and self._hasTaxid is None:
                self.extractTaxon()
            return self.getKey(key)
        else:
            return self.getSubSeq(key)
        
    def __setitem__(self,key,value):
        self._info[key]=value
        self._eval[key]=True
        if key=='taxid':
            self._hasTaxid=value is not None
        
    def __delitem__(self,key):
        if isinstance(key, str):
            del self._info[key]
            del self._eval[key]
            if key=='taxid':
                self._hasTaxid=None
        else:
            raise TypeError,key
        
    def __iter__(self):
        '''
        Iterate through the sequence symbols
        '''
        return iter(str(self))
    
    def __len__(self):
        return len(str(self))
    
    def hasKey(self,key):
        return key in self._info
    
    def __contains__(self,key):
        '''
        methods allowing to use the C{in} operator on a C{BioSequence}.
        
        The C{in} operator test if the C{key} value is defined for this
        sequence.
         
        @param key: the name of the checked value
        @type key: str
        @return: C{True} if the value is defined, {False} otherwise.
        @rtype: C{bool}
        '''
        if key=='taxid' and self._hasTaxid is None:
            self.extractTaxon()
        return self.hasKey(key)
    
    def rawiteritems(self):
        return self._info.iteritems()

    def iteritems(self):
        '''
        iterate other items dictionary storing the values
        associated to the sequence. It works similarly to
        the iteritems function of C{dict}.
        
            @return: an iterator over the items (key,value)
                     link to a sequence
            @rtype: iterator over tuple
            @see: L{items}
        '''
        for k in self._info:
            try:
                self._eval[k]=True
                self._info[k]=eval(self._info[k])
            except:
                pass
        return self._info.iteritems()
    
    def items(self):
        return [x for x in self.iteritems()]
    
    def iterkeys(self):
        return self._info.iterkeys()
    
    def keys(self):
        return [x for x in self.iterkeys()]
    
    def getTags(self):
        return self._info
    
    def getRoot(self):
        return self
    
    def getWrappers(self):
        if not hasattr(self, '_wrappers'):
            self._wrappers=WrapperSet()
        return self._wrappers
    
    def register(self,wrapper):
        self.wrappers.add(ref(wrapper,self._unregister))
        
    def _unregister(self,ref):
        self.wrappers.remove(ref)
        
    wrappers = property(getWrappers,None,None,'')

    definition = property(getDefinition, setDefinition, None, "Sequence Definition")

    id = property(getId, setId, None, 'Sequence identifier')
    
    def _getTaxid(self):
        return self['taxid']
    
    def _setTaxid(self,taxid):
        self['taxid']=taxid
        
    taxid = property(_getTaxid,_setTaxid,None,'NCBI Taxonomy identifier')
        
class NucSequence(BioSequence):
 
    def complement(self):
        return DNAComplementSequence(self)
    
    def isNucleotide(self):
        return True
    

class AASequence(BioSequence):

    def isNucleotide(self):
        return False
    
   
class WrappedBioSequence(BioSequence):

    def __init__(self,reference,id=None,definition=None,evaluated=True,**info):
        self._wrapped = reference
        reference.register(self)
        self._id=id
        self.definition=definition
        self._info=info
        self._eval = {}
        for k in self._info:
            self._eval[k]=evaluated
            
    def clone(self):
        seq = type(self)(self.wrapped,
                         id=self._id,
                         definition=self._definition
                         )
        seq._info=dict(self._info)
        seq._eval=dict(self._eval)
        return seq
        
    def getWrapped(self):
        return self._wrapped
        
    def getDefinition(self):
        d = self._definition or self.wrapped.definition
        return d
    
    def getId(self):
        d = self._id or self.wrapped.id
        return d
    
    def isNucleotide(self):
        return self.wrapped.isNucleotide()
    

    def iterkeys(self):
        return uniqueChain(self._info.iterkeys(),
                               self.wrapped.iterkeys())
        
    def rawiteritems(self):
        return chain(self._info.iteritems(),
                        (x for x in self.wrapped.rawiteritems()
                         if x[0] not in self._info))

    def iteritems(self):
        for x in self.iterkeys():
            yield (x,self[x])
            
    def getKey(self,key):
        if key in self._info:
            if not self._eval[key]:
                try:
                    self._eval[key]=True
                    self._info[key]=eval(self._info[key])
                except:
                    pass
            return self._info[key]
        else:
            return self.wrapped.getKey(key)
        
    def hasKey(self,key):
        return key in self._info or self.wrapped.hasKey(key)
            
    def getSymbolAt(self,position):
        return self.wrapped.getSymbolAt(self.posInWrapped(position))
    
    def posInWrapped(self,position,reference=None):
        if reference is None or reference is self.wrapped:
            return self._posInWrapped(position)
        else:
            return self.wrapped.posInWrapped(self._posInWrapped(position),reference)
            
    
    def getStr(self):
        return str(self.wrapped)
    
    def getRoot(self):
        return self.wrapped.getRoot()
    
    def _posInWrapped(self,position):
        return position
    
    
    definition = property(getDefinition,BioSequence.setDefinition, None, "Sequence Definition")
    id = property(getId,BioSequence.setId, None, "Sequence Identifier")

    wrapped = property(getWrapped, None, None, "Wrapped's Docstring")
         
    
class SubSequence(WrappedBioSequence):
    
    @staticmethod
    def _sign(x):
        if x == 0:
            return 0
        elif x < 0:
            return -1
        return 1
    
    def __init__(self,reference,
                 location=None,
                 start=None,stop=None,
                 id=None,definition=None,
                 evaluated=True,**info):
        WrappedBioSequence.__init__(self,reference,id=None,definition=None,evaluated=evaluated,**info)
        
        if isinstance(location, slice):
            self._location = location
        else:
            step = 1
            if not isinstance(start, int):
                start = 0;
            if not isinstance(stop,int):
                stop = len(reference)
            self._location=slice(start,stop,step)

        self._indices=self._location.indices(len(self.wrapped))
        self._xrange=xrange(*self._indices)
 
        self._info['cut']='[%d,%d,%s]' % self._indices
        self._eval['cut']=True
        
        if hasattr(reference,'quality'):
            self.quality = reference.quality[self._location]
        
    def getId(self):
        d = self._id or ("%s_SUB" % self.wrapped.id)
        return d

        
    def clone(self):
        seq = WrappedBioSequence.clone(self)
        seq._location=self._location
        seq._indices=seq._location.indices(len(seq.wrapped))
        seq._xrange=xrange(*seq._indices)
        return seq
        
           
    def __len__(self):
        return len(self._xrange)
    
    def getStr(self):
        return ''.join([x for x in self])
    
    def __iter__(self):
        return (self.wrapped.getSymbolAt(x) for x in self._xrange)
    
    def _posInWrapped(self,position):
        return self._xrange[position]
    
    def complement(self):
        if self.wrapped.isNucleotide():
            return DNAComplementSequence(self)
        raise AttributeError
    
    id = property(getId,BioSequence.setId, None, "Sequence Identifier")

                
 
class DNAComplementSequence(WrappedBioSequence):

    _comp={'a': 't', 'c': 'g', 'g': 'c', 't': 'a',
           'r': 'y', 'y': 'r', 'k': 'm', 'm': 'k', 
           's': 's', 'w': 'w', 'b': 'v', 'd': 'h', 
           'h': 'd', 'v': 'b', 'n': 'n', 'u': 'a',
           '-': '-'}

    
    def __init__(self,reference,
                 id=None,definition=None,evaluated=True,**info):
        WrappedBioSequence.__init__(self,reference,id=None,definition=None,evaluated=evaluated,**info)
        assert reference.isNucleotide()
        self._info['complemented']=True
        self._eval['complemented']=True
        if hasattr(reference,'quality'):
            self.quality = reference.quality[::-1]

           
    def getId(self):
        d = self._id or ("%s_CMP" % self.wrapped.id)
        return d
    
    def __len__(self):
        return len(self._wrapped)
    
    def getStr(self):
        return ''.join([x for x in self])
    
    def __iter__(self):
        return (self.getSymbolAt(x) for x in xrange(len(self)))
    
    def _posInWrapped(self,position):
        return -(position+1)

    def getSymbolAt(self,position):
        return DNAComplementSequence._comp[self.wrapped.getSymbolAt(self.posInWrapped(position))]
    
    def complement(self):
        return self.wrapped
    
    id = property(getId,BioSequence.setId, None, "Sequence Identifier")
                
   
def _isNucSeq(text):
    acgt   = 0
    notnuc = 0
    ltot   = len(text) * 0.8
    for c in text.lower():
        if c in 'acgt-':
            acgt+=1
        if c not in DNAComplementEncoder._comp:
            notnuc+=1
    return notnuc==0 and float(acgt) > ltot


def bioSeqGenerator(id,seq,definition=None,evaluated=True,**info):
    if _isNucSeq(seq):
        return NucSequence(id,seq,definition,evaluated,**info)
    else:
        return AASequence(id,seq,definition,evaluated,**info)
    
