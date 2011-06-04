import uuid
import traceback
import json
import pickle
from paxd.app.http import Response
from paxd.app.msg import PRequest
from redis import Redis
from paxd.webuiapp import html

def webui_app(request):
    try:
        response = handle_request(request)
    except:
        response = Response(500, 'Server Error %s' % traceback.format_exc())
    return response

def handle_request(request):
    if request.path == '/':
        return Response(200, get_apps())
    elif request.path.startswith('/load'):
        return Response(200, load_app(request))
    elif request.path.startswith('/unload'):
        return Response(200, unload_app(request))
    elif request.path.startswith('/failed'):
        return Response(200, get_failed(request))
    elif request.path.startswith('/pause'):
        return Response(200, pause_app(request))
    elif request.path.startswith('/unpause'):
        return Response(200, unpause_app(request))
    return Response(404, 'Not Found')

controller_queue = '_paxd.controller'
def get_apps():
    redis = Redis('localhost')
    req = PRequest(redis, controller_queue, {
            'command' : 'APPLIST'
        }, timeout=2)
    promise = req.send()
    resp = promise.get()
    if not resp:
        return 'NO RESPONSE'
    
    return html.header() + html.applications(resp) + html.footer()

def load_app(request):
    redis = Redis('localhost')
    single_app = request.GET.get('queue') and request.GET.get('entry')
    autoconf = request.GET.get('autoconf')
    
    assert autoconf == 'file' or single_app, (single_app, autoconf)
    
    if single_app:
        promise = PRequest(redis, controller_queue, {
            'command' : 'LOAD_APP',
            'path' : request.GET['path'], 
            'entrypoint': request.GET.get('entry'), 
            'queue' : request.GET.get('queue'),
        })
    else:
        promise = PRequest(redis, controller_queue, {
            'command' : 'LOAD_AUTO',
            'path' : request.GET['path'], 
            'autoconfigure' : request.GET.get('autoconfigure') == 'true',
        })
        


    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    return json.dumps(resp)

def get_failed(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'GET_FAILED',
        'id' : request.GET['id'], 
    }, timeout=10)
    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    return html.header() + html.failed(resp) + html.footer()

def unload_app(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'UNLOAD',
        'id' : request.GET['id'], 
    }, timeout=10)
    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    return json.dumps(resp)

def pause_app(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'PAUSE',
        'id' : request.GET['id'], 
    }, timeout=4)
    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    return json.dumps(resp)

def unpause_app(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'UNPAUSE',
        'id' : request.GET['id'], 
    }, timeout=4)
    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    return json.dumps(resp)
