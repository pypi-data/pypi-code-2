# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import sys

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text
from sqlalchemy.orm import mapper, backref, relation, clear_mappers

class ModelObject(object):
    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, ', '.join(["%s: %s" % (attr, getattr(self, attr)) for attr in dir(self) if not attr.startswith('_') and not attr == 'c' and not attr == 'parent']))

class Graph(ModelObject):
    def __init__(self, name, uri, ttl=None):
        self.ttl = ttl
        self.name = name
        self.uri = uri

class GraphData(ModelObject):
    def __init__(self, data, version):
        self.data = data # serialized RDF/XML
        self.version = version
        
class User(ModelObject):
    def __init__(self, name):
        """
        A member has a name and belongs to a set of groups.
        """
        self.name = name

class Group(ModelObject):
    def __init__(self, name):
        """
        A group has a name and a relation to users.
        """
        self.name = name

class AccessRights(ModelObject):
    def __init__(self, group, rights):
        self.group = group
        self.rights = rights
                    
class Collection(ModelObject):
    def __init__(self, name):
        self.name = name

def create_db_models(engine):
    metadata = MetaData()

    # clear all existing mappers
    clear_mappers()

    users_table = Table('users', metadata,
         Column('user_id', Integer, primary_key=True),    
         Column('name', String(512), index=True, nullable=False, unique=True))

    groups_table = Table('groups', metadata,
         Column('group_id', Integer, primary_key=True),
         Column('name', String(512), index=True, nullable=False, unique=True))

    group_user_relation = Table('groups_users', metadata,
        Column('group_id', Integer, ForeignKey('groups.group_id')),
        Column('user_id', Integer, ForeignKey('users.user_id')))

#    collection_access_table = Table('collection_access', metadata,
#         Column('id', Integer, primary_key=True),
#         Column('rights', Integer, nullable=False),
#         Column('group', Integer, ForeignKey('groups.id')))

    collections_table = Table('collections', metadata,
         Column('collection_id', Integer, primary_key=True),    
         Column('name', String(1024), index=True, nullable=False, unique=True),
         Column('owner', Integer, ForeignKey('users.user_id'), nullable=False),
         Column('parent', Integer, ForeignKey('collections.collection_id')))

    access_rights_relation = Table('access_rights', metadata,
        Column('group_id', Integer, ForeignKey('groups.group_id'), primary_key=True),
        Column('collection_id', Integer, ForeignKey('collections.collection_id'), primary_key=True),
        Column('rights', Integer, nullable=False))

    graphs_table = Table('graphs', metadata,
         Column('graph_id', Integer, primary_key=True),    
         Column('name', Text, nullable=False, unique=True),
         Column('uri', Text, nullable=False),         
         Column('ttl', Integer, nullable=True),
         Column('collection_id', Integer, ForeignKey('collections.collection_id')))

    graph_data_table = Table('graph_data', metadata,
        Column('graph_data_id', Integer, primary_key=True),
        Column('version', Integer, nullable=False),
        Column('graph', Integer, ForeignKey('graphs.graph_id')),
        Column('data', Text, nullable=False))
        
    metadata.create_all(engine)

    # a graph has many versions
    mapper(GraphData, graph_data_table)
    # the cascade option makes sure that all data in the graph_data_table is
    # removed when a graph is removed
    mapper(Graph, graphs_table, properties={
        'graphs':relation(GraphData, cascade="delete, delete-orphan")})

    mapper(User, users_table)
    mapper(Group, groups_table, properties={
        'users':relation(User, secondary=group_user_relation)})

    mapper(AccessRights, access_rights_relation, properties={
        'group': relation(Group, lazy=False)})
    
    #mapper(CollectionAccessRights, collection_access_table)        
    mapper(Collection, collections_table, properties={
        'access_rights': relation(AccessRights, backref='collection', cascade='all, delete-orphan'),
        'graphs': relation(Graph, backref='collection')})

