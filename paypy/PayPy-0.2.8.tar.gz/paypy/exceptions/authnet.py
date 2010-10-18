class AuthnetException(Exception):
    """Authorize.net base exception class."""
    
    pass

class AIMException(AuthnetException):
    """Authorize.net AIM base exception class."""
    
    pass

class ARBException(AuthnetException):
    """Authorize.net ARB base exception class."""
    
    pass
