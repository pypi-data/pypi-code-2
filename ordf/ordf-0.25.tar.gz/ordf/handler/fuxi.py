"""
.. autoclass:: FuXiReasoner
   :show-inheritance:
"""

from ordf.graph import Graph, _Graph, ConjunctiveGraph
from ordf.handler import Handler, HandlerPlugin
from ordf.namespace import CS, DC, FOAF, ORDF, RDF
from ordf.term import URIRef
from ordf.vocab.foaf import Agent

from FuXi.Rete.Network import ReteNetwork
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Horn.HornRules import HornFromN3
from FuXi.Rete.Util import generateTokenSet
from FuXi.Syntax.InfixOWL import Class, Property
from StringIO import StringIO
from getpass import getuser
from string import strip

from logging import getLogger
log = getLogger(__name__)

class FuXiReasoner(HandlerPlugin):
    """
    This handler implements a production rule reasoning system. In
    normal operation it would listen to a one queue using
    :class:`~ordf.handler.queue.RabbitHandler` and the handler would
    be configured to write to a different exchange using
    :class:`~ordf.handler.queue.RabbitQueue`.

    When the :meth:put method is called, it will be with a store that
    already contains a :class:`~ordf.changeset.ChangeSet`. This handler
    reasons over all of the non-changeset graphs in the store using the
    rules and for whatever statements it is able to infer adds them to
    the graphs and creates a new, (incremental) changeset.

    The resulting store is then passed back up to the handler where
    it should go out the outbound handlers and eventually be indexed.

    The configuration for this is slightly subtle, see the
    :ref:`configuring-inferencing` section of the configuration guide
    for how to do this.

    :param rule_modules: comma separated list of modules that export
        an :meth:`inference_rules` method
    """
    def __init__(self, rule_modules, foaf_mbox="fuxi-discussion@googlegroups.com", **kw):
        super(HandlerPlugin, self).__init__(**kw)
        self.rule_modules = map(strip, rule_modules.split(",")) if rule_modules else []
        self.busy = False
        ### FuXi, Agent of Change
        self.agent = Agent()
        self.agent.name("FuXi")
        self.agent.mbox(foaf_mbox)
        self.agent.nick(getuser())
        _s,_p,self.agent_hash = self.agent.one((self.agent.identifier, FOAF.mbox_sha1sum, None))

    def _get_network(self):
        if not hasattr(self, "__network__"):
            rstore, rgraph = SetupRuleStore()
            self.__network__ = ReteNetwork(rstore)
            log.info("startup %s" % self.__network__)
            for modname in self.rule_modules:
                __import__(modname, {}, {}, ["inference_rules"]
                           ).inference_rules(self.handler, self.__network__)
                log.info("rules from %s %s" % (modname, self.__network__))
        return self.__network__
    def _set_network(self, network):
        setattr(self, "__network__", network)
    def _del_network(self):
        if hasattr(self, "__network__"):
            delattr(self, "__network__")
    network = property(_get_network, _set_network, _del_network)

    def put(self, store):
        if self.busy:
            return
        self.busy = True

        inferredFacts = Graph()
        self.network.reset(inferredFacts)

        ## workaround for bug in reset()
        ## http://code.google.com/p/fuxi/issues/detail?id=17
        self.network.inferredFacts = inferredFacts

        if isinstance(store, _Graph):
            store = store.store

        def _get(graph):
            if isinstance(graph, basestring):
                identifier = graph
            else:
                identifier = graph.identifier
            for ctx in store.contexts():
                if ctx.identifier == identifier:
                    return ctx
        self.get = _get

        ### widen the set of statements to inference from
        ### any references, at one degree from the contents of
        ### the store, to external resources, add them to the
        ### store
        for s,p,o in ConjunctiveGraph(store).triples((None, None, None)):
            if isinstance(o, URIRef):
                o_graph = self.get(o)
                if not o_graph:
                    continue
                o_graph_copy = Graph(store=store, identifier=o_graph.identifier)
                for statement in o_graph.triples((None, None, None)):
                    o_graph_copy.add(statement)

        ### we don't reason on changesets, so make a list of changesets we have
        changesets = []
        facts = []
        for ctx in store.contexts():
            if ctx.exists((ctx.identifier, RDF.type, CS.ChangeSet)):
		log.debug("skip %s" % ctx.identifier)
                changesets.append(ctx)
            else:
                facts.append(ctx)

        ### retract previously inferred statements
        facts = [self.retract(g) for g in facts]

        ### feed data to the reasoner
        for fact_graph in facts:
            self.network.feedFactsToAdd(generateTokenSet(fact_graph))

        #log.debug("inferred\n%s" % inferredFacts.serialize(format="n3"))

        ### construct the change context

        change_ctx = self.handler.context(self.agent, "FuXi machine reasoning")
        for cs in changesets:
            ### for previous changeset, just preserve it in the change context
            ### store
            copy = Graph(store=change_ctx.store, identifier=cs.identifier)
            copy += cs

        for fact_graph in facts:
            ### add the relevant inferred facts
            copy = Graph(identifier=fact_graph.identifier)
            copy += fact_graph
            log.debug("facts %s" % fact_graph.identifier)
            for subj in fact_graph.distinct_subjects():
                inferred = inferredFacts.bnc((subj, None, None))
                log.debug("inferred %d facts about %s" % (len(inferred), subj))
                copy += inferred
                
            change_ctx.add(copy)

        ### save the changes
        ### this doesn't loop back through this function because
        ### at this point self.busy == True
        cs = change_ctx.commit()
        ### if we haven't been able to make any inferences, this changeset
        ### will be empty. but the preceding changeset will not, so we
        ### still need to send it to the indices
        if not cs:
            self.handler.put(change_ctx.store)

        #print cs.serialize(format="n3")

        ### get ready for the next message
        self.get = lambda x: None
        self.busy = False

        ### prevent further propagation of the original change bundle
        return True

    def retract(self, graph):
        """
        Retract statements previously inferred about graph by walking
        its change history and rolling back the most recent changeset
        that was made by this module
        """
        for cs in self.handler.history(graph.identifier):
            if isinstance(cs, list):
                log.warning("%s's change history branches before we get to inferred facts" % graph.identifier)
                break
            for creator in cs.objects(cs.identifier, DC.creator):
                if cs.exists((creator, FOAF.mbox_sha1sum, self.agent_hash)):
                    copy = Graph(identifier=graph.identifier)
                    copy += graph
                    cs.undo(copy)
                    ## preserve changeset linkage
                    copy.remove((copy.identifier, ORDF.changeSet, None))
                    [copy.add(change) for change in graph.triples((graph.identifier, ORDF.changeSet, None))]
                    return copy
        return graph
