'''
All available exceptions in GAE framework engine.
'''
class PageNotFound(Exception):
    '''404 error'''
    pass

class AccessDenied(Exception):
    '''500 error'''
    pass

class IncorrectUrlDefinition(Exception):
    '''Incorrect url'''
    pass