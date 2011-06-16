from datetime import datetime, timedelta
from unittest import TestCase

import ming
from ming.orm import session

from zarkov import model as M

class TestAggDef(TestCase):

    def setUp(self):
        ming.configure(**{
                'ming.main.master':'mim:///',
                'ming.main.database':'zarkov'})

    def test_setup_agg(self):
        agg = self._setup_agg()
        self.assertEqual(agg.collection, M.doc_session.db.sum_by_minute)
        self.assertEqual(agg.object_collection, M.doc_session.db.event)

    def test_incremental(self):
        agg = self._setup_agg()
        self._setup_events()
        agg.incremental()
        self._setup_events()
        agg.incremental()

    def test_full(self):
        agg = self._setup_agg()
        self._setup_events()
        agg.full()
        self._setup_events()
        agg.full()

    def _setup_agg(self):
        agg = M.AggDef.simple_count(
            'event', 'sum_by_minute', 'this.timestamp.getMinutes()')
        session(agg).flush()
        return agg
 
    def _setup_events(self):
        ts = datetime.utcnow()
        for x in range(100):
            ev = M.event.make(dict(
                    type='test',
                    timestamp=ts+timedelta(seconds=x),
                    context=dict(
                        user='test-user',
                        project='test-project',
                        tool='test--tool')))
            ev.m.insert()

        
                
