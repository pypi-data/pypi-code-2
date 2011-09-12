
def get_remote_resource(auto_origin=True):
    auto_origin=False
    if auto_origin:
        assert not origin, "Either origin or auto_origin, not both"
        origin_uri = hash_to_slash_uri(uri)
        origin, _origin_created = Origin.objects\
            .get_or_create(uri=origin_uri)



class ResourceManagerGetOrCreateAutoOrigin(): #unittest2.TestCase):
    """auto_origin will do a .GET() before continuing. can be slow
    """
    def test_manager_create_auto_origin(self):
        Origin.objects.reset_store()
        Resource.objects.reset_store()

#        uri = "http://renaud.delbru.fr/rdf/foaf#me"
#        renaud,_created = ldtools.Resource.objects.get_or_create(uri=uri,
#                                                         auto_origin=True)
#        renaud._origin.GET(**kw)
#        renaud._origin.__class__.objects.GET_all(**kw)

        uri = "http://example.org/resource#me"
        resource, created = Resource.objects.get_or_create(uri,
                                                           auto_origin=True)
        self.assert_(str(resource._origin.uri), uri.rstrip('#me'))
        self.assert_(len(Resource.objects.all()), 1)
        self.assert_(len(Resource.objects.all()), 1)





class ooo(object):
    def get_statistics(self):
        def triples_per_second(triples, time): # TODO make this more accurate
            total_seconds = (time.microseconds+(time.seconds+\
                                      time.days*24*3600)*10**6)//10**6
            return triples / total_seconds if total_seconds > 0 else None

        if hasattr(self, '_graph'):
            triples = len(self._graph)
            tps = triples_per_second(triples,
                                     self.stats['graph_processing_time'])
            if tps:
                logger.info(
                    "Crawled %s: '%s' triples in '%s' seconds --> '%s' "
                    "triples/second"
                    % (self.uri, triples,
                       self.stats['graph_processing_time'], tps))
            else:
                logger.info("Crawled %s in '%s' seconds"
                % (self.uri, self.stats['graph_processing_time']))
            pass
        else:
            print "no statistics recorded"
