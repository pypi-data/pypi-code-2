"""
The ChangeSet Class
-------------------

.. autoclass:: ChangeSet
   :show-inheritance:
"""

__all__ = ["ChangeSet"]

import logging

from ordf.namespace import *
from ordf.term import *
from ordf.utils import *
from ordf.graph import Graph
from ordf.vocab.foaf import Agent
from datetime import datetime
from uuid import uuid1

class ChangeSet(Graph):
    """
    ChangeSet Graph. Typically one does something like,

    .. code-block:: python

        cs = ChangeSet("some name", "some reason")
        cs.diff(g1_orig, g1_new)
        cs.diff(g2_orig, g2_new)
        cs.commit()


    There are two instantiation paths. The usual one where *name* and *reason
    parameters are supplied is intended for constructing new changesets. The
    other where *store* and *identifier* are supplied is intended for accessing
    previously stored changesets.

    :param name: The name of the person or entity creating this changeset. This
                 may be a string or an rdflib datatype (e.g. 
                 :class:`~rdflib.term.URIRef`, :class:`~rdflib.term.Literal`)
    :param reason: A description of the change. This may be a string or an
                   instance of :class:`~rdflib.term.Literal`
    :param store: When obtaining an existing changeset, the :class:`rdflib.store.Store`
                  which contains it.
    :param identifier: When obtaining an existing changeset, the graph identifier
                       that should be used to find it in the store
    :param namespace: When changesets are created they are assigned a name. The
                      name is generated using the :func:`uuid.uuid1` function.
                      It is then appended to the provided namespace.

    .. data:: metadata

        A representation of the metadata of this changeset graph. This excludes
        any *cs:addition* and *cs:removal* properties

    .. automethod:: diff
    .. automethod:: commit
    .. automethod:: rollback
    .. automethod:: apply
    .. automethod:: undo
    """
    def __init__(self, name=None, reason=None, store="IOMemory", identifier=None, namespace=UUID):
        if identifier is None:
            if not isinstance(namespace, Namespace):
                namespace = Namespace(namespace)
            identifier = namespace[unicode(uuid1())]
            self.__frozen__ = False
        else:
            self.__frozen__ = True
        super(ChangeSet, self).__init__(store=store, identifier=identifier)
        bind_ns(self)

        self.log = logging.getLogger("ordf.changeset")
        if name is not None:
            if not isinstance(name, Node):
                name = Literal(name)
                self.agent = Agent()
                self.agent.name(name)
            else:
                self.agent = name
        else:
            self.agent = None

        if reason is not None:
            if isinstance(reason, Node):
                self.reason = reason
            else:
                self.reason = Literal(reason)
        else:
            self.reason = None

        self.changes = 0

    def diff(self, orig, new):
        """
        Populate the ChangeSet with the differences between orig and new.

        :param orig: original graph
        :param new: new graph
        :return: number of distinct changes (additions + removals)
        """
        if self.__frozen__:
            raise Exception("%s already frozen" % self.identifier)
        if self.agent is None:
            raise ValueError("name must not be None")
        if self.reason is None:
            raise ValueError("reason must not be None")
        if orig.identifier != new.identifier:
            raise ValueError("can only diff versions of the same graph")

        ## remove any changeset in the new graph
        new.remove((new.identifier, ORDF.changeSet, None))

        changes = 0

        preceding = []
        ## any triples that have been removed
        for statement in orig.triples((None, None, None)):
            if statement not in new.triples(statement):
                s,p,o = statement
                if s == orig.identifier and p == ORDF.changeSet:
                    preceding.append(o)
                    continue
                self.reify(CS.removal, (s,p,o,orig.identifier))
                changes += 1

        ## any triples that have been added
        for statement in new.triples((None, None, None)):
            if statement not in orig.triples(statement):
                s,p,o = statement
                self.reify(CS.addition, (s,p,o,orig.identifier))
                changes += 1

        if changes > 0:
            ## remove preceding changesets
            for cs in preceding:
                self.reify(CS.removal, (orig.identifier, ORDF.changeSet, cs, orig.identifier))
            ## add linkage to the preceding changeset(s)
            for s,p,o in orig.triples((orig.identifier, ORDF.changeSet, None)):
                self.add((self.identifier, CS.precedingChangeSet, o))

            ## add linkage to the new changeset
            self.add((self.identifier, CS.subjectOfChange, new.identifier))
            add = BNode()
            self.add((self.identifier, CS.addition, add))
            self.add((add, RDF.type, RDF.Statement))
            self.add((add, RDF.subject, new.identifier))
            self.add((add, RDF.predicate, ORDF.changeSet))
            self.add((add, RDF.object, self.identifier))
            self.add((add, ORDF.graph, new.identifier))
  
            ## add linkage to the graph
            new.add((new.identifier, ORDF.changeSet, self.identifier))

        self.changes += changes

        return changes

    def commit(self):
        """
        Commit the changes, mark the changeset read-only.
        """
        if self.__frozen__:
            raise Exception("%s already frozen" % self.identifier)
        self.__frozen__ = True

        if self:
            ## Add changeset metadata
            self.add((self.identifier, RDF.type, CS.ChangeSet))
            self.add((self.identifier, CS.createdDate, Literal(datetime.utcnow().isoformat() + "Z")))
            self.add((self.identifier, DC.creator, self.agent.identifier))
            self += self.agent
            for name in self.agent.objects(self.agent.identifier, FOAF.name):
                self.add((self.identifier, CS.creatorName, name))
            if not self.exists((self.identifier, CS.creatorName, None)):
                for nick in self.agent.objects(self.agent.identifier, FOAF.nick):
                    self.add((self.identifier, CS.creatorName, nick))
            self.add((self.identifier, CS.changeReason, self.reason))
            self.add((self.identifier, ORDF.lens, URIRef("http://ordf.org/lens/changeset")))

            self.log.info("%d changes %s" % (self.changes, self.identifier))
            for s,p,o in self.triples((self.identifier, CS.precedingChangeSet, None)):
                self.log.info("%s follows %s" % (self.identifier, o))

    def rollback(self):
        """
        Empty the changeset. Fails if :meth:commit has already been called.
        """
        if self.__frozen__:
            raise Exception("%s already frozen" % self.identifier)
        self.remove((None, None, None))
        self.changes = 0

    def reify(self, op, (s,p,o,c)):
        add = BNode()
        self.add((self.identifier, op, add))
        self.add((add, RDF.type, RDF.Statement))
        self.add((add, RDF.subject, s))
        self.add((add, RDF.predicate, p))
        self.add((add, RDF.object, o))
        self.add((add, ORDF.graph, c))
        
    def disembody(self, node):
        d = {}
        for s,p,o in self.triples((node, None, None)):
            d[p] = o
        return (d[RDF.subject], d[RDF.predicate], d[RDF.object]), d[ORDF.graph]

    def __cached__(self, attr, predicate):
        if not hasattr(self, attr):
            result = None
            for s,p,o in self.triples((self.identifier, predicate, None)):
                result = o.toPython()
            if result:
                setattr(self, attr, result)
        else:
            result = getattr(self, attr)
        return result
    @property
    def createdDate(self):
        return self.__cached__("__createdDate__", CS.createdDate)

    @property
    def metadata(self):
        m = Graph(identifier=self.identifier)
        bind_ns(m)
        add = 0
        rem = 0
        for s,p,o in self.triples((self.identifier, None, None)):
            if p == CS.addition: add += 1
            elif p == CS.removal: rem += 1
            else: m.add((s,p,o))
        m.add((self.identifier, CS.additionCount, Literal(add)))
        m.add((self.identifier, CS.removalCount, Literal(rem)))
        return m

    def __nonzero__(self):
        nz = False
        ## check for additions, other than changeset housekeeping
        for s,p,o in self.triples((self.identifier, CS.addition, None)):
            (ss, pp, oo), context = self.disembody(o)
            if pp == ORDF.changeSet and oo == self.identifier: ## always add our own ident
                continue
            nz = True
            break
        if not nz:
            ## check for removals, other than changeset housekeeping
            for s,p,o in self.triples((self.identifier, CS.removal, None)):
                (ss, pp, oo), context = self.disembody(o)
                if pp == ORDF.changeSet: ## always remove previous changesets
                    continue
                nz = True
                break
        ## cache the result if we have been committed
        if self.__frozen__:
            self.__nonzero__ = lambda: nz
        return nz

    def _changes(self, graph):
        add, rem = 0, 0
        for s,p,o in self.triples((self.identifier, CS.removal, None)):
            statement, g = self.disembody(o)
            if g == graph.identifier:
                rem += 1
                yield statement, CS.removal
        for s,p,o in self.triples((self.identifier, CS.addition, None)):
            statement, g = self.disembody(o)
            if g == graph.identifier:
                add += 1
                yield statement, CS.addition
        self.log.debug("changes for %s: +%s/-%s" % (graph.identifier, add, rem))

    def apply(self, graph):
        """
        Apply the changeset to a graph
        """
        for (s, p, o), op in self._changes(graph):
            if op == CS.removal:
                graph.remove((s,p,o))
            else:
                graph.add((s,p,o))

    def undo(self, orig):
        """
        Undo the changes in the changeset on a graph.
        """
        for (s, p, o), op in self._changes(orig):
            if op == CS.removal:
                orig.add((s,p,o))
            else:
                orig.remove((s,p,o))
