from ordf.vocab.opmv import Agent, Process
from ordf.graph import Graph
from ordf.namespace import RDF
from ordf.term import Literal
from pkg_resources import get_distribution

def test_01_proc_version():
    g = Graph()
    a = Agent()
    a.nick("test")
    p = Process()
    p.agent(a)
    p.result(g)

    dist = get_distribution("ordf")
    assert g.exists((None, RDF["value"], Literal(dist.version)))
