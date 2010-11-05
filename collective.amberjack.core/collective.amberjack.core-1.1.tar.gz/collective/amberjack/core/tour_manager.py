from collective.amberjack.core.interfaces import ITourDefinition
from collective.amberjack.core.interfaces import ITourRetriever
from collective.amberjack.core.interfaces import ITourManager
from zope.component import getUtilitiesFor
from zope.component import queryUtility
from zope.interface import implements


class PackagedTourRetriever(object):
    implements(ITourRetriever)

    def getTours(self, context=None):
        return [(name, tour)
                for name, tour in getUtilitiesFor(ITourDefinition)]
    def getTour(self, tour_id, context=None):
        return queryUtility(ITourDefinition, name=tour_id)

        
class TourManager(object):
    implements(ITourManager)
    
    def getTours(self, context):
        alltours = []
        for name, retriever in getUtilitiesFor(ITourRetriever):
            alltours.extend(retriever.getTours(context))
        return sorted(alltours)

    def getTour(self, tour_id, context=None):
        tour = None
        for name, retriever in getUtilitiesFor(ITourRetriever):
            tour = retriever.getTour(tour_id, context)
            if tour is not None:
                return tour
        return tour
