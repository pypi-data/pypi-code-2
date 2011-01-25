from amalgam.backends.base.columns import BaseColumns


class BaseBackend(BaseColumns):
    def __init__(self, uri):
        '''Initialize backend
        '''
        self.uri = uri

    def __call__(self, prefix=None):
        '''Return Base for models with optional prefix for table names
        '''
        raise NotImplementedError()
