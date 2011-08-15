"""
This module provides the classes used to model graphs:
- Graph, an undirected graph
- DiGraph, a directed graph.

In PyWeaver, all graph arguments are assumed to be either undirected graph-like or
directed graph-like, implementing all methods supported by the Graph and DiGraph classes.

The Graph is the base-class for all graphs.  The DiGraph class extends Graph, redefining
methods where necessary in order to accomodate directed edges.
"""

"""
Copyright 2007 Derek Ruths

This file is part of PyWeaver.

PyWeaver is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyWeaver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PyWeaver.  If not, see <http://www.gnu.org/licenses/>.
"""

import Constants
import types

__all__ = [ 'Graph','DiGraph','Node','Edge','NodeManager','EdgeManager',
			'DirectedNodeManager','DirectedEdgeManager']
	
#####
# Classes that can be used with graphs.
#####
class Node(object):
	"""
	This is a utility class that can be used rather than having to define one's own node
	class.  The Node (or other user-defined) class is useful particularly when there
	is a need to define other fields - which system-defined types cannot manage.
	
	The Node constructor accepts arbitrary keyword-value arguments that will initialize
	the Node created to have a set of attributes.
	
	This class has all the behaviors of an object except in the way it renders itself as a
	string.  If the self.label field is defined, then the value of this field is returned
	as the string representation of this node.  Otherwise, the object string is returned.
	"""
		
	def __init__(self,label=None,**args):
		"""
		This constructor initializes the node with an arbitrary number of attributes.  The first
		value specified is always the label for the Node.  The label is set unless the value provided
		is None.  All parameters that follow the label must have keywords specified.  Each keyword-value
		pair is made an attribute (name is the keyword, attribute value is the value).
		"""
		if label is not None:
			self.label = label
	
		# set any keyword valued parameters
		for k,v in args.items():
			self.__dict__[k] = v
	

	def __str__(self):
		if hasattr(self,'label'):
			return self.label
		else:
			return object.__str__(self)
	
class Edge(object):
	"""
	This is a utility class that can be used rather than having to define one's own edge
	class.  The Edge (or other user-defined) class is useful particularly when there
	is a need to define other fields - which system-defined types cannot manage.
	
	This class has exactly the behaviors of an object.
	"""
	def __init__(self,**args):
		"""
		This constructor initializes the edge with an arbitrary number of attributes.
		All parameters must have keywords specified.  Each keyword-value pair is made 
		an attribute (name is the keyword, attribute value is the value).
		"""
		# set any keyword valued parameters
		for k,v in args.items():
			self.__dict__[k] = v

####################################################################################
#
# Undirected Graph-Specific Code
#

