from wsgiref.simple_server import make_server

from pystynamic.wsgi_app import PystynamicWSGIApp

def serve_command(root_path, port=8000):
    server = make_server('localhost', port, PystynamicWSGIApp(root_path))
    server.serve_forever()
