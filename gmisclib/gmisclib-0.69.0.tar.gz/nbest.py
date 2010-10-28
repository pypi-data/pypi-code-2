"""Beam search through a graph."""

class node:
	__doc__ = """This is a node of a graph, it includes links to other nodes."""

	def __init__(self, cost=0.0, label=None, terminal=0, comment=None):
		"""Create a node, with a specified cost (used in the beam search),
		and a label (arbitrary information).
		Terminal nodes are marked, and terminate the search."""

		self.terminal = terminal
		self.out = []
		self.cost = cost
		self.label = label
		self.comment = comment

	def add(self, nextnode, cost=0.0, label=None):
		"""Add a link from self to nextnode.
		Links can have a cost and label, too."""
		self.out.append( (nextnode, cost, label) )
		return nextnode


	def __str__(self):
		return "<node term=%d label=%s nout=%d cost=%f>" % (self.terminal, str(self.label),
									len(self.out), self.cost)

	__repr__ = __str__
	



class _l_list:
	__doc__ = """Linked list."""

	def __init__(self, contents, link):
		self.link = link
		self.contents = contents

	def walk(self):
		o = [self.contents]
		while self.link is not None:
			self = self.link
			o.append(self.contents)
		return o

	def rwalk(self):
		o = self.walk()
		o.reverse()
		return o



def go(graph, nbeam, cbeam):
	"""Search the graph for the lowest cost routes.
	Returns [ (cost, route), ...] where cost is the cost of a route,
	and route is [node, node, node, ...] the list of nodes on the route.
	Routes are sorted in order of increasing cost.
	"""

	assert isinstance(graph, node), "Non-node starts graph: %s" % str(graph)
	# current = [ (0.0, graph, [graph]) ]
	current = [ (0.0, graph, _l_list(graph, None)) ]
	terminate = [ ]

	while 1:
		nextstep = []
		for (cost, anode, path) in current:
			assert isinstance(anode, node), "Non-node in graph: %s" % str(anode)
			for (nnode, c, ll) in anode.out:
				# print anode, "->", nnode
				newcost = cost + nnode.cost + c
				newpath = _l_list(nnode, path)
				# newpath = path + [nnode]
				if nnode.terminal:
					terminate.append( ( newcost, newpath) )
				else:
					nextstep.append( (newcost, nnode, newpath) )
		if len(nextstep) == 0:
			break
		nextstep.sort()
		if len(nextstep) > nbeam:
			nextstep = nextstep[:nbeam]
		costlimit = nextstep[0][0] + cbeam
		i = 0
		while i < len(nextstep):
			if nextstep[i][0] > costlimit:
				break
			i += 1
		current = nextstep[:i]
	terminate.sort()
	if len(terminate) > nbeam:
		terminate = terminate[:nbeam]
	costlimit = terminate[0][0] + cbeam
	o = []
	for (cost, path) in terminate:
		if cost > costlimit:
			break
		o.append( (cost, path.rwalk() ) )
	return o



def test():
	graph = node(0.0, "A")
	graph.add(node(0.0, "B")).add(node(0.1, "C")).add(node(0.2, "D")).add(node(-0.3, terminal=1, label="E"))
	graph.add(node(1.0, "a")).add(node(1, "b")).add(node(2, terminal=1, label="c"))
	graph.add(node(0.0, label="q", terminal=1), 1.0, label="edge")
	print go(graph, 100, 1000.0)


if __name__ == '__main__':
	test()