class NodeManager(object):
	"""
	This class provides the V/N field in the graph.  It behaves like a set of nodes but
	also provides some additional utilities: selection and node indexing.
	"""
	def __init__(self,graph):
		self.graph = graph
		
		self.primary_index = None
		self.index_lookups = {}
		
	#####
	# container methods
	def __call__(self):
		"""
	    Returns a list of nodes in the graph.  This list is separate from any node lists
	    used internally in the graph.  Thus this list can be modified without
	    affecting the graph from which it came.
	    """
		return list(self.graph.node_edges.keys())
		
	def __iter__(self):
		"""
		Return an iterator over the nodes in the graph
		"""
		for n in self.graph.node_edges.keys():
			yield n
			
	def __contains__(self,n):
		"""
		Return True if the node n is in this graph.
		"""
		return (n in self.graph.node_edges)
		
	def __len__(self):
		"""
		Returns the number of nodes in the graph.
		"""
		return len(self.graph.node_edges)
			
	#####
	# Node addition/removal
	def add(self,n):
		"""
		Add a node to the graph.  The node must be unique otherwise a Exception will be
		raised.
		"""
		if n not in self.graph.node_edges:
			self.graph.node_edges[n] = []
			self.graph._notify_change_listeners_node_added(n)
		else:
			raise Exception, 'Node ' + str(n) + ' is already in the graph'
		
		# update index lookups
		for iname,lookup in self.index_lookups.items():
			if hasattr(n,iname):
				v = getattr(n,iname)
				if v not in lookup:
					lookup[v] = [n]
				else:
					lookup[v].append(n)
		
		# notify graph parents
		if self.graph.graph_parent is not None:
			self.graph.graph_parent.N.add(n)
		
	def update(self,nodes):
		"""
		Add multiple nodes to the graph.
		"""
		for n in nodes:
			self.add(n)
			
	def remove(self,n):
		"""
		Remove a node from the graph.  All dependent edges are also removed from
		the graph.
		"""
		if n not in self.graph.node_edges:
			raise Exception, "Node is not in the graph"

		# Remove all edges that depend on this node
		while len(self.graph.node_edges[n]) > 0:
			self.graph.E.remove(self.graph.node_edges[n][0])
		
		del self.graph.node_edges[n]
		self.graph._notify_change_listeners_node_removed(n)

		# update index lookups
		for iname,lookup in self.index_lookups.items():
			if hasattr(n,iname):
				v = getattr(n,iname)
				if v not in lookup:
					raise Exception, 'Inconsistency in index lookup %s for node %s' % (iname,str(n))
				else:
					L = lookup[v]
					L.remove(n)
					
					if len(L) == 0:
						del lookup[v]

		# if this graph is a subgraph, notify the parent
		if self.graph.graph_parent is not None:
			self.graph.graph_parent.N.remove(n)
			
		# this graph has subgraphs, remove the node in them as well
		for sg in self.graph.subgraph_list:
			if n in sg.nodes():
				sg.N.remove(n)
	
	def discard(self,n):
		"""
		Remove the node n from the graph if it exists.  Otherwise do nothing.
		"""
		if n in self.graph.node_edges:
			self.remove(n)
	
	def difference_update(self,nodes):
		"""
		Remove multiple nodes from the graph.  All dependent edges are also removed
		from the graph.
		"""
		for n in nodes:
			self.discard(n)
			
	#####
	# Indexing methods
	def index(self,*args):
		"""
		Index the node set using the field names specified.  The first index name
		specified is the primary index.
		"""
		# empty the index lookups
		self.index_lookups = {}
		self.primary_index = None
		
		if len(args) == 0:
			return
		
		# build each lookup
		self.primary_index = args[0]
		for iname in args:
			lookup = {}
			for n in self.graph.node_edges.keys():
				if hasattr(n,iname):
					v = getattr(n,iname)
					
					if v not in lookup:
						lookup[v] = [n]
					else:
						if n not in lookup[v]:
							lookup[v].append(n)
				
			self.index_lookups[iname] = lookup
			
		# done!
		return
		
	def reindex(self,n,index=Constants.ALL):
		"""
		Reindex the nodes specified for the indicies specified.  n can either be one node, a
		container of nodes, or the ALL constant.  By default, the nodes are reindex for all
		indices (ALL).  However if a string or a container of strings is specified, then the
		nodes are reindexed only for those indices specified.  This method needs to be called
		to notify the set when the value of an indexed field changes in a node.
		"""
		
		# get the list of indexes to process
		index_list = None
		
		if index == Constants.ALL:
			index_list = self.index_lookups.keys()
		elif type(index) == types.StringType :
			index_list = [index]
		elif type(index) == types.ListType:
			index_list = index
			
		# get the node list
		node_list = None
		
		if n == Constants.ALL:
			node_list = self.node_edges.keys()
		elif type(n) == types.StringType :
			node_list = [n]
		elif type(n) == types.ListType:
			node_list = n
			
		# add this node information to the index lookups
		for index in index_list:
			if index not in self.index_lookups:
				raise Exception, 'Unrecognized index: %s' % str(index)
			
			lookup = self.index_lookups[index]
			for n in node_list:
				if hasattr(n,index):
					v = getattr(n,index)
					
					if v not in lookup:
						lookup[v] = [n]
					else:
						lookup[v].append(n)
		
	def __clean_index_list__(self,el,iname,ival):
		"""
		Check for stale (wrong) entries in the index list that need to be cleaned out.
		For convenience, this method returns a reference to the same list (el) that was
		passed in.  At the end of this method, el will no longer contain any entries that
		do not have an attribute iname with value ival.
		"""
		i = 0
		while i < len(el):
			y = el[i]
			if not hasattr(y,iname) or y.__dict__[iname] != ival:
				el.pop(i)
			else:
				i += 1
				
		return el
				
	def __getitem__(self,x):
		"""
		Return the node with the primary index specified.  If no node exists with the specified
		value for the primary index, then None is returned.
		
		If a slice colon is used, G.N[x:], then a list of nodes with the primary index 
		specified is returned.
		"""
		if self.primary_index is None:
			raise Exception, 'No primary index has been specified'

		el = None
		ival = None
		lookup = self.index_lookups[self.primary_index]
		
		if type(x) == types.SliceType:
			ival = x.start
						
			if ival in lookup:
				el = lookup[x]
			else:
				el = []
		else:
			ival = x
			if ival in lookup:
				el = lookup[x]
			else:
				return None
			
		self.__clean_index_list__(el,self.primary_index,ival)

		# return the appropriate value...
		if type(x) == types.SliceType:
				return list(el)
		else:
			if len(el) > 0:
				return el[0]
			else:
				return None
		
	def find(self,**args):
		"""
		Return the first node found with the index values specified.
		"""
		L = self.find_all(**args)
		
		if len(L) == 0:
			return None
		else:
			return L[0]
			
	def find_all(self,**args):
		"""
		Return a list of nodes that have all the index values specified.
		"""
		# TODO: add a shortcut for probably the most likely case - there's only one k=v pair.
		# TODO: add support for values that aren't hashable... this will be a very slow procedure...
		
		# put the args in a more friendly iterable form
		args = [(k,v) for k,v in args.items()]
		
		# get an initial set of nodes to whittle down...
		candidates = None
		k,v = args[0]
		
		lookup = self.index_lookups[k]
		if v in lookup:
			candidates = list(self.__clean_index_list__(lookup[v],k,v))
		else:
			return []
			
		# now prune the list down
		for k,v in args[1:]:
			lookup = self.index_lookups[k]
			if v in lookup:
				sl = set(self.__clean_index_list__(lookup[v],k,v))
				candidates = [x for x in candidates if x in sl]
			else:
				return []
				
			if len(candidates) == 0:
				return []
				
		# if we got here, then return the remaining nodes
		return candidates
		
	def find_iter(self,**args):
		"""
		Return an iterator over all the nodes that have all the index values specified.
		"""
		for n in self.find_all(**args):
			yield n
			
	#####
	# Selection methods
	def select(self,x):
		"""
		Return a list of nodes for which x(n) evaluates True.
		"""
		return [n for n in self.graph.node_edges.keys() if x(n)]

	def select_iter(self,x):
		"""
		Return an iterator over the nodes for which x(n) evaluates to True.
		"""
		for n in self.graph.node_edges.keys():
			if x(n):
				yield n

