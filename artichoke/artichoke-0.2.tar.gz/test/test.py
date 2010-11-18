import artichoke, os
from artichoke import expose

class SubController(artichoke.Controller):
    @expose()
    def about(self, request, response, args, params):
        return 'HELLO %s' % str(args)

    @expose()
    def index(self, request, response, args, params):
        return 'INDEX'

    @expose()
    def not_found(self, request, response, args, params):
        return 'Sub Not Found'

class RootController(artichoke.Controller):
    def __init__(self, templates_path, helpers):
        super(RootController, self).__init__(templates_path, helpers)
        self.sub = SubController(os.path.join(templates_path, 'sub'), helpers)

    @expose('index')
    def index(self, request, response, args, params):
        foo = True
        return dict(foo=foo)

    @expose('index')
    def other(self, request, response, args, params):
        foo = params.get('foo', False)
        response.flash('Flash here!')
        return dict(foo=foo)

    @expose()
    def crash(self, request, response, args, params):
        raise Exception('FATAL')

    def hidden(self, request, response, args, params):
        return 'HIDDEN'

    @expose()
    def login(self, request, response, args, params):
        class FakeUser(object):
            pass

        user = FakeUser()
        user.user_name = params['user']
        user.password = params['password']

        response.identity = {'user':user}
        response.flash('Welcome back!')
        return self.redirect(response, '/index')

    @expose()
    def logout(self, request, response, args, params):
        response.identity = None
        return self.redirect(response, '/index')


app = artichoke.Application(root=RootController, templates_path='views')

if __name__ == '__main__':
    from artichoke.server import serve
    serve(app)
