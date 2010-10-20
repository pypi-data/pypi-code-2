import os
import sys
import argparse
import urlparse
import urllib
import cherrypy


class DjangoApplication(object):
    def __init__(self):
        self.domains = {}
        self.get_args()
        self.init()
        self.load()
        self.cfg_media()

    def get_args(self):
        parser = argparse.ArgumentParser(
            prog='cherrydev',
            description='Starts a CherryPy web server for Django development.')
        parser.add_argument(
            'settings_path',
            metavar='SETTINGS_PATH',
            nargs='?',
            help="""
            By default SETTINGS_PATH will look for settings.py
            in the current directory.""")
        parser.add_argument(
            '--noreload',
            dest='autoreload_on',
            action='store_false',
            default=True,
            help='Tells CherryPy to NOT use the auto-reloader.')
        parser.add_argument(
            '-b', '--bind',
            dest='address',
            default='127.0.0.1:8000',
            help="""
            The socket to bind. A string of the form: 'HOST', 'HOST:PORT'.
            An IP is a valid HOST. (default: '127.0.0.1:8000')""")
        media_group = parser.add_argument_group('Media', """
            By default, CherryPy will be used to serve your media. If your
            MEDIA_URL includes a host component, it will be changed to an
            alternate port on localhost. If your ADMIN_MEDIA_PREFIX includes
            a host component that does not match that of MEDIA_URL, it will
            also be changed to its own alternate port.""")
        media = media_group.add_mutually_exclusive_group()
        media.add_argument(
            '--nomedia',
            dest='media_on',
            action='store_false',
            default=True,
            help='Tells CherryPy to NOT host media.')
        media.add_argument(
            '-m', '--media',
            dest='media_addr',
            default='127.0.0.1:8001',
            help="""
            The socket to bind media. A string of the form: 'HOST', 'HOST:PORT'.
            An IP is a valid HOST. (default: '127.0.0.1:8001')""")
        admin = media_group.add_mutually_exclusive_group()
        admin.add_argument(
            '--noadmin',
            dest='admin_on',
            action='store_false',
            default=True,
            help='Tells CherryPy to NOT host admin media.')
        admin.add_argument(
            '-a', '--admin',
            dest='admin_addr',
            default='127.0.0.1:8002',
            help="""
            The socket to bind admin. A string of the form: 'HOST', 'HOST:PORT'.
            An IP is a valid HOST. (default: '127.0.0.1:8002')""")
        media_group.add_argument(
            '-l', '--link',
            dest='link_dir',
            action='append',
            default=[],
            type=self.link_dir,
            help="""
            An additional directory to be linked to MEDIA_URL. May be used
            multiple times. A string of the form: 'PATH=DIRECTORY'. (e.g.
            'app=../myapp/media')""")
        self.args = parser.parse_args()

    def link_dir(self, string):
        if string.count('=') != 1:
            raise argparse.ArgumentTypeError(
                'Invalid link directory format: %s' % string)
        path, root = string.split('=')
        if not os.path.exists(root):
            raise argparse.ArgumentTypeError(
                'Link directory does not exist: %s' % root)
        return path, os.path.abspath(root)

    def init(self):
        project_path = os.getcwd()

        if self.args.settings_path:
            settings_path = os.path.abspath(
                os.path.normpath(self.args.settings_path))
            if not os.path.exists(settings_path):
                self.no_settings(settings_path)
            else:
                project_path = os.path.dirname(settings_path)
        else:
             settings_path = os.path.join(project_path, 'settings.py')
             if not os.path.exists(settings_path):
                 self.no_settings(settings_path)

        project_name = os.path.split(project_path)[-1]
        settings_name, ext = os.path.splitext(os.path.basename(settings_path))
        self.settings_modname = '%s.%s' % (project_name, settings_name)

        sys.path.insert(0, project_path)
        sys.path.append(os.path.join(project_path, os.pardir))

    def no_settings(self, path):
        error = "Settings file '%s' not found in current folder.\n" % path
        sys.stderr.write(error)
        sys.stderr.flush()
        sys.exit(1)

    def load(self):
        settings = __import__(self.settings_modname, fromlist=[0])
        media_url = urlparse.urlsplit(settings.MEDIA_URL)
        admin_url = urlparse.urlsplit(settings.ADMIN_MEDIA_PREFIX)

        if self.args.media_on:
            if media_url.netloc:
                settings.MEDIA_URL = urlparse.urlunsplit(
                    ('http', self.args.media_addr) + media_url[2:])
                self.add_server(self.args.media_addr)

        if self.args.admin_on:
            if (self.args.media_on and media_url.netloc and
                media_url.netloc == admin_url.netloc):
                settings.ADMIN_MEDIA_PREFIX = urlparse.urlunsplit(
                    ('http', self.args.media_addr) + admin_url[2:])
            elif admin_url.netloc:
                settings.ADMIN_MEDIA_PREFIX = urlparse.urlunsplit(
                    ('http', self.args.admin_addr) + admin_url[2:])
                self.add_server(self.args.admin_addr)

        from django.core.management import setup_environ
        setup_environ(settings, self.settings_modname)

    def add_server(self, netloc):
        from cherrypy._cpwsgi_server import CPWSGIServer
        from cherrypy._cpserver import ServerAdapter

        server = CPWSGIServer()
        server.bind_addr = urllib.splitnport(netloc, 80)
        adapter = ServerAdapter(cherrypy.engine, server, server.bind_addr)
        adapter.subscribe()

    def cfg_media(self):
        from django.conf import settings

        if self.args.admin_on:
            import django
            admin_root = os.path.join(
                django.__path__[0], 'contrib', 'admin', 'media')
            admin_url = urlparse.urlsplit(settings.ADMIN_MEDIA_PREFIX)
            admin_path = admin_url.path.rstrip('/')
            admin_conf = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': admin_root,
            }

            if self.args.media_on and admin_url.netloc == self.args.media_addr:
                self.args.link_dir.append((admin_path, admin_root))
            elif admin_url.netloc:
                self.domains[admin_url.netloc] = cherrypy.Application(
                    root=None, config={admin_path or '/': admin_conf})
            elif admin_path:
                cherrypy.tree.mount(None, admin_path, {'/': admin_conf})

        if self.args.media_on:
            media_url = urlparse.urlsplit(settings.MEDIA_URL)
            media_path = media_url.path.rstrip('/')
            media_conf = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': settings.MEDIA_ROOT,
            }

            if media_url.netloc:
                config = {media_path or '/': media_conf}
                for path, conf in self.get_links(media_path):
                    config[path] = conf
                self.domains[media_url.netloc] = cherrypy.Application(
                    root=None, config=config)
            elif media_path:
                cherrypy.tree.mount(None, media_path, {'/': media_conf})
                for path, conf in self.get_links(media_path):
                    cherrypy.tree.mount(None, path, {'/': conf})

    def get_links(self, media_path):
        for path, root in self.args.link_dir:
            if path and not path.startswith('/'):
                path = '/'.join([media_path, path])
            path = path.rstrip('/')
            if path:
                yield path, {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': root,
                }

    def run(self):
        host, port = urllib.splitnport(self.args.address, 80)
        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
            'log.screen': True,
            'engine.autoreload_on': self.args.autoreload_on,
        })

        from django.core.handlers.wsgi import WSGIHandler
        app = WSGIHandler()

        if self.domains:
            app = cherrypy.wsgi.VirtualHost(app, self.domains)

        cherrypy.tree.graft(app)

        cherrypy.engine.start()
        cherrypy.engine.block()


def main():
    DjangoApplication().run()
