from xml.sax.handler import ContentHandler

IS_A = 0
PART_OF = 1

def get_intid(goid):
    return int(goid[3:])


class GOHandler(ContentHandler):
    def __init__(self,):
        # create flags
        self.isId, self.isType,self.isIsA, self.isPartOf, self.isAldId, self.isConsider, self.isName, self.isNameSpace , self.isDefStr, self.isObsolete= 0,0,0,0,0,0,0,0,0,0
        self.inTerm = 0
        self.inDef = 0
        self.inRelationship = 0
        self.edges = []
        self.terms = []
        self.GOAlt = dict()
        self.GONameSpace = dict()
        self.GOName = dict()
        self.GODef= dict()
        self.GOObsolete = set()
        self.id = ''
        
    def startElement(self, name, attrs):
        if name == 'term':
            self.inTerm = 1
        if name == 'def':
            self.inDef = 1
        
        if self.inTerm == 1:
            if self.inRelationship == 1:
                if name == 'type':        
                    self.isType = 1
                    self.type = ''
                elif name == 'to' and self.type=='part_of':
                    self.isPartOf = 1
                    self.partof = ''
            else:
                if name == 'relationship':
                    self.inRelationship = 1
                elif name == 'id':        
                    self.isId = 1
                    self.id = ''
                elif name == 'is_a':
                    self.isIsA = 1
                    self.isa = ''
                elif name == 'part_of':
                    self.isPartOf = 1
                    self.partof = ''
                elif name == 'is_obsolete':
                    self.isObsolete = 1
                    self.obsolete = ''
                elif name == 'alt_id':
                    self.isAldId = 1
                    self.altId = ''
                elif name == 'consider' or name == 'replaced_by':
                    self.isConsider = 1
                    self.consider = ''
                elif name == 'name' and not self.inDef:
                    self.isName = 1
                    self.name = ''
                elif name == 'namespace':
                    self.isNameSpace = 1
                    self.nameSpace = ''
                elif name == 'defstr':
                    self.isDefStr = 1
                    self.defStr = ''

    
    def endElement(self, name):
        if name == 'def':
            self.inDef = 0
            
        if self.inTerm == 1:
            if self.inRelationship == 1:
                if name == 'relationship':
                    self.inRelationship = 0
                elif name == 'type':
                    self.isType=0
                elif name == 'to' and self.type=='part_of':
                    self.isPartOf = 0
                    self.edges.append( (self.id, get_intid(self.partof), PART_OF ) )
            else:
                if name == 'term':
                    self.terms.append(self.id)
                    self.inTerm = 0
                elif name == 'id':
                    self.isId = 0
                    self.id = get_intid(self.id)
                    self.GODef[self.id]=''
                elif name == 'is_a':
                    self.isIsA = 0
                    self.edges.append( (self.id, get_intid(self.isa), IS_A ) )
                elif name == 'part_of':
                    self.isPartOf = 0
                    self.edges.append( (self.id, get_intid(self.partof), PART_OF ) )
                elif name == 'is_obsolete':
                    self.isObsolete = 0
                    self.GOObsolete.add(self.id)
                elif name == 'alt_id':
                    self.isAldId = 0
                    self.GOAlt[get_intid(self.altId)]=self.id
                elif name == 'consider' or name == 'replaced_by':
                    self.isConsider = 0
                    self.GOAlt[self.id]=get_intid(self.consider)
                elif name == 'name':
                    self.isName = 0 
                    self.GOName[self.id]=self.name
                elif name == 'namespace':
                    self.isNameSpace = 0
                    self.GONameSpace[self.id]=self.nameSpace
                elif name == 'defstr':
                    self.isDefStr = 0
                    self.GODef[self.id]=self.defStr
    
    def characters(self, ch):
        if self.isId == 1:
            self.id += ch
        elif self.isType == 1:
            self.type += ch
        elif self.isIsA == 1:
            self.isa += ch
        elif self.isPartOf == 1:
            self.partof += ch
        elif self.isObsolete == 1:
            self.obsolete += ch            
        elif self.isAldId == 1:
            self.altId += ch
        elif self.isConsider == 1:
            self.consider += ch
        elif self.isName == 1:
            self.name += ch
        elif self.isNameSpace == 1:
            self.nameSpace += ch
        elif self.isDefStr == 1:
            self.defStr += ch
            

