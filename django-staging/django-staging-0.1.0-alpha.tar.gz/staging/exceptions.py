class StagingException(Exception):
    pass

class ImproperlyConfigured(StagingException):
    pass

class RepoNotFound(StagingException):
    pass

class HGException(StagingException):
    pass
