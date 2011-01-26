from ordf.graph import Graph
import os, pkg_resources

def rdf_data():
    for filename in pkg_resources.resource_listdir("ordf.onto", "n3"):
        if not filename.endswith(".n3"):
            continue
        fp = pkg_resources.resource_stream("ordf.onto", os.path.join("n3", filename))
        fbase = filename[:-3]
        g = Graph(identifier="http://ordf.org/lens/%s" % fbase)
        g.parse(fp, format="n3")
        yield g
