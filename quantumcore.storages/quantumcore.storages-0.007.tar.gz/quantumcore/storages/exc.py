import quantumcore.exceptions

class DuplicateKey(quantumcore.exceptions.QuantumCoreException):
    """a duplicate unique key has been detected"""
    
    def __init__(self, k):
        self.key = k
    
    def __str__(self):
        return u"Duplicate Key '%s' detected." %self.key
        
        
class KeyGenerationError(quantumcore.exceptions.QuantumCoreException):
    """system was unable to generate a new key"""
    
    def __init__(self, reason=u"unkown"):
        self.reason = reason
    
    def __str__(self):
        return u"key couldn't be generated. Reason: %s" %self.reason