class EdgeManager(object):
	"""
	This class provides the E field in the graph.  It behaves like a set of edges but
	also provides some additional utilities: selection and edge indexing.
	"""
	def __init__(self,graph):
		self.graph = graph
		
		self.primary_index = None
		self.index_lookups = {}
		
	#####
	# container methods
	def __call__(self,u=None,v=None):
		"""
		Return a list of the edges in this graph.  The list is independent of the internal
		collection that is maintained by the Graph object.  Thus, this list may be modified
		without affecting the graph from which it came.
		
		If u or v is specified, then the list of edges adjacent to u or v are returned.
		
		If u and v are specified then the list of edges connecting u and v are returned.
		"""
		elist = None
		if v is None:
			if u is None:
				elist = list(self.graph.edges_conn.keys())
			else:
				if u not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(u)
				
				lst = self.graph.node_edges[u]
				if lst is None:
					lst = []
					
				elist = list(lst)
		else:
			if u is None:
				lst = self.graph.node_edges[v]
				if lst is None:
					lst = []
					
				elist = list(lst)
			else:
				if u not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(u)
				
				if v not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(v)
				
				elist = []
		
				if self.graph.node_edges[u] is not None:
					for e in self.graph.node_edges[u]:
						x,y = self.graph.edges_conn[e]
				
						if (x == v and y == u) or (y == v and x == u):
							elist.append(e)
			

		return elist
			
	def __iter__(self):
		"""
		Return an iterator over the edges in the graph
		"""
		for e in self.graph.edges_conn.keys():
			yield e
			
	def __contains__(self,e):
		"""
		Returns True if e is an edge decorator in this graph.
		"""
		return e in self.graph.edges_conn
		
	def __len__(self):
		"""
		Return the number of edges in the graph.
		"""
		return len(self.graph.edges_conn)
	
	def iter(self,u=None,v=None):
		"""
		Return an iterator over a subset of edges.
		
		If u or v is specified, then all edges adjacent to u or v are included.
		
		If u and v are specified then all the edges connecting u and v are included.
		"""
		for e in self(u,v):
			yield e
				
	#####
	# Node addition/removal
	def add(self,u,v,e=None):
		"""
		Add an edge to the graph.  If either endpoint does not exist in the graph, it
		is added.  Edges that do not have a decorator specified are assigned a unique
		integer decorator.
		
		The edge decorator is returned.
		"""
		# Pick an arbitrary object (number) for the newly added edge
		if e is None:
			if self.graph.graph_parent is None:
				while self.graph.next_default_edge_name in self.graph.edges_conn:
					self.graph.next_default_edge_name += 1
				e = self.graph.next_default_edge_name
				self.graph.next_default_edge_name += 1
			else:
				# if this graph is a subgraph, select an edge decorator that is legal
				# within its parent
				while self.graph.graph_parent.next_default_edge_name in self.graph.graph_parent.edges_conn:
					self.graph.graph_parent.next_default_edge_name += 1
				e = self.graph.graph_parent.next_default_edge_name
				self.graph.graph_parent.next_default_edge_name += 1
				
		# Try to insert the edge into the graph
		if e in self.graph.edges_conn:
			raise Exception, 'Edge decorator ' + str(e) + ' already exists in graph'
		else:
			both_in = True
		
			if u not in self.graph.node_edges:
				self.graph.N.add(u)
				both_in = False
			
			if v not in self.graph.node_edges:
				self.graph.N.add(v)
				both_in = False
				
			self.graph.edges_conn[e] = (u,v)
			self.graph.node_edges[u].append(e)
			
			if u != v:
				self.graph.node_edges[v].append(e)
			
			# update index lookups
			for iname,lookup in self.index_lookups.items():
				if hasattr(e,iname):
					v = getattr(e,iname)
					if v not in lookup:
						lookup[v] = [e]
					else:
						lookup[v].append(e)
			
			self.graph._notify_change_listeners_edge_added(e)
			
			if self.graph.graph_parent is not None:
				self.graph.graph_parent.E.add(u,v,e)

			return e
			
	def remove(self,e):
		"""
		Remove the specified edge from the graph
		"""
		if e not in self.graph.edges_conn:
			print e
			raise Exception, 'Edge %s does not exist' % str(e)
		
		u,v = self.graph.edges_conn[e]
		
		del self.graph.edges_conn[e]
		self.graph.node_edges[u].remove(e)
		
		if u != v:
			self.graph.node_edges[v].remove(e)
		
		# update index lookups
		for iname,lookup in self.index_lookups.items():
			if hasattr(e,iname):
				v = getattr(e,iname)
				if v not in lookup:
					raise Exception, 'Inconsistency in index lookup %s for edge %s' % (iname,str(e))
				else:
					L = lookup[v]
					L.remove(e)
					
					if len(L) == 0:
						del lookup[v]
		
		# notify change listeners
		self.graph._notify_change_listeners_edge_removed(e)
		
		# if this node is a subgraph, remove the edge in its parent
		if self.graph.graph_parent is not None:
			self.graph.graph_parent.rm_edge(e)
			
		# this node has subgraphs, remove the edge in them as well
		for sg in self.graph.subgraph_list:
			if e in sg.E:
				sg.E.remove(e)
	
	def discard(self,e):
		"""
		Remove the edge e from the graph if it exists.  Otherwise do nothing.
		"""
		if e in self.graph.edges_conn:
			self.remove(e)
			
	def difference_update(self,edges):
		"""
		Remove multiple edges from the graph.
		"""
		for e in edges:
			self.discard(e)
		
	def get(self,u,v):
		"""
		Return the first edge found that connects the two nodes specified.  If no edge is
		found, then None is returned.

		This method does not guarantee that the same edge will be returned for different
		calls using the same endpoints.  It is intended for use when it is known that 
		no multi-edges exist between the two nodes.
		"""
		elist = self.__call__(u,v)

		if len(elist) > 0:
			return elist[0]
		else:
			return None
			
	def contains(self,u,v=None):
		"""
		Return True if edge decorator u is in the edge set.  If v is specified, then return True
		if there is an edge connecting nodes u and v.
		"""
		if v is None:
			return e in self.graph.edges_conn
		else:
			return self.get(u,v) is not None			
	#####
	# Indexing methods
	def index(self,*args):
		"""
		Index the edge set using the field names specified.  The first index name
		specified is the primary index.
		"""
		# empty the index lookups
		self.index_lookups = {}
		self.primary_index = None
		
		if len(args) == 0:
			return
		
		# build each lookup
		self.primary_index = args[0]
		for iname in args:
			lookup = {}
			for e in self.graph.edges_conn.keys():
				if hasattr(e,iname):
					v = getattr(e,iname)
					
					if v not in lookup:
						lookup[v] = [e]
					else:
						lookup[v].append(e)
				
			self.index_lookups[iname] = lookup
			
		# done!
		return
		
	def reindex(self,e=None,index=Constants.ALL):
		"""
		Reindex the edges specified for the indicies specified.  e can either be one edge, a
		container of edges, or the ALL constant.  By default, the edges are reindex for all
		indices (ALL).  However if a string or a container of strings is specified, then the
		edges are reindexed only for those indices specified.  This method needs to be called
		to notify the set when the value of an indexed field changes in an edge.
		"""
		# get the list of indexes to process
		index_list = None
		
		if index == Constants.ALL:
			index_list = self.index_lookups.keys()
		elif type(index) == types.StringType :
			index_list = [index]
		elif type(index) == types.ListType:
			index_list = index
			
		# get the node list
		edge_list = None
		
		if e == Constants.ALL:
			edge_list = self.node_edges.keys()
		elif type(e) == types.StringType :
			edge_list = [n]
		elif type(e) == types.ListType:
			edge_list = e
			
		# add this node information to the index lookups
		for index in index_list:
			if index not in self.index_lookups:
				raise Exception, 'Unrecognized index: %s' % str(index)
			
			lookup = self.index_lookups[index]
			for e in edge_list:
				if hasattr(e,index):
					v = getattr(e,index)
					
					if v not in lookup:
						lookup[v] = [e]
					else:
						if e not in lookup[v]:
							lookup[v].append(e)
		
	def __clean_index_list__(self,el,iname,ival):
		"""
		Check for stale (wrong) entries in the index list that need to be cleaned out.
		For convenience, this method returns a reference to the same list (el) that was
		passed in.  At the end of this method, el will no longer contain any entries that
		do not have an attribute iname with value ival.
		"""
		i = 0
		while i < len(el):
			y = el[i]
			if not hasattr(y,iname) or y.__dict__[iname] != ival:
				el.pop(i)
			else:
				i += 1
				
		return el
		
	def __getitem__(self,x):
		"""
		Return the edge with the primary index specified.  If no edge exists with the specified
		value for the primary index, then None is returned.
		
		If a slice colon is used, G.N[x:], then a list of edges with the primary index 
		specified is returned.
		"""
		if self.primary_index is None:
			raise Exception, 'No primary index has been specified'

		el = None
		ival = None
		lookup = self.index_lookups[self.primary_index]
		
		if type(x) == types.SliceType:
			ival = x.start
						
			if ival in lookup:
				el = lookup[x]
			else:
				el = []
		else:
			ival = x
			if ival in lookup:
				el = lookup[x]
			else:
				return None
			
		self.__clean_index_list__(el,self.primary_index,ival)

		# return the appropriate value...
		if type(x) == types.SliceType:
				return list(el)
		else:
			if len(el) > 0:
				return el[0]
			else:
				return None
		
	def find(self,**args):
		"""
		Return the first edge found with the index values specified.
		"""
		L = self.find_all(**args)
		
		if len(L) == 0:
			raise KeyError, 'No edge satisfies all indices: %s' % (str(args))
		else:
			return L[0]
			
	def find_all(self,**args):
		"""
		Return a list of edges that have all the index values specified.
		"""
		# TODO: add a shortcut for probably the most likely case - there's only one k=v pair.
		# TODO: add support for values that aren't hashable... this will be a very slow procedure...
		
		# put the args in a more friendly iterable form
		args = [(k,v) for k,v in args.items()]
		
		# get an initial set of nodes to whittle down...
		candidates = None
		k,v = args[0]
		
		lookup = self.index_lookups[k]
		if v in lookup:
			candidates = list(self.__clean_index_list__(lookup[v],k,v))
		else:
			return []
			
		# now prune the list down
		for k,v in args[1:]:
			lookup = self.index_lookups[k]
			if v in lookup:
				sl = set(self.__clean_index_list__(lookup[v],k,v))
				candidates = [x for x in candidates if x in sl]
			else:
				return []
				
			if len(candidates) == 0:
				return []
				
		# if we got here, then return the remaining nodes
		return candidates
		
	def find_iter(self,**args):
		"""
		Return an iterator over all the nodes that have all the index values specified.
		"""
		for n in self.find_all(**args):
			yield n
			
	#####
	# Selection methods
	def select(x):
		"""
		Return a list of edges for which x(e) evaluates True.
		"""
		return [e for e in self.graph.edges_conn.keys() if x(e)]

	def select_iter(x):
		"""
		Return an iterator over the edges for which x(e) evaluates to True.
		"""
		for e in self.graph.edges_conn:
			if x(e):
				yield e
							
