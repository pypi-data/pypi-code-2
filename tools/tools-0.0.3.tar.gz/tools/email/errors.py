class EmailNotFound(Exception):
    pass

class AbuseError(Exception):
    pass

class AuthError(Exception):
    """
    Raised when credentials are invalid or other problem with
    starting working with service.
    """
