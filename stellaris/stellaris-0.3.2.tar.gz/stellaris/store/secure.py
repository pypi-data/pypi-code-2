# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os

from benri.app import WSGICollection, json
from benri.threadstage import EventHandler, ThreadStageOrderedEvent
from benri.db import DB, Index
#from benri.security import AuthorizationService

from stellaris.store import LifetimeStore as Store
from stellaris.store.exceptions import Unauthorized
from stellaris.exceptions import ConfigAttributeMissing

log = logging.getLogger('stellaris')

WRITE = 0
READ = 1

SYSTEM_USER = 'system'

# TODO: why cant the attributes of the instance be addressed directly, but
#       has to go over the strange _SecureStore prefix
def authorize(rights=WRITE):
    def wrap(f):
        def check_user(self, *args, **kwargs):
            # graph id must be the second variable, first is the graph
            graph = args[0]
            
            # default user is public, if no user is given
            try:
                user = kwargs['user']
            except KeyError, e:
                user = 'public'

            valid_user = False
            graph_acl = True
            try:
                acl = dict(self._SecureStore__acls[graph.name])
                
                if user in acl and acl[user] == rights:
                    valid_user = True

            except KeyError, e:
                # dont like nested exceptions, do this instead
                graph_acl = False
                
            if graph_acl == False:
                # no acl for the graph, try if the collection has an ACL
                try:
                    # / in the end of collection_id?
                    collection_id = os.path.dirname(graph.name)
                    acl = dict(self._SecureStore__acls[collection_id])
                
                    if user in acl and acl[user] == rights:
                        valid_user = True
                except KeyError, e:
                    # no ACL assigned to graph nor collection, that means 
                    # only project members can write, but everyone can read 
                    # the graph
                    if rights == WRITE:
                        # TODO: check if the user is registered with the
                        # security service
                        valid_user = True
                    else:
                        valid_user = True
        
            if not valid_user:
                raise Unauthorized('User %s is not allowed to access the graph: %s' % (user, graph.name))

            # remove the keyword argument user since it is not part of the
            # lower level interface
            del kwargs['user']
            return f(self, *args, **kwargs)
        
        check_user.__doc__ = f.__doc__
        return check_user
    return wrap

# TODO: bulk method with a list of graphs as input and a list of graphs which
#       the user is allowed to read as output. This is necessary in order
#       to enable security for queries.
class SecureStore(Store):

    def __init__(self, config):
        try:
            self.__db = config['internal']['db_instance']
        except KeyError, e:
            raise ConfigAttributeMissing('internal', 'db_instance')
            
        # persistent mapping from graph -> ACL
        self.__acls = Index('acl.db', self.__db)
        Store.__init__(self, config)
    
    def is_authorized(self, graph_name, user=None, rights=WRITE):
        # default user is public, if no user is given
        if user == None:
            user = 'public'
        # the system user can do whatever
        elif user == SYSTEM_USER:
            return True
            
        valid_user = False
        graph_acl = True
        try:
            acl = dict(self.__acls[graph_name])
            
            if user in acl and acl[user] == rights:
                valid_user = True

        except KeyError, e:
            # dont like nested exceptions, do this instead
            graph_acl = False
            
        if graph_acl == False:
            # no acl for the graph, try if the collection has an ACL
            try:
                # / in the end of collection_id?
                collection_id = os.path.dirname(graph_name)
                acl = dict(self.__acls[collection_id])
            
                if user in acl and acl[user] == rights:
                    valid_user = True
            except KeyError, e:
                # no ACL assigned to graph nor collection, that means 
                # only project members can write, but everyone can read 
                # the graph
                if rights == WRITE:
                    # TODO: check if the user is registered with the
                    # security service
                    valid_user = True
                else:
                    valid_user = True
    
        return valid_user
            
    def close(self):
        self.__acls.close()
        Store.close(self)

    def create_graph(self, graph, user=None):
        print "creating new graph: ", graph
        
        if self.is_authorized(graph.name, user=user, rights=WRITE):
            return Store.create_graph(self, graph)
        
        raise Unauthorized('User %s is not allowed to create graph %s' % (user, graph.name))

    def retrieve_graph(self, name, user=None):
        if self.is_authorized(name, user=user, rights=READ):
            return Store.retrieve_graph(self, name)
        
        raise Unauthorized('User %s is not allowed to read graph %s' % (user, name))


    def replace_graph(self, name, graph, user=None):
        if self.is_authorized(name, user=user, rights=WRITE):
            return Store.replace_graph(self, name, graph)
        
        raise Unauthorized('User %s is not allowed to modify graph %s' % (user, name))

    def update_graph(self, name, graph, user=None):
        if self.is_authorized(name, user=user, rights=WRITE):
            return Store.update_graph(self, name, graph)
        
        raise Unauthorized('User %s is not allowed to modify graph %s' % (user, name))

    def append_graph(self, name, graph, user=None):
        if self.is_authorized(name, user=user, rights=WRITE):
            return Store.append_graph(self, name, graph)
        
        raise Unauthorized('User %s is not allowed to modify graph %s' % (user, name))

    def remove_graph(self, name, graph, user=None):
        if self.is_authorized(name, user=user, rights=WRITE):
            return Store.remove_graph(self, name, graph)
        
        raise Unauthorized('User %s is not allowed to modify graph %s' % (user, name))

    def delete_graph(self, name, user=None):
        if not self.is_authorized(name, user=user, rights=WRITE):
            raise Unauthorized('User %s is not allowed to modify graph %s' % (user, name))        
    
        # remove the acl from local db
        try:
            del self.__acls[name]
        except KeyError, e:
            # there was no acl assigned to the graph
            pass
            
        # call the store to delete the graph    
        return Store.delete_graph(self, name)

    def graph_exists(self, name, prefix_lookup=False, user=None):
        if self.is_authorized(name, user=user, rights=READ):
            return Store.graph_exists(self, name, prefix_lookup=prefix_lookup)
        
        raise Unauthorized('User %s is not allowed to lookup graph %s' % (user, name))
        
    def assign_ttl(self, name, ttl, user=None):
        if self.is_authorized(name, user=user, rights=WRITE):
            return Store.assign_ttl(self, name, ttl, user=user)
        
        raise Unauthorized('User %s is not allowed to set the TTL for graph %s' % (user, name))

    def remove_ttl(self, graph, user=None):
        if self.is_authorized(graph.name, user=user, rights=WRITE):
            return Store.remove_ttl(self, graph, user=user)
        
        raise Unauthorized('User %s is not allowed to remove the TTL for graph %s' % (user, graph.name))
        
    def associate_acl(self, graph_name, acl, user=None):
        """
        Associates an ACL with a graph.
        
        ``acl`` - A list of (user, rights)-tuples
        ``graph`` - associate the ACL with this graph
        """
        if not self.is_authorized(graph_name, user=user, rights=WRITE):
            raise Unauthorized('User %s is not allowed to change the ACL for graph %s' % (user, graph.name))

        # if acl is == [], delete the graph_id
        if acl == []:
            try:
                del self.__acls[graph_name]
                return
            except KeyError, e:
                # means the graph id didnt exist which is ok
                pass
                
        try:
            # overwrites any existing acl
            self.__acls[graph_name] = acl
        except Exception, e:
            raise
