class BigdoorError(Exception):
    """The base type of Bigdoor Exception"""

class MissingClient(BigdoorError):
    """Raised when there is no client available to service
    the request.
    """

class MissingParentDetails(BigdoorError):
    """Raised when there are certain attributes missing regarding a resource's
    parent.
    """

class PayloadError(BigdoorError):
    """Raised when there's a problem with the payload variable"""
