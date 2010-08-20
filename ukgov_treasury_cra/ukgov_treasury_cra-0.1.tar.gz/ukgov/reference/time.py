"""
Calendar values and time specifications
=======================================

.. autoclass:: Year
    :show-inheritance:
.. autoclass:: _Year
    :show-inheritance:
.. autoclass:: GovYear
    :show-inheritance:
"""

from ordf.namespace import register_ns, Namespace
register_ns("year", Namespace("http://reference.data.gov.uk/id/year/"))
register_ns("govyear", Namespace("http://reference.data.gov.uk/id/government-year/"))
register_ns("interval", Namespace("http://reference.data.gov.uk/def/intervals/"))

from ordf.vocab.owl import Class, Individual
from ordf.graph import Graph
from ordf.namespace import YEAR, GOVYEAR, INTERVAL, TIME, RDF, RDFS
from telescope import Select, v

class Year(Class):
    """
    This is an OWL Factory class. See the documentation for 
    :class:`ordf.vocab.owl.Class` for more information on precisely what
    this means.

    This particular factory class has a :meth:get method that will
    fetch year data from the UK government namespace and return an
    instance of the concrete indivudual :class:`_Year`.
    
    >>> factory = Year(load=True)
    >>> year2000 = factory.get("2000")
    >>> print year2000.start, year2000.end
    2000-01-01 00:00:00 2001-01-01 00:00:00
    >>>

    :param graph:
        The graph that the OWL specification of the class is to live
        in, and the default graph for individuals created with the
        :meth:`get` method.
    :parm load:
        If True, the get method will fetch a year specification from
        the Internet if it doesn't already exist in the local graph
        or in the cache.
    """
    _cache = {}
    _namespace = YEAR
    def __init__(self, graph=None, load=False):
        super(Year, self).__init__(
            INTERVAL.Year,
            graph=graph)
        self._load = load
    def get(self, yearSpec, graph=None):
        """
        Return a :class:`_Year` individual in the given graph which
        defaults to the graph of the factory class.
        """
        year = self._cache.get(yearSpec)
        if year is None:
            if graph is None: graph=self.graph
            year = _Year(identifier=self._namespace[yearSpec], graph=graph)
            year.factoryGraph = graph
            if self._load:
                year.type = TIME.Interval

                yearDef = Graph().parse(self._namespace[yearSpec])

                s, p, o = yearDef.one((year.identifier, TIME.hasBeginning, None))
                year.graph.add((s,p,o))
                year.graph.add((o, RDF.type, TIME.Instant))
                yearStart = Graph(identifier=o).parse(o)
                start = yearStart.one((yearStart.identifier, TIME.inXSDDateTime, None))
                year.graph.add(start)

                s, p, o = yearDef.one((year.identifier, TIME.hasEnd, None))
                year.graph.add((s,p,o))
                year.graph.add((o, RDF.type, TIME.Instant))
                yearEnd = Graph(identifier=o).parse(o)
                end = yearEnd.one((yearEnd.identifier, TIME.inXSDDateTime, None))
                year.graph.add(end)

            self._cache[yearSpec] = year
        return year
            
class GovYear(Year):
    """
    Same as with :class:`Year` except for the fiscal year, starting on the
    first of April.

    >>> factory = GovYear(load=True)
    >>> year2000 = factory.get("2000-2001")
    >>> print year2000.start, year2000.end
    2000-04-01 00:00:00 2001-04-01 00:00:00
    >>>
    """
    _cache = {}
    _namespace = GOVYEAR

class _Year(Individual):
    """
    An individual representing a year.

    :attribute start: 
        an instance of :class:`datetime.datetime` for the start of the year
        
    :attribute end: 
        an instance of :class:`datetime.datetime` for the end of the year.
    
    """
    @property
    def start(self):
        if hasattr(self, "_start"):
            return self._start
        q = Select([v.start], distinct=True).where(
            (self.identifier, TIME.hasBeginning, v.instant),
            (v.instant, TIME.inXSDDateTime, v.start)
            )
        for start in self.graph.query(q.compile()):
            self._start = start
            return start.toPython()
        
    @property
    def end(self):
        if hasattr(self, "_end"):
            return self._end
        q = Select([v.end], distinct=True).where(
            (self.identifier, TIME.hasEnd, v.instant),
            (v.instant, TIME.inXSDDateTime, v.end)
            )
        for end in self.graph.query(q.compile()):
            self._end = end
            return end.toPython()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
