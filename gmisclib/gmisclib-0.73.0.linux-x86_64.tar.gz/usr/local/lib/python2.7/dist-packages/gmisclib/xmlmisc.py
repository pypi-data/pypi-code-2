"""This contains helper functions and classes for processing XML,
based on the ElementTree module.
"""

import xml.etree.cElementTree as elTree


def treestructures(elt):
	"""This gives you a view of what the XML hierarchy looks like.
	It's intended to help you deduce the correct DTD, or just to understand
	how the data is arranged.  It shows you the kinds of leaf tags you have
	and the kinds of paths through the XML tree necessary to get to each leaf.
	@param elt: an XML tree structure
	@type elt: an xml.etree.cElementTree Element
	@return: a sequence of embedding lists.   Each embedding list contains
		the tags you go through en route to a leaf node.   So,
		C{<a> <b> <c>x</c> </b> </a>} would yield a list C{['a', 'b', 'c']}
		and C{<a> <b>x</b> <c> y </c> </a>} would yield
		C{['a', 'b']} and C{['a', 'c']}.
	@rtype: iterator(list(str))
	"""
	assert elTree.iselement(elt)
	if len(elt) == 0:
		return set( [ ( elt.tag,) ] )
	rv = set()
	eltt = (elt.tag,)
	for e in elt:
		for re in treestructures(e):
			rv.add(eltt + re)
	return rv


class _tmpnode(object):
	def __init__(self, el, parent, i):
		self.e = el
		self.p = parent
		self.id = id(el)
		self.i = i
	
	def __hash__(self):
		return self.id
	
	def __eq__(self, other):
		return self.e() is other.e()

	def check(self, e):
		if self.e is not e:
			raise ValueError, "Whoops"
		return self




class loc_finder(object):
	"""A class for specifying a path through an XML tree to a particular node.
	Basically, this is a way of referring to a particular element that will
	survive serialization of the XML tree.
	"""

	def __init__(self, root_element):
		"""Create an instance of the L{loc_finder} class and initialize it from a
		portion of an XML tree.
		@param root_element: the top element of the tree (or subtree).   All positions
			will be computed relative to this element.
		@type root_element: L{elTree.Element}.
		@note: This walks the entire XML file and builds a cache, so it is expensive
			to initialize, but fairly cheap to use.
		@note: this works on L{elTree.Element} object, not on an L{elTree.ElementTree}
			object.    If you have x which is a L{elTree.ElementTree}, then use
			loc_finder(x.get_root()).
		"""
		self.tree = root_element
		self.up = {}
		self.maxdepth =  self.__walk(self.tree)


	def __walk(self, tree):
		depth = 0
		for (i,t) in enumerate(tree):
			self.up[id(t)] = _tmpnode(t, tree, i)
			td = self.__walk(t)+1
			if td > depth:
				depth = td
		return depth + 1


	def find_up(self, el, tag):
		"""Search upwards (towards the document root) to find the
		first tag of the specified type.
		@type tag: L{str}
		@param tag: the tag of an XML element.
		@rtype: L{elTree.Element}
		@return: The smallest enclosing element that has the specified tag.
		"""
		depth = 0
		while el is not self.tree:
			if el.tag == tag:
				return el
			tmp = self.up[id(el)].check(el)
			el = tmp.p
			if depth >= self.maxdepth:
				raise ValueError, "Whoops"
			depth += 1
		return None
	

	def path(self, el):
		"""Describe the path through an XML file to a specific element.
		@param el: The target element.
		@return: A tuple, intended to be handed to L{walkto}.
		@type el: L{elTree.Element}
		@rtype: L{tuple}C{(L{int})}
		"""
		rv = []
		while el is not self.tree:
			tmp = self.up[id(el)].check(el)
			rv.append(tmp.i)
			el = tmp.p
			if len(rv) >= self.maxdepth:
				raise ValueError, "Whoops"
		rv.reverse()
		return tuple(rv)


	@staticmethod
	def walkto(tree, path):
		"""If you have a elementTree and a path obtained from L{loc_finder.path}(),
		this will walk you back to the same element.
		@type path: C{tuple(int)}
		@rtype: L{elTree.Element}
		@return: The element specified by the C{path}, in the C{tree}.
		"""
		if not path:
			return tree
		p0 = path[0]
		for (i,t) in enumerate(tree):
			if i == p0:
				return loc_finder.walkto(t, path[1:])
	
	
def test_loc_finder():
	tree = elTree.Element('a')
	t1 = elTree.Element('b')
	t2 = elTree.Element('c')
	tree.append(t1)
	tree.append(t2)
	top = elTree.Element('0')
	top.append(tree)

	lf = loc_finder(top)
	assert loc_finder.walkto(top, lf.path(t2)) is t2
	assert loc_finder.walkto(top, lf.path(t1)) is t1
	assert loc_finder.walkto(top, lf.path(tree)) is tree

if __name__ == '__main__':
	test_loc_finder()
