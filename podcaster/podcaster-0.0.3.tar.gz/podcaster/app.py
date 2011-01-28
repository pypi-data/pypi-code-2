# -*- coding:utf-8 -*-
from nagare import wsgi, component

from podcaster.comp import Main


app = wsgi.WSGIApp(lambda: component.Component(Main()))
