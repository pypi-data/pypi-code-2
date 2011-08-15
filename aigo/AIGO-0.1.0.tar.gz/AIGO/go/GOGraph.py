from pylab import *


from xml.sax import make_parser

from AIGO.go.Graph import DiGraph
from AIGO.go.GOHandler  import GOHandler

def get_GOGraph(f_stream, prefix="GO"):
    """Constructs a GO tree (GOGraph) from the provided stream.  Reads xml format only."""

    parser = make_parser()
    cH = GOHandler()
    parser.setContentHandler(cH)
    parser.parse(f_stream)
    f_stream.close()
    return GOGraph(cH.terms, cH.edges, GOName=cH.GOName, GODef=cH.GODef, GOAlt=cH.GOAlt, GONameSpace=cH.GONameSpace, GOObsolete=cH.GOObsolete, prefix=prefix)


class GOGraph(DiGraph):
    """
    Each node in GOGraph is the GO:id term (int value).  Each edge connects the term,
    the relationship can be found by calling which(edge_num)
    """
    
    def __init__(self, terms, edges, GOName=None, GODef=None, GOAlt=None, GONameSpace=None, GOObsolete=None, prefix="GO"):
        """
        Construct GOGraph with parameters:
            terms - list of ints
            edges - list tuples (int,P int, edge_type)
        Use get_GOGraph to generate the GO graph from a stream.
        """
        DiGraph.__init__(self)

        self.aspect=['biological_process', 'cellular_component', 'molecular_function']

        self.prefix=prefix
        
        self.edge_types = [0 for i in range(len(edges))]
        self.ancestors_cache = {}
        self.concepts_cache = {}
            
        for (u,v,type) in edges:
            self.add_edge(u,v,type)

        if GOAlt:
            self.GOAlt = GOAlt

        if GONameSpace:
            self.GONameSpace = GONameSpace
            self.aspect=[str(a)for a in set(GONameSpace.values())]

        if GOName:
            self.GOName=GOName

        if GODef:
            self.GODef=GODef

        if GOObsolete:
            self.GOObsolete=GOObsolete

    def deep_copy(self):
        """
        Return a deep copy of this GOGraph
        """
        edges = []
        for e in self.E:
            u,v = self.endpoints(e)
            type = self.edge_type(e)
            edges.append( (u,v,type) )
        
        return GOGraph(None, edges, self.is_a, self.part_of)
    

    def clean(self, GO):
        """
        Remove all go terms in GO that are not in the network.
        """
        removal = []
        for go in GO:
            if go not in self.N:
                removal.append(go)
        for go in removal:
            GO.remove(go)
    
    def clean_set(self, G):
        """
        Remove all go terms in G, a set of GOs, that are not in the network.
        """
        removal = []
        for GO in G:
            self.clean(GO)
            if len(GO) == 0:
                removal.append(GO)
        for GO in removal:
            G.remove(GO)
            del GO
        del removal
        

    def ancestors(self,intid):
        if self.ancestors_cache.has_key(intid):
            return self.ancestors_cache.get(intid)
        
        if intid not in self.N:
            return set()
        
        anc = set()
        anc.add(intid)
        processed = set()
        queue = self.neighbors(intid)
        
        while len(queue) > 0:
            t = queue.pop()
            anc.add(t)
            processed.add(t)
            for tp in self.neighbors_iter(t):
                if tp not in processed:
                    queue.append(tp)
        
        self.ancestors_cache[intid] = anc
        
        return anc

    def induced(self, S):
        U=set()
        for intid in S:
            U = U | self.ancestors(intid)

        return U
        
    
    def concepts(self, intid):
        """
        Retrieves a dictionary of concept -> depth for the given intid
        """

        if self.concepts_cache.has_key(intid):
            return self.concepts_cache.get(intid)
        
        if intid not in self.N:
            return set()
        
        anc = {}
        processed = set()
        #queue = self.neighbors( (intid,1) )
        queue = [(intid,1)]
        
        while len(queue) > 0:
            (t,depth) = queue.pop()
            anc[t] = depth
            processed.add(t)
            for tp in self.neighbors_iter(t):
                if tp not in processed:
                    queue.append( (tp,depth+1) )

        self.concepts_cache[intid] = anc
        
        return anc
       
