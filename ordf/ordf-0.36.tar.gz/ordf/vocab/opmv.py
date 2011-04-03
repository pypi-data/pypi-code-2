"""
.. autoclass:: Agent
   :show-inheritance:
.. autoclass:: Process
   :show-inheritance:
"""
__all__ = ["Agent", "Process"]

from ordf.term import BNode, Literal, URIRef, Node
from ordf.graph import Graph
from ordf.namespace import OPMV, ORDF, RDF, RDFS, TIME, FOAF
from ordf.utils import get_identifier
from ordf.vocab import foaf
from pkg_resources import get_distribution
from datetime import datetime
from socket import gethostname
import sys, os

class Agent(foaf.Agent):
    """
    .. autoattribute:: __types__
    """
    __types__ = [OPMV["Agent"]]
    "* *opmv:Agent*"

    def __init__(self, *av, **kw):
        super(Agent, self).__init__(*av, **kw)
        self.add((self.identifier, RDF["type"], FOAF["Agent"]))

class Process(Graph):
    """
    .. autoattribute:: __types__

    .. automethod:: agent
    .. automethod:: use
    .. automethod:: result
    .. automethod:: add_distribution

    """
    __types__ = [OPMV["Process"]]
    """
    * *opmv:Process*
    """
    __distributions__ = {}
    @classmethod
    def add_distribution(cls, name):
        """
        Add a distribution (python package in the setuptools
        sense) by name to be recorded in provenance graph.

        This is a classmethod that should be called only once
        per distribution. The distribution "ordf" is already
        present.
        """
        try:
            dist = get_distribution(name)
        except DistributionNotFound:
            dist = None
        cls.__distributions__[name] = dist

    def __init__(self, *av, **kw):
        super(Process, self).__init__(*av, **kw)
        self.add((self.identifier, RDF.type, OPMV["Process"]))
        self.time = None
        self._finished = False
        self.add((self.identifier, ORDF["cmdline"], Literal(self.cmdline())))
        self.add((self.identifier, ORDF["hostname"], Literal(gethostname())))
        self.add((self.identifier, ORDF["pid"], Literal(os.getpid())))
        descr = "%s on %s (%s)" % (os.path.basename(sys.argv[0]), gethostname(), os.getpid())
        self.add((self.identifier, RDFS["label"], Literal(descr)))

        for name, dist in self.__distributions__.items():
            b = BNode()
            self.add((self.identifier, ORDF["version"], b))
            self.add((b, RDFS["label"], Literal(name)))
            if dist is not None:
                self.add((b, RDF["value"], Literal(dist.version)))

    def cmdline(self):
        from sys import argv
        args = []
        for a in argv:
            a = a.replace("'", "\\'")
            if " " in a or '"' in a:
                a = "'" + a + "'"
            args.append(a)
        return " ".join(args)
        
    def start(self):
        self.time = BNode()
        self.add((self.time, RDF.type, TIME["Interval"]))
        self.add((self.identifier, OPMV["wasPerformedAt"], self.time))

        start = BNode()
        self.add((self.time, TIME["hasBeginning"], start))
        self.add((start, RDF.type, TIME["Instant"]))
        self.add((start, TIME["inXSDDateTime"], Literal(datetime.utcnow())))

    def finish(self):
        if self._finished:
            return
        self._finished = True
        if self.time is None:
            self.time = BNode()
            self.add((self.time, RDF["type"], TIME["Instant"]))
            self.add((self.identifier, OPMV["wasPerformedAt"], self.time))
            self.add((self.time, TIME["inXSDDateTime"], Literal(datetime.utcnow())))
        else:
            end = BNode()
            self.add((self.time, TIME["hasEnd"], end))
            self.add((end, RDF.type, TIME["Instant"]))
            self.add((end, TIME["inXSDDateTime"], Literal(datetime.utcnow())))

    def clone(self):
        p = Process(identifier=self.identifier)
        p.remove((None, None, None))
        p.time = self.time
        p += self
        return p

    def use(self, what):
        """
        Add the given :class:`ordf.term.URIRef` or :class:`ordf.term.Graph` as
        a resource used by this process.
        """
        if isinstance(what, Node):
            ident = what
        else:
            ident = get_identifier(what)
        self.add((self.identifier, OPMV["used"], ident))

    def agent(self, agent):
        """
        Set the :class:`Agent` that is controlling this :class:`Process`

        :arg agent: a :class:`ordf.graph.Graph` or instance of :class:`Agent`
        """
        ident = get_identifier(agent)
        self.add((self.identifier, OPMV["wasControlledBy"], ident))
        self += agent

    def result(self, graph):
        """
        Cause linkages to this proces to be added to the given :class:`Graph`
        """
        self.finish()
        graph.add((graph.identifier, RDF["type"], OPMV["Artifact"]))
        graph.remove((graph.identifier, OPMV["wasGenereatedBy"], None))
        graph.add((graph.identifier, OPMV["wasGeneratedBy"], self.identifier))
        graph += self
Process.add_distribution("ordf")