if __name__ == '__main__':
    from sqlalchemy import create_engine, and_, or_
    from sqlalchemy.orm import sessionmaker
    # http://techspot.zzzeek.org/?p=13
    READ = 0
    WRITE = 1
    
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)

    create_db_models(engine)

    session = Session()
    
    graph1 = Graph('/test/g', 'uri1')
    graph2 = Graph('/test/g2', 'uri2')    
    
    user1 = User('public')
    user2 = User('authorized')
    
    session.save(user1)
    session.flush()
    
    group1 = Group('public')
#    group1.users.append(user1)
#    group1.users.append(user2)
    
    group2 = Group('auth')
#    group2.users.append(user1)
    
    session.save(group1)
    session.save(group2)
    session.flush()

    def group(name):
        return session.query(Group).filter_by(name=name).one()

    #print group('blub')
           
    collection = Collection('/test/')
    collection.owner = user1.user_id
    collection.access_rights.append(AccessRights(group('public'), READ))
    collection.access_rights.append(AccessRights(group('auth'), WRITE))

#    collection.groups.append(group1)
#    collection.groups.append(access_group2)    
#    collection.graphs.append(graph1)
#    collection.graphs.append(graph2)    

#    collection_child = Collection('/test/')
#    collection_child.owner = user2
#    collection.parent = collection

#    session.save(user1)
    session.save(collection)
    session.flush()
    
#    session.save(collection_child)
#
#    session.save(user2)
#    session.save(group1)
    
    session.commit()
    session.clear()

    q = session.query(Collection).join(['access_rights','group'], id='rights')
    q = q.filter(Collection.name == '/test/')
    q = q.filter(and_(AccessRights.group == group('public'), \
                      AccessRights.rights == WRITE))
#                    or_(AccessRights.rights == WRITE, \
#                        AccessRights.rights == READ)))
    q = q.add_entity(AccessRights, id='rights')
    
    print [(col.name, ar.rights, ar.group) for (col, ar) in q]

    q = session.query(Collection).join('access_rights')
    q = q.filter(Collection.name == '/test/')
    q = q.filter(and_(AccessRights.group == group1, \
                    or_(AccessRights.rights == WRITE, \
                        AccessRights.rights == READ)))
    
    print [col.name for col in q]
                        
#    cols = session.query(Collection).join('access_rights', id='ar')\
#                  .filter(Collection.name=='/test/')\
#                  .filter(or_(AccessRights.rights == WRITE, AccessRights.rights == READ))\
#                  .add_entity(AccessRights, id='ar')
    
#    print [(col.name, ar.group.name) for (col, ar) in cols]
    
#    col = session.query(Collection).filter_by(name='/test/').one()
#    print col
#    print [(access_right.group.name, access_right.rights) 
#           for access_right in col.access_rights]    
#    print [a.access_rights for a in session.query(Collection).filter(Collection.access_rights.contains(ar1)).filter(AccessRights.group_id == group1.group_id)]
    
#    print [a for a in session.query(Collection).join('access_rights')]
    
#    print [a for a in session.query(Collection).join(['access_rights', 'group', 'users']).filter(and_(and_(AccessRights.rights == READ, Collection.name == '/test/'), User.name == 'test1'))]
    
    # returns all collections which has a group containing the user and the 
    # given name of the collection
#    print [a for a in session.query(Collection).join(['groups', 'a']).filter(and_(Collection.name == '/test/', CollectionAccessRights.rights == WRITE)).filter(CollectionAccessRights.group == Group.id).filter(User.name == 'test1')]
    
#    print session.query(Collection).join(['groups', 'group', 'users']).filter(and_(Collection.name == '/test/', User.name == 'test2')).all()
                            #  .filter(Collection.groups.any(Group..all()
        
#    print session.query(User).filter(Collection.name=='/test/')\
#                             .filter(Collection.groups.users.any(User.name == 'test1')).all()
    
#    print graph1
#    print user1
#    print user2
#    print group1
#    print collection
