'''The Zarkov data model.'''
import bson

from datetime import datetime

from ming import Session, collection, Field
from ming import schema as S
from ming.orm import ThreadLocalORMSession

doc_session = Session.by_name('main')
orm_session = ThreadLocalORMSession(doc_session)

# Things we want to track -- the 'fact table' from an OLAP perspective
event = collection(
    'event', doc_session,
    Field('_id', S.ObjectId()),
    Field('timestamp', datetime, if_missing=datetime.utcnow, index=True),
    Field('type', str, index=True),
    Field('context', {str:str}),
    Field('extra', None),
    # Here we can 'lock' an event while it's being processed by an aggregation
    # job
    Field('jobs', [S.ObjectId()], index=True),
    # Here we note which aggregates in which the event already has been included
    # so we can do incremental aggregation
    Field('aggregates', [str], index=True))

# Aggregations defined over (by default) the 'event' collection
agg_def = collection(
    'agg_def', doc_session,
    Field('_id', S.ObjectId()),
    # Collection into which we store the aggregation
    Field('name', str),
    # Input collection to aggregate
    Field('object', str, if_missing='event'),
    # Javascript map function
    Field('map', str),
    # Javascript reduce function
    Field('reduce', str))

class Event(object): pass

class AggDef(object):

    @classmethod
    def simple_count(cls, collection_name, name, key_js):
        '''Build an AggDef that counts mapped events'''
        return cls(
            name=name,
            map='function(){emit(%s, 1)}' % key_js,
            reduce=cls.sum_js,
            object=collection_name)

    @property
    def collection(self):
        '''The aggregate (output) collection'''
        return doc_session.db[self.name]

    @property
    def object_collection(self):
        '''The object (input) collection'''
        return doc_session.db[self.object]

    def incremental(self, jobid=None):
        'Update the aggregate incrementally based on the component events'
        if jobid is None: jobid = bson.ObjectId()
        c_obj = self.object_collection
        # Mark the events to be agg'd
        c_obj.update(
            dict(aggregates={'$ne':self.name}),
            { '$push':dict(jobs=jobid, aggregates=self.name)},
            multi=True)
        try:
            # Perform the agg
            result = doc_session.db.command(
                'mapreduce', self.object,
                map=bson.Code(self.map),
                reduce=bson.Code(self.reduce),
                out=dict(reduce=self.name),
                query=dict(jobs=jobid))
        except:
            # Mark the agg as NOT done
            c_obj.update(
                dict(jobs=jobid),
                { '$pull': dict(jobs=jobid, aggregates=self.name) },
            multi=True)
            raise
        else:
            # Unmark the events
            c_obj.update(
                dict(jobs=jobid),
                { '$pull': dict(jobs=jobid) },
            multi=True)
        return result

    def full(self, jobid=None):
        'Clear the agg and recompute'
        self.collection.remove()
        self.object_collection.update(
            {},
            {'$pull':dict(aggregates=self.name)},
            multi=True)
        return self.incremental(jobid)

    sum_js = '''function(key,values) {
      var total = 0;
      for(var i = 0; i < values.length; i++) {
        total += values[i]; }
      return total; }'''

orm_session.mapper(Event, event)
orm_session.mapper(AggDef, agg_def)
