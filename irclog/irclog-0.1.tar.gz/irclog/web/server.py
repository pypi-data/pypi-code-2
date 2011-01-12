""":mod:`irclog.web.server` --- Built-in web server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line interface
----------------------

.. program:: python -m irclog.web.server

This module provides a command line interface for running the web server.

.. sourcecode:: bash

   $ python -m irclog.web.server
   Usage: python -m irclog.web.server [options] archive-path

   python -m irclog.web.server: error: archive path is required

It takes exactly one argument, the path of log archive, and several options
following explained:

.. option:: -H <host>, --host <host>

   Host to listen. Default: ``0.0.0.0``.

.. option:: -p <port>, --port <port>

   Port to bind. Default: ``8080``.

.. option:: -T <path>, --template <path>

   HTML template path. Default: :file:`basic`.

.. option:: -P <prefix>, --path-prefix <prefix>

   Prefix of the URL path.

.. option:: -d, --debug

   Debug mode.


Internals
---------

.. function:: serve(host, port, app)

   Serves a WSGI application.

   :param host: a host to listen
   :type host: :class:`basestring`
   :param port: a port to listen
   :type port: :class:`int`
   :type app: a WSGI application
   :type app: callable object

"""
import os.path
import optparse
import irclog.web


BUILTIN_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")


try:
    import meinheld
    def serve(host, port, app):
        meinheld.server.listen((host, port))
        meinheld.server.run(app)
except ImportError:
    try:
        import gevent.wsgi
        def serve(host, port, app):
            httpd = gevent.wsgi.WSGIServer((host, port), app)
            httpd.serve_forever()
    except ImportError:
        try:
            import rocket
            def serve(host, port, app):
                httpd = rocket.Rocket((host, port), "wsgi", {"wsgi_app": app})
                httpd.start()
        except ImportError:
            import wsgiref.simple_server
            def serve(host, port, app):
                httpd = wsgiref.simple_server.make_server(host, port, app)
                httpd.serve_forever()


def main():
    description = "Serve IRC log archive as web. The archive-path is a " \
                  "pattern like /<server>/<channel>/<date:%Y-%m-%d>."
    parser = optparse.OptionParser(prog="python -m irclog.web.server",
                                   usage="Usage: %prog [options] archive-path",
                                   description=description)
    parser.add_option("-H", "--host", default="0.0.0.0",
                      help="host to listen [%default]")
    parser.add_option("-p", "--port", type="int", default="8080",
                      help="port to bind [%default]")
    parser.add_option("-T", "--template", metavar="PATH", default="basic",
                      help="HTML template path [%default]")
    parser.add_option("-P", "--path-prefix", metavar="PREFIX", default="",
                      help="prefix of the URL path")
    parser.add_option("-d", "--debug", action="store_true",
                      help="debug mode")
    options, args = parser.parse_args()
    try:
        archive_path, = args
    except ValueError:
        parser.error("archive path is required")
    template = options.template
    if not os.path.isdir(template):
        template = os.path.join(BUILTIN_TEMPLATE_PATH, template)
    if not os.path.isdir(template):
        parser.error("--template path is not correct")
    app = irclog.web.Application(archive_path, template, options.path_prefix,
                                 debug=options.debug)
    serve(options.host, options.port, app)


if __name__ == "__main__":
    main()

