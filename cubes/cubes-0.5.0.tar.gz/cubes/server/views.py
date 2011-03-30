from werkzeug.wrappers import Response
from werkzeug.utils import redirect
from werkzeug.exceptions import NotFound
from slicer.utils import *

import cubes

def hello(request):
    model = cubes.load_model(logical_model_path)
    return Response("model: %s" % model.__class__)

@expose('/')
def new(request):
    error = url = ''
    return Response('hello')

@expose('/aggregate')
def new(request):
    error = url = ''
    return Response('aggregate')
