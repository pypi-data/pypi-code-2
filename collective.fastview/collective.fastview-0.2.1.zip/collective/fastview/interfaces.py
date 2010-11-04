import zope.interface

class ViewletNotFoundException(RuntimeError):
    """ Special exception for the cases we didn't found a viewlet the user asked through traversing """

class ViewletProcessingFailsException(RuntimeError):
    """ Special exception for the cases viewlet update() or render() raises exception.
    
    If we let exceptions like TraversalError or NotFound through,
    the orignal exception cause is lost.
    """
        
