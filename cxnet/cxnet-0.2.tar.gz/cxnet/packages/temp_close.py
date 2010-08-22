def close(node):
    return G.predecessors(node) + G.successors(node) + [node]
