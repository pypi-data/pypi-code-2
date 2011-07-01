import uuid
import traceback
import json
import pickle
from paxd.app.http import Response
from paxd.app.msg import PRequest
from redis import Redis
from paxd.webuiapp import html

################################
#  Web UI App/Routing
################################

def webui_app(request):
    try:
        response = handle_request(request)
    except:
        response = Response(500, 'Server Error %s' % traceback.format_exc())
    return response


def route_mapping():
    return (
        ('/load', load_app),
        ('/unload', unload_app),
        ('/failed/remove', remove_failed),
        ('/failed/requeue', requeue_failed),
        ('/failed', get_failed),
        ('/pause', pause_app),
        ('/unpause', unpause_app),
        ('/trace', trace_app),
        ('/', get_apps),
    )

def route(request):
    for path, fun in route_mapping():
        if request.path.startswith(path):
            return fun
    return None

def handle_request(request):
    fun = route(request)
    if fun is None:
        return Response(404, 'Not Found')
    try:
        return Response(200, fun(request), content_type='text/html')
    except NoResponse:
        return Response(500, 'No Response from controller')

################################
#  Web UI Actions
################################

controller_queue = '_paxd.controller'
def get_apps(request):
    redis = Redis('localhost')
    req = PRequest(redis, controller_queue, {
            'command' : 'APPLIST'
        }, timeout=2)
    promise = req.send()
    resp = promise.get()
    if not resp:
        return 'NO RESPONSE'
    
    return html.render('applications.html', {'apps' : resp})
    # return html.header() + html.applications(resp) + html.footer()

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

def requeue_failed(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'REQUEUE_FAILED',
        'id' : request.GET['id'], 
        'fid' : request.GET['fid'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return json.dumps(res)

def remove_failed(request):
    print 'remove failed', 1
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : 'REMOVE_FAILED',
        'id' : request.GET['id'], 
        'fid' : request.GET['fid'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return json.dumps(res)

def get_failed(request):
    resp = id_app(request, 'GET_FAILED')
    res = html.render('failed.html', resp)
    return res

def unload_app(request):
    resp = id_app(request, 'UNLOAD')
    return json.dumps(resp)

def pause_app(request):
    resp = id_app(request, 'PAUSE')
    return json.dumps(resp)

def unpause_app(request):
    resp = id_app(request, 'UNPAUSE')
    return json.dumps(resp)

def trace_app(request):
    resp = id_app(request, 'TRACE')
    return html.render('traces.html', resp)

def id_app(request, command_name):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : command_name,
        'id' : request.GET['id'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return res

class NoResponse(Exception):
    pass

