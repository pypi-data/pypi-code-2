from __future__ import with_statement

import os
import itertools

from pyf.dataflow import component
from pyf.splitter import get_splitter, get_input_item_flow

import logging
logger = logging.getLogger()

class WarehouseStorageException(Exception):
    pass

class WarehouseStorage(object):
    def __init__(self, max_items_per_shelve=500, index_key=None):
        self.max_items = max_items_per_shelve
        
        self.shelves = list()
        
        self.use_index = index_key is not None
        self.index_key = index_key
        self.current_index = 0
        self.current_count = 0
        self.index_bucket = None
        self.bucket_names = None
    
    def load(self, items_flow, split_node_name=None):
        """Function to load items in the warehouse storage.

        @param: max_items: Max Input Items to split
        @type: Integer
        
        @param split_node_name: The node name that we want to keep for a chunk.
        example : TransactionReference
        @type: String
        """
        if self.use_index:
            items_flow = self.__index_setter(items_flow,
                                             self.index_key)

        items_flow = self.__element_counter(items_flow)
            
        if self.use_index and split_node_name is None:
            self.index_bucket = dict()
            self.bucket_names = list()
            splitter = get_splitter(max_items=self.max_items)
            bucket_name_index = 0
            current_bucket_name = None
            for item in items_flow:
                bucket_name = splitter.push(item)
                
                if bucket_name != current_bucket_name:
                    if not bucket_name in self.bucket_names:
                        self.bucket_names.append(bucket_name)
                        bucket_name_index = self.bucket_names.index(bucket_name)
                        current_bucket_name = bucket_name
                     
                index_key = getattr(item, self.index_key, None)
                if not index_key is None:
                    self.index_bucket[index_key] = bucket_name_index
                
            buckets = splitter.finalize()
            
        else:
            splitter = get_splitter(items_flow,
                                self.max_items,
                                split_node_name)
            buckets = splitter.split()
            
        self.shelve_buckets(buckets)
        
    def __index_setter(self, items, key):
        start = self.current_index + 1
        for num, item in enumerate(items):
            self.current_index = num + start
            setattr(item, key, self.current_index)
            yield item

    def __element_counter(self, items):
        start = self.current_count + 1
        for num, item in enumerate(items):
            self.current_count = num + start
            yield item

    def __len__(self):
        return self.current_count
    
    @component('IN', 'OUT')
    def loader(self, items, result):
        """ A loader component to use with pyf.dataflow.
        Yields the status of the operation"""
        self.load(items)
        # if no error happened, tell we succeed
        yield True
    
    def shelve_buckets(self, buckets):
        for bucket in buckets:
            if bucket not in self.shelves:
                self.shelves.append(bucket)
    
    def retrieve(self, shelves=None):
        """ Retrieve the content of the storage as a data flow
        @param shelves: List of shelves to retrieve all item, if shelves is None,
        the method retrieve all item from all shelves
        @type shelves: List of filename 
        """
        if shelves is None:
            shelves = self.shelves
            
        for shelve in shelves:
            with open(shelve, 'r') as shelve_file:
                for item in get_input_item_flow(shelve_file):
                    yield item
                    
    def __iter__(self):
        """ Just retrieve contents as an iterator """
        return self.retrieve()
            
    def roll_and_filter(self, comp, shelves=None):
        """ Retrieve all the data matching some criterions as a generator.
        
        Example : storage.roll_and_filter(lambda x: not x.value % 2)
        
        @param comp: fonction(s) to use for comparison (takes an object as param
        and returns true or false wether to return the object or not).
        @type comp: function or list of functions
        
        @param shelves: List of shelves to retrieve all item, if shelves is None,
        the method retrieve all item from all shelves
        @type shelves: List of filename 
        """
        if not isinstance(comp, list):
            comp = [comp]
        
        current_iterator = self.retrieve(shelves)
        
        for comparison in comp:
            current_iterator = itertools.ifilter(comparison, current_iterator)
            
        return current_iterator
    
    def selective_retrieve(self, id_list):
        shelves = None
        if not self.index_bucket is None:
            shelves = list()
            for id in id_list:
                if id in self.index_bucket:
                    shelve = self.bucket_names[self.index_bucket[id]]
                    if not shelve in shelves:
                        shelves.append(shelve)

        if self.index_key:
            return self.roll_and_filter(
                    lambda x: getattr(x, self.index_key) in id_list,
                    shelves = shelves)
        else:
            msg = 'Cannot use selective retrieve without defined index key'
            raise WarehouseStorageException(msg)
        
    def clean(self):
        """ A function that cleans all the shelves, and throw everything.
        Warning, don't expect to get the items afterward."""
        for shelve in self.shelves:
            logger.debug('removing temp file %s' % shelve)
            os.unlink(shelve)
            
        self.shelves = list()
        self.current_index= 0
        self.current_count = 0
