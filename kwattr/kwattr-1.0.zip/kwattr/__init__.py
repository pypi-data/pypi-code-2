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

def kwattr(data):
    'decorator: make kwargs from function attributes'
    data = {x: False for x in data.split()}

    def x(func):
        return KWATTR(data, func, False)
    return x
