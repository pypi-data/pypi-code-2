
def run_every(fn):
    def new(*args):
        return fn(*args)
    return new


def addspam(fn):
...     def new(*args):
...         print "spam, spam, spam"
...         return fn(*args)
...     return new