import cherrypy
import os

from . import staticdirindex
from . import htmldir

def serve_local():
	"""
	Serve the current directory as static files.
	"""
	config = {
		'global': {
			'server.socket_host': '::0',
		},
		'/': {
			'tools.staticdir.on': 'true',
			'tools.staticdir.indexlister': htmldir.htmldir,
			'tools.staticdir.dir': os.getcwd(),
		},
	}
	cherrypy.quickstart(None, config=config)
