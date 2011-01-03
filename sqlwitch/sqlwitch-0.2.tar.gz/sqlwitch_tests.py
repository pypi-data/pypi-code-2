from __future__ import with_statement

import sys
import os

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '..'
    )
)
sys.path.append(ROOT)

import unittest
import sqlwitch

def sqlwitch_test(func):
    def test_wrapper(self):
        expected_sql = func.__doc__.strip()
        func(self)
        params = tuple(self.db.params())
        if len(params):
            self.assertEquals(expected_sql, self.db.sql() % params)
        else:
            self.assertEquals(expected_sql, self.db.sql())
    return test_wrapper

class SQLWitchTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlwitch.SQLWitch()
    
    @sqlwitch_test
    def test_simple_insert(self):
        '''
        insert into foobars (foo, bar) values (1, 2);
        '''
        with self.db.insert(into='foobars') as obj:
            obj.foo = 1
            obj.bar = 2
    
    @sqlwitch_test
    def test_simple_select(self):
        '''
        select foo, bar from foobars;
        '''
        self.db.select('foo, bar', from_='foobars')
        
    @sqlwitch_test
    def test_conditional_select_1(self):
        '''
        select foo, bar from foobars where foo = 1;
        '''
        with self.db.select('foo, bar', from_='foobars'):
            self.db.where('foo = %s', 1)

    @sqlwitch_test
    def test_conditional_select_2(self):
        '''
        select foo, bar from foobars where foo = 1 and bar = 2;
        '''
        with self.db.select('foo, bar', from_='foobars'):
            self.db.where('foo = %s', 1)
            self.db.where('bar = %s', 2)
            
    @sqlwitch_test
    def test_conditional_select_3(self):
        '''
        select foo, bar from foobars where foo = 1 limit 10;
        '''
        with self.db.select('foo, bar', from_='foobars'):
            self.db.where('foo = %s', 1)
            self.db.limit(10)

    @sqlwitch_test
    def test_conditional_select_4(self):
        '''
        select foo, bar from foobars where foo = 1 order by foo limit 10, 10;
        '''
        with self.db.select('foo, bar', from_='foobars'):
            self.db.where('foo = %s', 1)
            self.db.order_by('foo')
            self.db.limit(10, 10)

    @sqlwitch_test
    def test_limited_select(self):
        '''
        select foo, bar from foobars limit 10;
        '''
        self.db.select('foo, bar', from_='foobars')
        self.db.limit(10)

    @sqlwitch_test
    def test_offset_and_limited_select(self):
        '''
        select foo, bar from foobars limit 10, 10;
        '''
        self.db.select('foo, bar', from_='foobars')
        self.db.limit(10, 10)

    @sqlwitch_test
    def test_ordered_select(self):
        '''
        select foo, bar from foobars order by foo;
        '''
        self.db.select('foo, bar', from_='foobars')
        self.db.order_by('foo')
        
    @sqlwitch_test
    def test_select_in_1(self):
        '''
        select foo, bar from foobars where foo in (2);
        '''
        with self.db.select('foo, bar', from_='foobars'):
            self.db.where('foo')
            self.db.in_(*[2])
            
    @sqlwitch_test
    def test_select_in_2(self):
        '''
        select foo, bar from foobars where foo in (2);
        '''
        self.db.select('foo, bar', from_='foobars').where('foo').in_(*[2])

    @sqlwitch_test
    def test_simple_update(self):
        '''
        update foobars set foo = 2, bar = 1;
        '''
        with self.db.update('foobars') as obj:
            obj.foo = 2
            obj.bar = 1
            
    @sqlwitch_test
    def test_conditional_update_1(self):
        '''
        update foobars set foo = 2, bar = 1 where foo = 1;
        '''
        with self.db.update('foobars') as obj:
            obj.foo = 2
            obj.bar = 1
            self.db.where('foo = %s', 1)
            
    @sqlwitch_test
    def test_conditional_update_2(self):
        '''
        update foobars set foo = 3 where foo = 1 and bar = 2;
        '''
        with self.db.update('foobars') as obj:
            obj.foo = 3
            self.db.where('foo = %s', 1)
            self.db.where('bar = %s', 2)

    @sqlwitch_test
    def test_simple_delete(self):
        '''
        delete from foobars;
        '''
        self.db.delete(from_='foobars')

    @sqlwitch_test
    def test_conditional_delete_1(self):
        '''
        delete from foobars where foo = 1;
        '''
        with self.db.delete(from_='foobars'):
            self.db.where('foo = %s', 1)

    @sqlwitch_test
    def test_conditional_delete_2(self):
        '''
        delete from foobars where foo = 1 and bar = 2;
        '''
        with self.db.delete(from_='foobars'):
            self.db.where('foo = %s', 1)
            self.db.where('bar = %s', 2)
        
if __name__ == '__main__':
    unittest.main()
