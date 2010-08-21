import os
import pkg_resources
from getpass import getuser
from logging import getLogger
from ordf.graph import Graph

log = getLogger(__name__)

def rdf_data():
    graph_uri = "http://ordf.org/schema/ordf"
    log.info("Loading %s" % graph_uri)

    graph = Graph(identifier=graph_uri)
    fp = pkg_resources.resource_stream("ordf.vocab", os.path.join("n3", "ordf.n3"))
    graph.parse(fp, format="n3")
    fp.close()

    from ordf.vocab.opmv import Agent, Process
    agent = Agent()
    agent.nick(getuser())
    proc = Process()
    proc.result(graph)

    yield graph