class Graph(object):
	"""
	An undirected graph.  Nodes can be any hashtable object.  Edges can have any 
	hashable decorator.  The edge (u,v) is the same as the edge (v,u).  Multi-edges
	and self-loops are supported in this graph.
	
	Every edge must have a unique decorator.  If none is provided, then an edge is 
	given a unique number decorator.
	
	Accessing nodes and edges is done through the N (or V) and E fields.  N/V is a NodeManager
	and E is an EdgeManager.  The V field may be preferred by those who are familiar with
	the formal definition of a graph as G = (V,E).
	"""
	
	def __init__(self,graph=None,node_manager=None,edge_manager=None):
		"""
		If no parameters are specified, then an empty graph is constructed.  If the graph
		is specified, then a copy of that graph's topology is made.  If the graph is directed, then
		an undirected version of that graph is made.
		
		By default, nodes are indexed by their label field and edges are not indexed at all.
		
		node_manager and edge_manager are input parameters that are for internal use only.
		"""
		
		#####
		# The basics...
		
		# the parent is never initialized here, but needs to exist as a field.  It is used for
		# subgraph relationships.
		self.graph_parent = None
		
		self.node_edges = {}
		self.edges_conn = {}
		
		self.clisteners = set()
		
		self.next_default_edge_name = 0
		
		#####
		# Setup node manager
		if node_manager is not None:
			self.V = self.N = node_manager
		else:
			self.V = self.N = NodeManager(self)
			
		self.N.index('label') # set the default indexing that the graph does...
		
		#####
		# Setup edge manager
		if edge_manager is not None:
			self.E = edge_manager
		else:
			self.E = EdgeManager(self)
		
		#####
		# copy the graph if necessary
		if graph is not None:
			# copy all nodes
			self.N.update(graph.N)
			
			# copy all edges
			if graph.is_directed():
				for e in graph.E:
					x,y = graph.endpoints(e)
					
					if not self.E.contains(x,y):
						self.E.add(x,y,e)				
			else:
				for e in graph.E:
					x,y = graph.endpoints(e)
					self.E.add(x,y,e)
		
		# BUGBUG: This list is a memory leak - we need to watch references
		# so that once nothing else points to a subgraph, we remove it from
		# this list as well and allow it to be garbage collected.
		self.subgraph_list = []
	
	####
	# Listener methods
	def add_change_listener(self,listener):
		self.clisteners.add(listener)
	
	def remove_change_listener(self,listener):
		self.clisteners.remove(listener)
	
	def _notify_change_listeners_node_added(self,n):
		for cl in self.clisteners:
			if hasattr(cl,'node_added'):
				cl.node_added(self,n)

	def _notify_change_listeners_edge_added(self,e):
		for cl in self.clisteners:
			if hasattr(cl,'edge_added'):
				cl.edge_added(self,e)
	
	def _notify_change_listeners_node_removed(self,n):
		for cl in self.clisteners:
			if hasattr(cl,'node_removed'):
				cl.node_removed(self,n)
	
	def _notify_change_listeners_edge_removed(self,e):
		for cl in self.clisteners:
			if hasattr(cl,'edge_removed'):
				cl.edge_removed(self,n)
	
	
	#####
	# other methods
	def __getitem__(self,x):
		"""
		Return the component with the primary index specified.  If no component exists with the specified
		value for the primary index, then None is returned.
		
		If a slice colon is used, G.N[x:], then a list of components with the primary index 
		specified is returned.
		"""

		is_slice = False
		if type(x) == types.SliceType:
			x = x.start
			is_slice = True
			
		args = {self.N.primary_index : x}
		comp_list = self.N.find_all(**args)
		
		args = {self.E.primary_index : x}
		comp_list.extend(self.E.find_all(**args))
			

		if is_slice:
			return comp_list
		else:
			if len(comp_list) > 0:
				return comp_list[0]
			else:
				return None
		
	def is_directed(self):
		"""
		Return whether this graph is directed.  If the graph is directed, then it should extend
		DiGraph in order to implement the basic directed graph methods.
		"""
		return False
	
	def neighbors_iter(self,v):
		"""
		Return an iterator over the neighbors of node v.
		"""
		for e in self.E(v):
			yield self.endpoint(e,v)
	
	def neighbors(self,v):
		"""
		Return the neighbors of node v.
		"""
		neighbors = []
		for e in self.E(v):
			neighbors.append(self.endpoint(e,v))
			
		return neighbors
		
	def endpoints(self,e):
		"""
		Return the endpoints of the edge.  In a directed graph, the endpoints will be ordered
		such that the source is the first endpoint and the destination is the second endpoint.
		"""
		if e not in self.edges_conn:
			raise Exception, "Edge is not in the graph"

		return self.edges_conn[e]

	def endpoint(self,e,u):
		"""
		Returns the endpoint of edge e that is not u.
		"""
		x,y = self.edges_conn[e]
		if u == x:
			return y
		else:
			return x
			
	def topology(self):
		"""
		Returns a list of the edge topology which makes up the graph.  Each entry in the
		list is a 2-tuple of (source,target) for an edge.  If multi-edges exist in the
		graph then these edges will occur multiple times in the list.
		"""
		return [t for t in self.edges_conn.values()]
	
	def subgraph(self,nodes=None,edges=None):
		"""
		Create a subgraph of this graph consisting of a subset of its nodes/edges.  nodes and edges must be
		both iteratable objects.  If only nodes are specified, then all edges connecting these nodes are
		included in the subgraph.  If only edges are specified, then all nodes connected to these edges
		are included in the subgraph.  If both nodes and edges are specified, then only these objects are
		included in the subgraph.
		
		Unless specified to the contrary, the subgraph constructed will be of the same type as the graph
		from which the subgraph is constructed.
		
		Once constructed, modifications to the subgraph are reflected in the parent of the subgraph
		"""
		
		# build the subgraph
		sgraph = None
		if self.is_directed():
			sgraph = DiGraph()
		else:
			sgraph = Graph()
		
		# make note of the graph for future updates
		self.subgraph_list.append(sgraph)
		
		# populate the subgraph
		if nodes is not None and edges is None:
			node_set = set(nodes)
			
			# add all the nodes
			sgraph.V.update(nodes)
			
			# add all edges connecting these nodes
			for n in nodes:
				for e in self.node_edges[n]:
					if e in sgraph.E:
						continue

					v = self.endpoint(e,n)
										
					if v in node_set:
						u,v = self.endpoints(e)
						sgraph.E.add(u,v,e)
			
		elif edges is not None and nodes is None:
			for e in edges:
				u,v = self.endpoints(e)
				sgraph.E.add(u,v,e)
				
		elif nodes is not None and edges is not None:
			sgraph.V.update(nodes)
			
			for e in edges:
				u,v = self.endpoints(e)
				sgraph.E.add(u,v,e)
		
		# set the parent of this graph
		sgraph.graph_parent = self
		
		# done!
		return sgraph
			
	def degree(self,node=None):
		"""
		Return the degree of this graph.  If a node is specified, then the degree
		of the node is returned.  If a list of nodes are provided, then a list of
		degrees is returned, one for each node.  If Constants.ALL is specified,
		then a list containing the degree of all the nodes in the graph is returned.
		"""
		if node is None:
			max_degree = 0
			
			for n,e in self.node_edges.items():
				if len(e) > max_degree:
					max_degree = len(e)
					
			return max_degree
		elif type(node) == types.ListType:
			degrees = [len(self.node_edges[n]) for n in node]
			return degrees
		elif node == Constants.ALL:
			degrees = [len(e) for n,e in self.node_edges.items()]
			return degrees
		else:
			return len(self.node_edges[node])


