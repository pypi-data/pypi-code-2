class AtomPigletError(Exception):
    """Errors raised while using AtomPiglet."""
    pass

class ServerError(AtomPigletError):
    """Errors raised while trying to communicate with an AtomPub server."""
    pass

class NotFoundError(AtomPigletError):
    """Errors raised when a document is not located as expected."""
    pass

class EntryError(AtomPigletError):
    """Errors relating to the interaction with an atom:entry."""
    pass

class EntryEditError(EntryError):
    """Errors relating to the failure of edits to an atom:entry or its content. This usually 
       is due to non-matching entity tags."""
    pass
