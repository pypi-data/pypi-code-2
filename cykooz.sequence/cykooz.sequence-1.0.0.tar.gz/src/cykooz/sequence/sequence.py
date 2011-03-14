"""Adapter for generating sequences"""

import threading

from persistent import Persistent
import zope.annotation.interfaces
import zope.component
import zope.interface

from interfaces import ISequenceGenerator


class SequenceGenerator(object):
    zope.interface.implements(ISequenceGenerator)
    zope.component.adapts(zope.annotation.interfaces.IAnnotatable)

    annotation_key = 'cykooz.sequence'
    sequence_lock = threading.Lock()
    storage_lock = threading.Lock()

    def __init__(self, context):
        self.context = context


    def getNextValue(self):
        self.sequence_lock.acquire()
        try:
            # this part is required to be thread/ZEO safe
            last = self._get_last_value()
            last += 1
            self._set_last_value(last)
            return last
        finally:
            self.sequence_lock.release()


    def setNextValue(self, value):
        if not isinstance(value, (int, long)):
            raise ValueError, 'setNextValue expected Integer, %s found.' % type(value)
        self._set_last_value(value - 1)


    def _get_last_value(self):
        return self._get_sequence_storage().last_value


    def _set_last_value(self, last):
        self._get_sequence_storage().last_value = last


    def _get_sequence_storage(self):
        self.storage_lock.acquire()
        try:
            annotatable = zope.annotation.interfaces.IAnnotatable(self.context)
            seq_st = annotatable.get(self.annotation_key)
            if seq_st is None:
                seq_st = SequenceStorage()
                annotatable[self.annotation_key] = seq_st
            return seq_st
        finally:
            self.storage_lock.release()


class SequenceStorage(Persistent):
    '''Store the actual sequence value'''

    last_value = 0

    def _p_resolveConflict(self, oldState, savedState, newState):
        max_value = max(savedState['last_value'], newState['last_value'])
        savedState['last_value'] = max_value
        return savedState
