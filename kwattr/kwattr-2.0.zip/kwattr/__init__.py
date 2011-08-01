'decorator: make keywords arguments of bool values from function attributes'

class KWATTR(object):
    def __init__(self, kw, func, dup):
        self.kw = dict(kw)
        self.func = func
        self.dup = dup

    def __getattr__(self, attr):
        if attr in self.kw:
            if self.dup:
                obj = self
            else:
                obj = self.__class__(self.kw, self.func, True)
            obj.kw[attr] = True
            return obj
        else:
            raise AttributeError(attr)

    def __call__(self, *args, **kwargs):
        kw = dict(self.kw)
        kw.update(kwargs)
        return self.func(*args, **kw)

class KWattr(object):
    def __init__(self, kw, dup):
        self.kw = dict(kw)
        self.dup = dup

    def __getattr__(self, attr):
        if self.dup:
            obj = self
        else:
            obj = self.__class__(self.kw, True)
        obj.kw[attr] = False
        return obj

    def __call__(self, func):
        return KWATTR(self.kw, func, False)

kwattr = KWattr({}, False)