#    def _key(self):
#        return self.w[0]*1000 + self.w[1]

    def add_term(self,go):
        self.N.add(go)
    
    def edge_type(self,eid):
        return self.edge_types[eid]
        
    def add_edge(self,go1,go2,type):
        """
        Add a connection from go1 to go2 of type (IS_A, PART_OF)
        """
        e = self.E.add(go1, go2)
        self.edge_types[e] = type

    def tips(self):
        from itertools import repeat

        tips=dict(zip(self.N(), repeat(True)))

        for u,v in self.edges_conn.values():
            tips[v]=False
            
        return [t for t in tips if tips[t]]
    
    def roots(self):

        roots=list()
        for aspect in self.aspect:
            for n in self.N():
                if aspect==self.GONameSpace[n]:
                    break

            c=self.concepts(n)
            idx=argsort(c.values())

            o=-1
            while not len(self.ancestors(c.keys()[idx[o]]))==1:
                o=o-1
            
            roots.append(c.keys()[idx[o]])

        return sort(roots)


    def subgraph(self,nodes=None,edges=None):
        """
        """

        return super(GOGraph,self).subgraph(nodes,edges)

#------------------------------------------------------------------
#  Semantic Distance 
#------------------------------------------------------------------

    def GS2(self, G):
        """
        Calculates GS2 measure on gene set G. G is a list (or set) of annotation sets (in int format)
        Valid G = [ [456,897], [23690,1230,23450], ... ]
        Valid GO ids are 4568, 2009, NOT GO:0003456 or 0003456
        """

        if len(G)==0:
            return 0,[0]
        
        gN = {}
        gP = {}
        G = zip(range(len(G)),G)
        for (i,g) in G:
            parents = set(g)
            for intid in g:
                gP[intid] =  self.ancestors(intid)
                parents = parents | gP[intid]
            for intid in parents:
                gN[intid] = gN.get(intid,0) + 1
            
        # calculate similarity
        l=[ self._trank(g,G,gP,gN) for (i,g) in G]
        sim = sum(l)/len(G)

        return sim, l
    
    def _trank(self, g, G, gP, gN):
        if len(g) == 0:
            return 0
        
        s = 0
        for i in g:
            if len(gP[i]) > 0:
                s += sum([ gN[j] - 1 for j in gP[i] ]) / ( len(gP[i])*(len(G)-1.0) )
        
        return s/len(g)


    def CzekanowskiDice(self, GO1, GO2):
        """
        Calculates CzekanowskiDice semantic similarity between two sets of annotations (in int format)
        """

        induced_GO1=self.induced(GO1)
        induced_GO2=self.induced(GO2)

        symD=len(induced_GO1.symmetric_difference(induced_GO2))
        U=len(induced_GO1.union(induced_GO2))
        I=len(induced_GO1.intersection(induced_GO2))
        
        return 1.- (1.0 * symD )/ (U+I)

    def Resnik(self, GO1, GO2, IC):
        """
        Calculates Resnik semantic similarity between two sets of annotations (in int format)
        The mean pairwise term similiarity is returned
        """

        D=dict()
        for go1 in GO1:
            for go2 in GO2:
                g1,g2=sort([go1,go2])                
                D.setdefault(g1,dict()).update({g2:self._minimumSubsumer(g1,g2,IC)})


        M1=mean([max([D[sort([go1,go2])[0]][sort([go1,go2])[1]] for go2 in GO2]) for go1 in GO1])
        M2=mean([max([D[sort([go1,go2])[0]][sort([go1,go2])[1]] for go1 in GO1]) for go2 in GO2])


        return (M1+M2)/2.0, [M1,M2]

    def _minimumSubsumer(self, go1,go2,IC):
        go1=self.GOAlt.get(go1,go1)
        go2=self.GOAlt.get(go2,go2)
        common=self.ancestors(go1).intersection(self.ancestors(go2))
        return max([IC[self.GONameSpace[go]][go] for go in common])
        
