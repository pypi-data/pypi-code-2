"""Google Checkout Payment Adapter

Interacts with the Google Checkout API using mapped fields from the
Payment module.

"""
from paypy.adapters          import __init__ as adapters

from paypy.exceptions.google import GoogleException

class GoogleResult(adapters.Result):
    """Represent a transaction result as an object."""
    
    pass

class Transaction(adapters.Adapter):
    """Create an object representing a Google Checkout transaction."""
    
    def __init__(self, configuration):
        
        pass
    
    def set_fields(self, fields):
        """Amend the instantiated configuration with more fields."""
        
        pass
    
    def process(self):
        """Process the transaction and return a result."""
        
        return GoogleResult(result)