####################################################################################
#
# Directed Graph-Specific Code
#

class DirectedNodeManager(NodeManager):
	"""
	This class provides the N field in the directed graph.  It behaves like a set of nodes but
	also provides some additional utilities: selection and node indexing.
	"""
	def __init__(self,graph):
		NodeManager.__init__(self,graph)

	#####
	# container methods
	
	# Implemented in NodeManager
	# def __call__(self):

	# Implemented in NodeManager
	#def __iter__():

	# Implemented in NodeManager
	#def __contains__(self,n):

	# Implemented in NodeManager
	#def __len__(self):

	#####
	# Node addition/removal
	
	# Implemented in NodeManager
	#def add(self,n):
	
	# Implemented in NodeManager
	#def update(self,nodes):

	# Implemented in NodeManager
	#def remove(self,n):
		
	# Implemented in NodeManager
	#def difference_update(self,nodes):

	#####
	# Indexing methods

	# Implemented in NodeManager	
	#def index(self,*args):

	# Implemented in NodeManager
	#def reindex(self,n=None,index=ALL):

	# Implemented in NodeManager
	#def __getitem__(self,x):

	# Implemented in NodeManager
	#def find(self,**args):

	# Implemented in NodeManager
	#def find_all(self,**args):
	
	# Implemented in NodeManager
	#def find_iter(self,**args):

	#####
	# Selection methods
	
	# Implemented in NodeManager
	#def select(x):

	# Implemented in NodeManager
	#def select_iter(x):