#------------------------------------------------------------------
#  Extra
#------------------------------------------------------------------

    def get_intid(self, goid):
        return int(goid[3:])

    def get_goid(self, intid):
        return "%s:%07d" % (self.prefix, intid)

    def GOtoInt(self, S):
        """Convert GO ids to integers"""
        return [self.get_intid(goid) for goid in S]

    def InttoGO(self, S):
        """Convert integers to GO ids"""
        return [self.get_goid(intid) for intid in S]

    def get_GOAlternative(self, go, nameSpace=True):
        intid=self.get_intid(go)
    
        intid=self.GOAlt.get(intid, intid)

        if nameSpace:
            return self.get_goid(intid), self.GONameSpace.get(intid, None)
        else:
            return self.get_goid(intid)

    def get_GOName(self, go):
        intid=self.get_intid(go)

        intid=self.GOAlt.get(intid, intid)

        return self.GOName.get(intid, "")

    def get_GONameSpace(self, go):
        intid=self.get_intid(go)

        intid=self.GOAlt.get(intid, intid)

        return self.GONameSpace.get(intid, "")

    def isObsolete(self, goid):
        return self.get_intid(goid) in self.GOObsolete

    def isUnconnected(self, goid):
    
        intid=self.get_intid(goid)
        intid=self.GOAlt.get(intid, intid)

        return intid in self.GOObsolete

    def get_NodesfromAspect(self, aspect):
        return self.InttoGO([n for n in self.N() if self.GONameSpace[n]==aspect])

    def get_Redundant(self, S):
        """
        Get the redundant annotations in a set
        """

        redundant=set()
        S=self.GOtoInt(S)
        for intid in S:
            s = set(S)
            s.remove(intid)
            redundant = redundant | self.ancestors(intid).intersection(s)
            
        return self.InttoGO(redundant)

    def get_Parents(self, goid):
        intid=self.get_intid(goid)

        d=self.concepts(intid)
        parents=[n for n in d if d[n]==2]
        return self.InttoGO(parents)
        

    def get_Ancestors(self, goid):
        intid=self.get_intid(goid)
        return self.InttoGO(self.ancestors(intid))

    def get_Tips(self):
        return self.InttoGO(self.tips())

    def get_Roots(self):
        return self.InttoGO(self.roots())

    def plot_InducedGraph(self, S, allRoot=False, figName="induced.png", ttl=""):
        import pygraphviz as pgv
        import textwrap

        ec=['blue', 'lightblue']

        A=pgv.AGraph(directed=True)
        A.graph_attr['label']=ttl
        A.graph_attr['splines']="true"
        A.graph_attr['ordering']="out"
        A.node_attr['shape']="box"

        if allRoot:
            #Make sure that the placement is constant (doesn't work !!!)

            A.add_node('root')
            n=A.get_node('root')
            n.attr['style']='invis'

            roots=sort(self.get_Roots())
            for r in roots:
                A.add_edge('root', r, style='invis')

            for r in roots:
                n=A.get_node(r)
                s=str('\\n'.join(textwrap.wrap(self.get_GOName(r), 25)))
                n.attr['label']='%s\\n%s' % (r, s)

            sub=A.add_subgraph(roots,"roots", ordering="out", rank="min")


        if not len(S)==0:
            #Get the subgraph induced by S
            U=set()
            for intid in self.GOtoInt(S):
                U = U | self.ancestors(intid)
            g=self.subgraph(U)

            #Creating all the edges
            T=g.topology()
            idx=argsort([e[0] for e in T])

            for i in idx:
                sp,ep=T[i]
                t=self.edge_type(self.E.get(sp,ep))
                A.add_edge(self.get_goid(ep),self.get_goid(sp),color=ec[t], dir='back')

            #Coloring the nodes from S
            for goid in S:
                n=A.get_node(goid)
                n.attr['style']='filled'
                n.attr['fillcolor']='lightgrey'

            #Setting up the nodes labels
            for intid in U:
                goid=self.get_goid(intid)
                n=A.get_node(goid)
                s=str('\\n'.join(textwrap.wrap(self.GOName[intid], 25)))
                n.attr['label']='%s\\n%s' % (goid, s)

        A.layout(prog="dot")

        A.draw(figName)

    def compare_InducedGraph(self, S1,S2,allRoot=False, figName="induced.png", ttl=""):
        import pygraphviz as pgv
        import textwrap

        ec=['blue', 'lightblue']

        A=pgv.AGraph(directed=True)
        A.graph_attr['label']=ttl
        A.graph_attr['splines']="true"
        A.graph_attr['ordering']="out"
        A.node_attr['shape']="box"

        if allRoot:
            #Make sure that the placement is constant (doesn't work !!!)

            A.add_node('root')
            n=A.get_node('root')
            n.attr['style']='invis'

            roots=sort(self.get_Roots())
            for r in roots:
                A.add_edge('root', r, style='invis')

            for r in roots:
                n=A.get_node(r)
                s=str('\\n'.join(textwrap.wrap(self.get_GOName(r), 25)))
                n.attr['label']='%s\\n%s' % (r, s)

            sub=A.add_subgraph(roots,"roots", ordering="out", rank="min")


        S=set(S1).union(S2)
        I=set(S1).intersection(S2)
        if not len(S)==0:
            #Get the subgraph induced by S1 and S2
            U=set()
            for intid in self.GOtoInt(S):
                U = U | self.ancestors(intid)
            g=self.subgraph(U)

            #Creating all the edges
            T=g.topology()
            idx=argsort([e[0] for e in T])

            for i in idx:
                sp,ep=T[i]
                t=self.edge_type(self.E.get(sp,ep))
                A.add_edge(self.get_goid(ep),self.get_goid(sp),color=ec[t], dir='back')


            #Coloring the nodes from S1
            for goid in S1:
                n=A.get_node(goid)
                n.attr['style']='filled'
                n.attr['fillcolor']='chartreuse1'

            #Coloring the nodes from S2
            for goid in S2:
                n=A.get_node(goid)
                n.attr['style']='filled'
                n.attr['fillcolor']='firebrick1'

            #Coloring the nodes from the intersection of S1 and S2
            for goid in I:
                n=A.get_node(goid)
                n.attr['style']='filled'
                n.attr['fillcolor']='lightgrey'

            #Setting up the nodes labels
            for intid in U:
                goid=self.get_goid(intid)
                n=A.get_node(goid)
                s=str('\\n'.join(textwrap.wrap(self.GOName[intid], 25)))
                n.attr['label']='%s\\n%s' % (goid, s)

        A.layout(prog="dot")

        A.draw(figName)



    def plot_FrequencyGraph(self, aspect, freq, figName="induced.png", ttl="", graphviz=None):
        import pygraphviz as pgv
        
        cmap=cm.hot_r

        if graphviz is None:

            A=pgv.AGraph(directed=True)
                
            A.graph_attr['splines']="false"
            A.graph_attr['ordering']="out"
            A.graph_attr['ranksep']="1.0"
            A.graph_attr['overlap']="true"
            A.graph_attr['outputorder']="edgesfirst"
        
            A.node_attr['shape']="point"        
            A.node_attr['fixedsize']="true"
            A.node_attr['label']=""
            A.node_attr['width']="0.3"
            A.node_attr['height']="0.3"
            
            c=cmap(0)
            A.node_attr['style']='filled'
            A.node_attr['fillcolor']= "#%02x %02x %02x %02x"  % (255*c[0], 255*c[1], 255*c[2], 255*0.2)
            A.node_attr['color']="#88 88 88 33"

            S=set(self.get_Tips()).intersection(self.get_NodesfromAspect(aspect))

            #Get the subgraph induced by S
            U=set()
            for intid in self.GOtoInt(S):
                U = U | self.ancestors(intid)
            g=self.subgraph(U)

            #Creating all the edges
            T=g.topology()
            idx=argsort([e[0] for e in T])

            for i in idx:
                sp,ep=T[i]
                t=self.edge_type(self.E.get(sp,ep))
                A.add_edge(self.get_goid(ep),self.get_goid(sp),color="transparent", dir='none')

            r=self.get_goid(U.intersection(self.roots()).pop())
            A.graph_attr['root']=r

            A.layout(prog="twopi")
        else:
            A=graphviz

        #Coloring the nodes from S
        for n in A.nodes():
            n.attr['style']='filled'
            c=cmap(freq[n])
            n.attr['fillcolor']= "#%02x %02x %02x %02x"  % (255*c[0], 255*c[1], 255*c[2], 255*0.8)
            n.attr['color']="#88 88 88 33"

        A.graph_attr['label']=ttl
        A.draw(figName)

        return A
