import os
from huck import web

class Handler(web.RequestHandler): pass

class Application(web.Application):

    def __init__(self, route, options):
        root_path = os.path.dirname(os.path.realpath(__file__))

        setup = {
            'debug': options['debug'],
            'static_path': os.path.join(root_path, 'static'),
            'template_path': os.path.join(root_path, 'templates'),
        }

        route.append((r'/static/(.*)', web.StaticFileHandler, {'path': setup['template_path']}))

        web.Application.__init__(self, route, **setup)