class DirectedEdgeManager(EdgeManager):
	"""
	This class provides the E field in the directed graph.  It behaves like a set of edges but
	also provides some additional utilities: selection and edge indexing.
	"""
	def __init__(self,graph):
		EdgeManager.__init__(self,graph)

	#####
	# container methods
	def __call__(self,u=None,v=None,directed=True):
		"""
		Return a list of the edges in this graph.  The list is independent of the internal
		collection that is maintained by the Graph object.  Thus, this list may be modified
		without affecting the graph from which it came.

		If only u is specified and directed is True, then only edges with u as their source are 
		returned.  If directed is False, then all edges adjacent to u are returned.

		If only v is specified and directed is True, then only edges with v as their target are 
		returned.  If directed is False, then all edges adjacent to v are returned.

		If u and v are specified then the list of edges connecting u to v are returned.  If directed
		is False, then all edges connecting u and v are returned irrespective of the direction.
		
		If it is True, then an iterator is returned rather than a list.
		"""
		elist = None
		
		if v is None:
			if u is None:
				elist = list(self.graph.edges_conn.keys())
			else:
				if u not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(u)

				if directed is False:
					if self.graph.node_edges[u] is None:
						elist = []
					else:
						elist = self.graph.node_edges[u]
				else:
					elist = []

					if self.graph.node_edges[u] is not None:
						for e in self.graph.node_edges[u]:
							x,y = self.graph.edges_conn[e]

							if x == u:
								elist.append(e)
		else:
			if u is None:
				if directed is False:
					if self.graph.node_edges[v] is None:
						elist = []
					else:
						elist = list(self.graph.node_edges[v])
				else:
					elist = []

					if self.graph.node_edges[v] is not None:
						for e in self.graph.node_edges[v]:
							x,y = self.graph.edges_conn[e]

							if y == v:
								elist.append(e)				
			else:
				if u not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(u)

				if v not in self.graph.node_edges:
					raise Exception, '%s is not in the graph' % str(v)

				elist = []

				for e in self.graph.node_edges[u]:
					x,y = self.graph.edges_conn[e]

					if directed:
						if (y == v and x == u):
							elist.append(e)
					else:
						if (y == v and x == u) or (x == v and y == u):
							elist.append(e)

		return elist

	# Implemented in EdgeManager
	#def __iter__():

	# Implemented in EdgeManager
	#def __contains__(self,e):

	# Implemented in EdgeManager
	#def __len__(self):

	#####
	# Node addition/removal
	
	# Implemented in EdgeManager
	#def add(self,u,v,e=None):

	# Implemented in EdgeManager
	#def remove(self,e):

	# Implemented in EdgeManager
	#def difference_update(edges):
	
	def iter(self,u=None,v=None,directed=True):
		"""
		Return an iterator over a subset of edges.
		
		If u or v is specified, then all edges leaving u or entering v are included.
		
		If u and v are specified then all the edges connecting u to v are included.
		
		By default, directionality is considered when determining what edges to return.
		However, if directed is False, then this method treats the graph like an undirected
		graph.
		"""
		for e in self(u,v,directed):
			yield e
		
	def get(self,u,v,directed=True):
		"""
		Return the first edge found that connects the two nodes specified.

		This method does not guarantee that the same edge will be returned for different
		calls using the same endpoints.  It is intended for use when it is known that 
		no multi-edges exist between the two nodes.

		By default this method respects the direction indicated (from u to v).  However, if
		directed is False, then this method finds any edge connecting u to v.  The first one found
		is returned.
		"""

		# this code is the same as appears in part of edges ... but it's repeated here for speed.
		for e in self.graph.node_edges[u]:
			x,y = self.graph.edges_conn[e]

			if directed:
				if (y == v and x == u):
					return e
			else:
				if (y == v and x == u) or (x == v and y == u):
					return e

		return None

	def contains(self,u,v=None,directed=True):
		"""
		If only u is specified, then this method returns True 
		if the specified edge decorator is in this graph.

		If both u and v are specified, then this method returns True
		if there is an edge (u,v) in the graph.

		By default this method tests for directed edges.  However, if directed is False,
		then the test for the edge is undirected.
		"""		
		if v is None:
			return (u in self.graph.edges_conn)
		else:
			return self.get(u,v,directed) is not None
						
	#####
	# Indexing methods
	
	# Implemented in EdgeManager
	#def index(self,*args):

	# Implemented in EdgeManager
	#def reindex(self,e=None,index=ALL):

	# Implemented in EdgeManager
	#def __getitem__(self,x):

	# Implemented in EdgeManager
	#def find(self,**args):
	
	# Implemented in EdgeManager
	#def find_all(self,**args):

	# Implemented in EdgeManager
	#def find_iter(self,**args):

	#####
	# Selection methods
	
	# Implemented in EdgeManager
	#def select(x):

	# Implemented in EdgeManager
	#def select_iter(x):
							
