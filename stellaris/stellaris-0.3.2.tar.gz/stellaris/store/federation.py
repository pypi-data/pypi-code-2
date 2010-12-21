# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

#from stellaris.store.store import Store

class FederationRedirect(Exception): pass

class FederationStore(object):

    def __init__(self, config):
        # extract the hayai service url from config
        pass
        #Store.__init__(self, config)

    def create_graph(self, graph_data, graph_id, format='xml', ttl=None, user=None):
        # try to create the graph in the global namespace, 
        # if that fails, the graph is already at some other node, then raise
        # FederationRedirect with the graph location
        pass
        #Store.create_graph(self, graph_data, graph_id, format=format, ttl=ttl, user=user)        
