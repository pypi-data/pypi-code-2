"""
    Register a function to be called when the transaction aborts.
"""
import transaction
import logging

logger = logging.getLogger('getpaid.realex')

class AbortManager(object):
    """Simple data manager to call a hook on aborting the transaction"""

    handler = None

    def __init__(self, handler):
        self.handler = handler
    def tpc_finish(self, transaction):
        pass
    def sortKey(self):
        return 1
    def tpc_abort(self, transaction):
        pass
    def abort(self, transaction):
        logger.warn("Calling abort handler %s", self.handler)
        self.handler()

    def tpc_begin(self, transaction):
        pass
    def commit(self, transaction):
        pass
    def tpc_vote(self, transaction):
        pass

def registerAbortHook(handler):
    """Register a function which is to be called when the transaction aborts."""
    am = AbortManager(handler)
    txn = transaction.get()
    txn.join(am)

