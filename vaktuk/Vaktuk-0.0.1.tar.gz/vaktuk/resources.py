class Resource(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        raise KeyError('Finished iterating tree for traversal.')

    @classmethod
    def factory(cls, *args, **kwargs):
        return cls(*args, **kwargs)
