#coding:utf-8
class Jsdict(object):
    def __init__(self, d=None):
        if d is None:
            d = {}
        self.__dict__["_Jsdict__d"] = d

    def __iter__(self):
        for i in self.__d.iteritems():
            yield i

    def __nonzero__(self):
        return bool(self.__d)

    def __setattr__(self, name, val):
        if val is not None:
            self.__d[name] = val

    def __getattr__(self, name):
        return self.__d.get(name, "")

    def __getitem__(self, name):
        return self.__d.get(name, "")

    def __contains__(self, b):
        return b in self.__d

    def __setitem__(self, name, val):
        if val is not None:
            self.__d[name] = val

    def __delitem__(self, name):
        del self.__d[name]

WHITE_SPACE = "\r\n \t"
class StripJsdict(object):
    def __init__(self, form):
        self.__dict__["_StripJsdict__f"] = form

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, name):
        v = self.__f[name]
        if type(v) is str:
            v = v.strip(WHITE_SPACE)
        return v

    def __iter__(self):
        for i in self.__f:
            yield i

    def __nonzero__(self):
        return bool(self.__f)

    def __setattr__(self, name, val):
        if val is not None:
            self.__f[name] = val

    def __contains__(self, b):
        return b in self.__f

    def __setitem__(self, name, val):
        if val is not None:
            self.__f[name] = val

    def __delitem__(self, name):
        del self.__f[name]

if "__main__" == __name__:
    a = Jsdict()
    a['1'] = 2
    for k, v in a:
        print k, v
    b = dict(list(a))
    print b