class DiGraph(Graph):
	"""
	A directed graph with support for multi-edges and self-loops.

	As in the undirected graph, every edge must have a unique decorator.  If None is provided, 
	then an edge is given a unique number decorator.
	
	Also as in the undirected graph, by default, nodes are indexed by their label field and 
	edges are not indexed at all.

	All directed graphs should extend this class in order to ensure that they implement
	all methods expected of directed graphs.
	
	Accessing nodes and edges is done through the N and E fields.  N is a NodeManager
	and E is an EdgeManager.
	"""

	def __init__(self, graph=None, node_manager=None, edge_manager=None):
		"""
		This method creates a new directed graph.  A copy of another directed graph can be made
		by specifying the graph parameter.
		"""
		if graph is not None and not graph.is_directed():
			raise Exception,'Directed graphs can only copy other directed graphs.'

		nm = node_manager
		if nm is None:
			nm = DirectedNodeManager(self)
			
		em = edge_manager
		if em is None:
			em = DirectedEdgeManager(self)

		# let the Graph class handle all other initialization
		Graph.__init__(self, graph, node_manager=nm, edge_manager=em)			

	# Implemented in Graph
	#def __getitem__(self,x):
		
	def is_directed(self):
		return True

	def source(self,e):
		"""
		Return the source of the edge.
		"""
		u,v = self.edges_conn[e]

		return u

	def target(self,e):
		"""
		Return the target of the edge.
		"""
		u,v = self.edges_conn[e]

		return v

	# Implemented in Graph
	# def endpoints(self,e):

	# Implemented in Graph
	# def endpoint(self,e,u):

	# Implemented in Graph
	# def topology(self):

	# Implemented in Graph
	# def subgraph(self,nodes=None,edges=None):

	def indegree(self,node=None):
		"""
		Return the in-degree of this graph.  If a node is specified, then the in-degree
		of the node is returned.  If a list of nodes are provided, then a list of
		in-degrees is returned, one for each node.  If Constants.ALL is specified,
		then a list containing the in-degree of all the nodes in the graph is returned.
		"""
		if node is None:
			max_degree = 0

			for n,el in self.node_edges.items():
				ie = [e for e in el in self.edges_conn[e][1] == n]

				if len(ie) > max_degree:
					max_degree = len(ie)

			return max_degree
		elif type(node) == types.ListType:
			degrees = []
			for n in node:
				degrees.append(len([e for e in self.node_edges[n] if self.edges_conn[e][1] == n]))

			return degrees
		elif node == Constants.ALL:
			degrees = []
			for n in self.node_edges:
				degrees.append(len([e for e in self.node_edges[n] if self.edges_conn[e][1] == n]))

			return degrees
		else:
			return len([e for e in self.node_edges[node] if self.edges_conn[e][1] == node])

	def outdegree(self,node=None):
		"""
		Return the out-degree of this graph.  If a node is specified, then the out-degree
		of the node is returned.  If a list of nodes are provided, then a list of
		out-degrees is returned, one for each node.  If Constants.ALL is specified,
		then a list containing the out-degree of all the nodes in the graph is returned.
		"""
		if node is None:
			max_degree = 0

			for n,el in self.node_edges.items():
				oe = [e for e in el in self.edges_conn[e][0] == n]

				if len(oe) > max_degree:
					max_degree = len(oe)

			return max_degree
		elif type(node) == types.ListType:
			degrees = []
			for n in node:
				degrees.append(len([e for e in self.node_edges[n] if self.edges_conn[e][0] == n]))

			return degrees
		elif node == Constants.ALL:
			degrees = []
			for n in self.node_edges:
				degrees.append(len([e for e in self.node_edges[n] if self.edges_conn[e][0] == n]))

			return degrees
		else:
			return len([e for e in self.node_edges[node] if self.edges_conn[e][0] == node])

	def neighbors_iter(self,v,directed=True):
		"""
		Return an iterator over the neighbors of node v.
		"""
		for e in self.E(v,directed=directed):
			yield self.endpoint(e,v)

	def neighbors(self,v,directed=True):
		"""
		Return the neighbors of node v.
		"""
		neighbors = []
		for e in self.E(v,directed=directed):
			neighbors.append(self.endpoint(e,v))

		return neighbors
