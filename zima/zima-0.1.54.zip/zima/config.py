# -*- coding: utf-8 -*-
from bottle import WSGIRefServer

from utils import derive
from lilium import liliumDNA

board = derive(liliumDNA, {
	'root': '',
	'host': ['localhost', 'localhost:8070', '127.0.0.1'],
	'maxThreads': 90,
	'bumpLimit': 400,
	'captcha': None
	})

server = {
    'iface': '127.0.0.1:8070',
    'debug': True,
    'frontend': WSGIRefServer,
    'pipelineWidth': 4,
    '_kv': {}
    }
