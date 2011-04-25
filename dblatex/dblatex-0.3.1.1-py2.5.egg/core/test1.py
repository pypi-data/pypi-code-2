from error import ErrorHandler, get_handler, set_handler

class Tutu:
    pass

class MyError(ErrorHandler):
    def signal(self, object, *args, **kwargs):
        print "Error on object %s" % object

a = Tutu()
e = MyError()

try:
    set_handler(a)
except Exception, x:
    print x

try:
    set_handler(e)
    r = get_handler()
    if r != e:
        print "BOO"
    r.signal(a, "Something wrong")
except Exception, x:
    print x


