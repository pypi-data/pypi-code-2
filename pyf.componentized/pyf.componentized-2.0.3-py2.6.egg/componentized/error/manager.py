class ManagerError(Exception):
    """the base class for all exceptions raised by Nostromo Manager
    """
    pass

class DataPathError(ManagerError):
    pass