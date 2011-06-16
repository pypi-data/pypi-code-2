

class FakeLabManager(object):
    def __init__(self):
        pass

    def __getattr__(self, val):
        import os
        from cPickle import loads
        pjoin = os.path.join
        dname = os.path.dirname
        def fakeapi(*args, **kwargs):
            import suds
            newval = val
            if args:
                newval = newval + '_' + args[0]
            return loads(open(pjoin(dname(dname(__file__)), 'rawoutput', newval)).read())
        return fakeapi
