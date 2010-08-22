import sys
sys.path.insert(0, ".")

graph_module = None

try:
    from igraph import plot
except ImportError:
    pass
else:
    graph_module="igraph"
    from igraphtools import igraph_from_dot
    from igraphtools import igraph_from_vertices_edges
    from debnetworki import debnetwork
    from debnetworki import CXNet
    from igraph import summary, plot

if graph_module is None:
    try:
        from networkx import diameter
    except ImportError:
        pass
    else:
        graph_module="networkx"
        has_networkx = True
        from networkx import barabasi_albert_graph, erdos_renyi_graph, complete_graph
        from networkx import connected_components, connected_component_subgraphs
        from networkx import draw

if graph_module is None:
    print """I could not import neither IGraph nor NetworkX.
Try to install one of them properly.
Without one of them cxnet can not work with networks/graphs."""
elif graph_module == "igraph":
    print """I will use IGraph."""
elif graph_module == "networkx":
    print """I will use NetworkX."""

from degdist import DegreeDistribution, KolmogorovSmirnoff_statistics, split
from archives import get_netdata, put_debnetdata
