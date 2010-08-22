import igraph
from packages import get_igraph_from_cache
g=get_igraph_from_cache()
print g.vcount()
print g.ecount()
