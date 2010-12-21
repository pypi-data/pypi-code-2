# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

from __future__ import with_statement

import logging, os, time, sys

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.orm import sessionmaker

from stellaris.store import Store
from stellaris.graph import Graph
from stellaris.security import AUTHENTICATED_USER, PUBLIC_USER, ADMIN_GROUP, AUTHENTICATED_GROUP, PUBLIC_GROUP, READ, READ_WRITE
from stellaris.dbmodels import create_db_models, Graph as DBGraph, GraphData as DBGraphData, Collection as DBCollection, User as DBUser, Group as DBGroup, AccessRights as DBAccessRights

from stellaris.exceptions import ConfigAttributeMissing
from stellaris.store.exceptions import CollectionAlreadyExists, CollectionNotFound, GraphAlreadyExists, GraphNotFound, GroupAlreadyExists, GroupNotFound, Unauthorized

class RDBMSStore(Store):

    # db_uri = None, 
    def __init__(self, db_uri, admin_user=ADMIN_GROUP, gc_interval=3600, backup_interval=86400, backup_path=None, log=None):
            
        self.log = log
        
        if self.log:
            self.log.debug('Creating database engine with uri: %s' % db_uri)
                        
        self.__engine = create_engine(db_uri)
        
        # create the graph models using the engine, if they already exists,
        # this is ignored.
        create_db_models(self.__engine)
                
        self.__Session = sessionmaker(bind=self.__engine, autocommit=True) #, autoflush=False, transactional=False)
        
        # create the root-collection
        self._create_default_groups(admin_user=admin_user)        
        self._create_collection('/', AUTHENTICATED_USER)
        
        Store.__init__(self, gc_interval=gc_interval, backup_interval=backup_interval, backup_path=backup_path, log=log)

    def _create_default_groups(self, admin_user=ADMIN_GROUP):
        # create a default group for public and authenticated access
        # these two groups are the initial groups for any collection
        # The admin group has a user with the name of the admin group or a pre-
        # defined user via the configuration.

        # create the public group
        try:
            self.group_create(PUBLIC_GROUP, users=[PUBLIC_USER])
        except GroupAlreadyExists,e:
            pass
        
        # create the authenticated group        
        try:
            self.group_create(AUTHENTICATED_GROUP, users=[AUTHENTICATED_USER])
        except GroupAlreadyExists,e:
            pass

        # create the admin group        
        try:
            self.group_create(ADMIN_GROUP, users=[admin_user])
        except GroupAlreadyExists,e:
            pass
        
    def _create_collection(self, name, user):
        """
        Creates a new collection from the given name with the user as owner.
        If the collection already exists, ``CollectionAlreadyExists`` is raised.
        
        ``name`` - name of the collection, starts and ends with '/'
        ``user`` - The owner of a newly created collection. If the user does
                   not exist it is also created.
        """
        session = self.__Session()

        # get all possible parent collections in reverse order
        # e.g. ['/a/b/c/', '/a/b/', '/a/', '/']
        
        name_spl = name.split('/')
        parents = ['/'.join(name_spl[:i]) + '/' for i in range(-1,-len(name_spl),-1)]

        # default owner to authenticated user
        try:
            if not user:
                user = AUTHENTICATED_USER

            db_user = session.query(DBUser).filter(DBUser.name==user).one()
        except InvalidRequestError, e:
            # user doesnt exist so it gets created
            db_user = DBUser(user)
            session.add(db_user)
            session.flush()

        exists = False

        collection = None
        cols = []
        for col in parents:
            # check if the collection exists
            try:
                collection = session.query(DBCollection).filter(DBCollection.name==col).one()
                # stop the iteration
                break
            except InvalidRequestError, e:
                # collection doesnt exist, save it on the list
                cols.append(col)
            except Exception, e:
                if self.log:
                    self.log.error('Failed to retrieve collection: %s' % str(e))
                raise

        # create the collections starting with the shortest prefix
        prev_coll = collection
        cols.reverse()

        pub_group = session.query(DBGroup).filter(DBGroup.name==PUBLIC_GROUP).one()
        auth_group = session.query(DBGroup).filter(DBGroup.name==AUTHENTICATED_GROUP).one()

        for col in cols:
            coll = DBCollection(col)
            coll.owner = db_user.user_id
            if prev_coll:
                coll.parent = prev_coll.collection_id

            # create default groups    
            coll.access_rights.append(DBAccessRights(pub_group, READ))
            coll.access_rights.append(DBAccessRights(auth_group, READ_WRITE))

            try:                
                session.add(coll)
                session.flush()
            except Exception, e:
                if self.log:
                    self.log.error('Failed to create collection: %s, error: %s' % (str(col), str(e)))
                raise

            prev_coll = coll                
                            
        session.close()

    def _collection_name(self, graph_name):        
        col_name = os.path.dirname(graph_name)
        if not col_name.endswith('/'):
            col_name += '/'

        return col_name
                
    def create(self, graph, user=None):
        
        try:
            self.exists(graph.name)
            raise GraphAlreadyExists(graph.name)
        except GraphNotFound, e:
            # if the graph does not exists, just continue
            pass
        
        session = self.__Session()
        
        db_graph = DBGraph(graph.name, graph.uri, ttl=graph.ttl)
        
        serialized = graph.serialized
        db_graph_data = DBGraphData(serialized, graph.version)
        db_graph.graphs.append(db_graph_data)
        
        self._create_collection(graph.name, user)
        
        with session.begin():
            # get collection so the graph can be added to its list
            col_name = self._collection_name(graph.name)
            collection = session.query(DBCollection)\
                                .filter(DBCollection.name == col_name).one()
            collection.graphs.append(db_graph)
            try:
                session.add(db_graph)
                session.add(db_graph_data)
            except Exception, e:
                if self.log:
                    self.log.error('Failed when creating new graph: %s, error:' % (graph.name, str(e)))
                raise
            
        session.close()
        
    def open(self):
        Store.open(self)

    def retrieve(self, name, version=None, cached_version=-1):
        """
        Returns a single graph with the given name and version.
        """
        session = self.__Session()

        with session.begin():
            try:
                db_g = session.query(DBGraph).filter(DBGraph.name==name).one()
                # get the latest version
                data = ''
                if version == None:
                    db_g_data = db_g.graphs[-1]
                    if cached_version == db_g_data.version:
                        # avoid passing around data by returning an empty graph
                        data = ''
                    else:
                        data = str(db_g_data.data)
                else:
                    db_g_data = session.query(DBGraphData)\
                                       .filter(and_(DBGraphData.version==version,\
                                        DBGraphData.graph==db_g.graph_id)).one()
                    data = str(db_g_data.data)
                
                # convert to string before storing into the graph, otherwise
                # the data gets corrupted and cannot be parsed
                g = Graph(db_g.name, data, uri=db_g.uri, ttl=db_g.ttl, version=db_g_data.version)
            except InvalidRequestError, e:
                raise GraphNotFound(name)
            except Exception, e:
                raise

        session.close()
        g.prepare_transfer()
        return g

    def update(self, graph):
        session = self.__Session()
        
        with session.begin():
            try:
                db_g = session.query(DBGraph).filter(DBGraph.name==graph.name).one()
            except Exception, e:
                raise GraphNotFound(graph.name)

            # update to the graph data when the newest persistent version
            # is older then the graph
            if db_g.graphs[-1].version < graph.version:
                db_g_data = DBGraphData(graph.serialized, graph.version)
                
                # TODO: it is extremely inefficient to store old versions
                # re-implement this to only store deltas, until then
                # no old versions are kept.
                del db_g.graphs[-1]
                db_g.graphs.append(db_g_data)
                session.add(db_g_data)
                
            # update the ttl
            if db_g.ttl != graph.ttl:
                db_g.ttl = graph.ttl
            
            #session.save(db_g)
        
        session.close()

    def _delete_collection(self, name):        
        """
        Deletes a collection if it does not contain any sub-collections or
        graphs.
        """

        # dont delete the root collection
        if name == '/':
            return
        
        name_spl = name.split('/')
        # -len(name_spl)+1 makes sure that we skip the '/'
        parents = ['/'.join(name_spl[:i]) + '/' for i in range(-1,-len(name_spl)+1,-1)]

        session = self.__Session()

        with session.begin():
            for col in parents:
                try:
                    db_c = session.query(DBCollection).filter(DBCollection.name==col).one()
                except Exception, e:
                    # collection doesnt exist, cant delete it
                    return

                # find all collections which has the current collection as
                # parent, and make sure there are no sub-graphs                    
                if not len(db_c.graphs) and not len(session.query(DBCollection).filter(DBCollection.parent == db_c.collection_id).all()):
                    session.delete(db_c)
                    session.flush()
                # dont need to check more parents since they will for sure have
                # sub-collections
                else:
                    break

        session.close()
            
    def delete(self, name):
        session = self.__Session()
        
        with session.begin():
            try:
                db_g = session.query(DBGraph).filter(DBGraph.name==name).one()
            except Exception, e:
                raise GraphNotFound(name)

            session.delete(db_g)
                
        session.close()
    
        self._delete_collection(self._collection_name(name))

    def collection_exists(self, name):
        """
        Returns ``True`` if the collection exists. Otherwise CollectionNotFound
        is raised.
        
        ``name`` - the name of the collection
        """
        
        if not name.endswith('/'):
            return False
        
        session = self.__Session()
    
        exists = False
      
        with session.begin():
            try:
                collection = session.query(DBCollection)\
                                    .filter(DBCollection.name==name).one()
                exists = True
            except InvalidRequestError, e:
                # collection doesnt exist
                pass
        session.close()
        
        if not exists:
            raise CollectionNotFound(name)
            
        return exists

    def retrieve_graphs(self, name, depth=1):
        """
        Returns a list of graphs as available in the collection and recursively
        in any sub-collection to the given depth.
                
        ``name`` - the name of the collection
        ``depth`` - Recursive depth, defaults to one which means the current
                    collection.
        """
        
    def collection_retrieve(self, name):
        """
        Returns a list of graphs as available in the collection and any 
        sub-collections as a (sub-collections, graphs)-tuple. 
                
        ``name`` - the name of the collection
        """
        
        if not name.endswith('/'):
            return ([],[])
            
        # find the collection
        # find all graphs that has the collection as backref
        # find all collections that has the collection as parent
        session = self.__Session()
        
        sub_collections = []
        graphs = []
         
        with session.begin():
            try:
                col = session.query(DBCollection)\
                                    .filter(DBCollection.name == name).one()
                graphs = [g.name for g in col.graphs]
                sub_collections = [c.name for c in session.query(DBCollection)\
                                        .filter(DBCollection.parent == col.collection_id)]
            except InvalidRequestError, e:
                pass

        return (sub_collections, graphs)

    def exists(self, name, prefix_lookup=False):
        """
        Check if the graph with the given name exists. If prefix_lookup is
        ``True``, each prefix in the hierarchy of the name is checked for
        existence. Returns the prefix if any is found, otherwise a
        ``GraphNotFound``-exception is thrown.
        
        Note: Even if this returns the prefix, there may be another thread in 
              the system that removes the graph before it has a chance to be 
              retrieved.
              
        ``name`` - the (hierarchical) name of the graph
        ``prefix_lookup`` - indicates if an hierarchical prefix search should be
                            performed. Default is ``False``.
        """

        session = self.__Session()

        if not prefix_lookup:
            with session.begin():
                try:
                    db_g = session.query(DBGraph).filter(DBGraph.name==name).one()
                except Exception, e:
                    raise GraphNotFound(name)
                
            session.close()
            return name
                        
        name_spl = name.split('/')

        names = [name] + ['/'.join(name_spl[:i]) for i in range(-1,-len(name_spl)+1,-1)]

        for n in names:
            try:
                with session.begin():
                    db_g = session.query(DBGraph).filter(DBGraph.name==n).one()
                
                return n
            except:
                pass        
       
        session.close()
        
        raise GraphNotFound(name)

    # -------- Group management methods goes in here for now, break out later
    
    def group_list(self):
        """
        Returns a dictionary with all groups in the system. The key is the
        group name and the value is a list of user-names.
        """
        session = self.__Session()
        
        results = {}
                
        with session.begin():
            # does the groups associated with the collection contain the user?            
            results = dict([(group.name, [user.name for user in group.users]) for group in session.query(DBGroup)])
            
        session.close()
        return results
             
    def group_create(self, name, users=[]):
        """
        Creates a group with an initial set of users.
        
        ``name`` - group name
        ``users`` - list of strings representing the users
        """
        session = self.__Session()

        with session.begin():
            try:
                session.query(DBGroup).filter(DBGroup.name==name).one()
                exists = True
            except Exception, e:
                exists = False

            if exists:
                raise GroupAlreadyExists(name)

            # create any user that doesnt exist from the list
            db_users = []
            for user in users:
                try:
                    db_user = session.query(DBUser).filter(DBUser.name==user).one()
                except InvalidRequestError, e:
                    # user doesnt exist so it gets created
                    db_user = DBUser(user)
                    session.add(db_user)
                    session.flush()

                db_users.append(db_user)

            db_g = DBGroup(name)
            db_g.users = db_users

            session.add(db_g)

        session.close()

    def group_retrieve(self, name):
        """
        Returns the list of user names that are in the group.
        """
        session = self.__Session()

        users = []
        
        with session.begin():
            try:
                db_g = session.query(DBGroup).filter(DBGroup.name==name).one()
            except Exception, e:
                raise GroupNotFound(name)
        
            for user in db_g.users:
                users.append(user.name)

        session.close()
        return users                

    def group_update(self, name, users=[]):
        """
        Replaces the current list of users with the given list.
        """
        session = self.__Session()

        with session.begin():
            try:
                db_g = session.query(DBGroup).filter(DBGroup.name==name).one()
            except Exception, e:
                raise GroupNotFound(name)

            # create any user that doesnt exist from the list
            db_users = []
            for user in users:
                try:
                    db_user = session.query(DBUser).filter(DBUser.name==user).one()
                except InvalidRequestError, e:
                    # user doesnt exist so it gets created
                    db_user = DBUser(user)
                    session.add(db_user)
                    session.flush()
                    
                db_users.append(db_user)    

            db_g.users = db_users

        session.close()

    def group_delete(self, name):
        """
        Deletes a group.
        """
        session = self.__Session()

        with session.begin():
            try:
                db_g = session.query(DBGroup).filter(DBGroup.name==name).one()
            except Exception, e:
                raise GroupNotFound(name)
            
            session.delete(db_g)

        session.close()
    
    def group_add_to_collection(self, collection_name, group_name, access_rights=READ):
        """
        Associates the group with the collection. All users in the group are
        then allowed the given access_rights. Defaults to read.
        
        ``collection_name`` - name of the collection
        ``group_name`` - name of the group
        ``access_rights`` - either READ or READ_WRITE from 
                            ``stellaris.security``
        """
        session = self.__Session()
        
        with session.begin():
            # check if the group exists
            try:
                db_g = session.query(DBGroup).filter(DBGroup.name==group_name).one()
            except Exception, e:
                raise GroupNotFound(group_name)
        
            # check for the collection
            try:
                db_c = session.query(DBCollection)\
                              .filter(DBCollection.name==collection_name).one()
            except Exception, e:
                raise CollectionNotFound(collection_name)

            new_rights = DBAccessRights(db_g, access_rights)            
            # is the group in the collection already?
            # then dont do anything
            if not new_rights in db_c.access_rights:
                db_c.access_rights.append(new_rights)

        session.close()

    def group_remove_from_collection(self, collection_name, group_name):
        """
        Removes a group from the collection.
        
        ``collection_name`` - name of the collection
        ``group_name`` - name of the group        
        """
        session = self.__Session()
        
        with session.begin():
            # check if the group exists
            try:
                db_rights = session.query(DBAccessRights)\
                            .join('collection')\
                            .filter(DBCollection.name == collection_name)\
                            .join('group')\
                            .filter(DBGroup.name == group_name).one()
            except Exception, e:
                raise GroupNotFound(group_name)
        
            # check for the collection
            try:
                db_c = session.query(DBCollection)\
                              .filter(DBCollection.name==collection_name).one()
            except Exception, e:
                raise CollectionNotFound(collection_name)
            
            db_c.access_rights.remove(db_rights)

        session.close()

    def is_admin(self, user):
        """
        Returns ``True`` if the user is part of the group %s.
        """ % (ADMIN_GROUP)
        
        session = self.__Session()
        is_part = False
        
        with session.begin():
            try:
                db_user = session.query(DBUser).filter(DBUser.name == user).one()
                session.query(DBGroup).filter(DBGroup.users.contains(db_user)).one()
                is_part = True                
            except InvalidRequestError, e:
                pass
        
        return is_part
                                                
    def is_authorized(self, name, user, access_type=READ):
        """
        Checks if the user is allowed to access the graph with the 
        give access_type. Basically, it checks if the user is part of any group
        that is associated with the graph's collection. Raises ``Unauthorized``
        if the user is not allowed access.
        
        ``name`` - name of the graph
        ``user`` - name of the user
        ``access_type`` - Either READ or READ_WRITE from ``stellaris.security``
        """
        collection_name = self._collection_name(name)

        try:
            self.collection_exists(collection_name)
        # anyone is allowed access to a non-existent collection, this could
        # for example be when a new graph is being created in a collection
        # which not yet exists
        except CollectionNotFound, e:
            return True
                    
        session = self.__Session()
        
        authorized = False
        
        with session.begin():
            # TODO: are only registered users seen as authenticated?
            
            # is the user the owner of the collection
            try:
                db_user = session.query(DBUser).filter(DBUser.name == user).one()
                tmp = session.query(DBCollection)\
                       .filter(and_(DBCollection.name == collection_name, DBCollection.owner == db_user.user_id)).one()
                authorized = True
            except Exception, e:
                pass

            # check if the collection has the default groups public and authenticated
            # the non-public user is in the authenticated group by default

            if not authorized:
                pub_group = session.query(DBGroup).filter(DBGroup.name==PUBLIC_GROUP).one()
                auth_group = session.query(DBGroup).filter(DBGroup.name==AUTHENTICATED_GROUP).one()

                def _allowed_write(group):            
                    try:
                        q = session.query(DBCollection).join(['access_rights', 'group'])
                        q = q.filter(DBCollection.name == collection_name)
                        q = q.filter(DBAccessRights.group == group)
                        q = q.filter(DBAccessRights.rights == READ_WRITE)
                        q = q.one()
                        return True
                    except InvalidRequestError, e:
                        return False

                def _allowed_read(group):            
                    try:
                        q = session.query(DBCollection).join(['access_rights', 'group'])
                        q = q.filter(DBCollection.name == collection_name)
                        q = q.filter(and_(DBAccessRights.group == group, \
                                          DBAccessRights.rights == READ))
                        q = q.one()
                        return True
                    except InvalidRequestError, e:
                        return False 

                # public access for both read and write makes any user 
                # authorized
                if access_type == READ:
                    # pub group can read => any-one can read                
                    if _allowed_read(pub_group):   
                        authorized = True
                    # is the auth group allowed to read (user must be auth.)
                    elif user != PUBLIC_USER and _allowed_read(auth_group):
                        authorized = True
                    
                    # otherwise neither group was allowed read access for the 
                    # collection                
                elif access_type == READ_WRITE:
                    if _allowed_write(pub_group):
                    # pub group was not allowed write, check if auth_group
                    # is allowed to write, otherwise check special group
                        authorized = True
                    elif user != PUBLIC_USER and _allowed_write(auth_group):
                        authorized = True
            
            # check if the user is in any of the groups associated with the 
            # collection            
            if not authorized:    
                # does the groups associated with the collection contain the user?
                try:
                    q = session.query(DBCollection).join(['access_rights', 'group', 'users'])
                    
                    if access_type == READ_WRITE:
                        q = q.filter(and_(and_(DBAccessRights.rights == access_type,\
                                              DBCollection.name == collection_name),\
                                              DBUser.name == user)).one()
                    elif access_type == READ:
                        q = q.filter(and_(and_(or_(DBAccessRights.rights == READ,\
                                                   DBAccessRights.rights == READ_WRITE),\
                                              DBCollection.name == collection_name),\
                                              DBUser.name == user)).one()
                        
                    authorized = True
                except Exception, e:
                    pass

        session.close()

        if not authorized:
            raise Unauthorized('User %s is not allowed access to the collection %s.' % (user, collection_name))
            
        return authorized
    
    def garbage_collection(self):
        """
        Runs a garbage collection routine for the store. This includes removal
        of expired graphs etc. .
        """

        # Note: since this is running via a separate thread, it does not
        # know about the db when using an in-memory db (eg. sqlite:///:memory:)
        # This limits the usage of this store to only non in-memory dbs.
        
        remove_graphs = []
        
        session = self.__Session()
        current_time = time.time()

        with session.begin():
            for g in session.query(DBGraph).filter(DBGraph.ttl < current_time):
                remove_graphs.append(g.name)
        
        session.close()
        
        for g_name in remove_graphs:
            self.delete(g_name)
            
    def close(self):
        """
        Closes the store.
        """
        Store.close(self)

