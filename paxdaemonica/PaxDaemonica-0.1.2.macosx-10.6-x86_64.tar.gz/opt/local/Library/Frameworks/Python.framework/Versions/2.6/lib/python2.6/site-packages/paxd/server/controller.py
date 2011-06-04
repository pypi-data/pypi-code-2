from multiprocessing import Process, Pipe, Queue
from Queue import Empty
from signal import signal, SIGINT, SIGKILL, SIGTERM
from threading import RLock, Thread
import os
import sys
import pickle
import json
from redis import Redis

from paxd.app.application import Application
from paxd.process import print_exc
from paxd.server.webstats import start_webui
from paxd.app.msg import BaseRequest, BaseResponse

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Controller(object):
    command_queue = '_paxd.controller'
    webui_queue = '_paxd.web_ui'
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.lock = RLock()
        self.processes = []
        self.threads = []
        self.applications = []
    
    def run(self):
        try:
            print 'STARTING UP CONTROLLER.  pid: ', os.getpid()
            # Internal Applications
            self.start_process(start_webui, self.webui_queue)
            
            # Start "apps"
            self.configure()
            
            # Wait For Commands
            self.handle_commands()
        except Exception, e:
            print 'TERMINATING', e
            import sys
            for process in self.processes:
                process.terminate()
            raise
    
    def configure(self):
        redis = Redis('localhost')
        config = redis.hget('_paxd.controllers.config', self.instance_id)
        if not config:
            self.load_app(PROJECT_PATH, 'paxd.webuiapp.webui.webui_app', self.webui_queue, name="paxd admin/api", unstoppable=True)
            return
        config = json.loads(config)
        for app in config['applications']:
            application = self.load_app(app['path'], app['entry'], app['queue'], environment=app['environment'], name=app['name'], unstoppable=app['unstoppable'], id=app['id'])
            if app['status'] == 'stopped' or app['status'] == 'paused':
                application.pause()
    
    def handle_commands(self):
        thread = Thread(target=command_thread, args=(self,))
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        while True:
            try:
                thread.join(60)
            except KeyboardInterrupt:
                print 'CONTROLLER EXITING'
                sys.exit(0)
    
    def load_app(self, path, entry, queue, environment=None, logger=None, name=None, unstoppable=False, id=None):
        if not name:
            name = entry
        application = Application(self.instance_id, name, path, entry, queue, logger, environment=environment, unstoppable=unstoppable, id=id)
        with self.lock:
            self.applications.append(application)
        application.run()
        return application
    
    def load_auto(self, path):
        with open(os.path.join(path, 'pax.conf')) as conf_file:
            conf = json.loads(conf_file.read())
        
        environment = {}
        for k, v in conf.get('ENVIRONMENT',{}).iteritems():
            environment[k] = v
        print conf.get('ENVIRONMENT',{})
        apps = []
        for entry, appconf in conf['APPS'].iteritems():
            apps.append(self.load_app(path, entry, entry, environment=environment))
        return apps
    
    def start_process(self, fun, name):
        process = Process(target=fun, args=(name,))
        process.start()
        print 'STARTING INTERNAL PROCESS', name, process.pid
        self.processes.append(process)

def command_thread(controller):
    redis = Redis('localhost')
    while True:
        with print_exc:
            _, value = redis.blpop(controller.command_queue)
            request = BaseRequest.from_serialized(value)
            
            resp_data = handle_command(controller, redis, request.deserialize(request.args))
            
            response = request.response_class(request.response_queue, 'SUCCESS', resp_data)
            pipe = redis.pipeline()
            q = request.response_queue
            ser = response.serialize_resp()
            pipe.lpush(q, ser)
            pipe.expire(request.response_queue, request.timeout)
            # pipe.lrem(self.active_queue, 1, request.raw)
            pipe.execute()
            save_settings(redis, controller)

def save_settings(redis, controller):
    pipe = redis.pipeline()
    apps = []
    with controller.lock:
        for app in controller.applications:
            apps.append(app.json_info)
    redis.hset('_paxd.controllers.config', controller.instance_id, json.dumps({
        'applications' : apps,
    }))

def handle_command(controller, redis, rdata):
    command = rdata['command']
    if command == 'APPLIST':
        return handle_list(controller, redis, rdata)
    elif command == 'LOAD_APP':
        return handle_load_app(controller, redis, rdata)
    elif command == 'LOAD_AUTO':
        return handle_load_auto(controller, redis, rdata)
    elif command == 'UNLOAD':
        return handle_unload(controller, redis, rdata)
    elif command == 'PAUSE' or command == 'UNPAUSE':
        return handle_pause_unpause(controller, redis, rdata)
    elif command == 'GET_FAILED':
        return handle_get_failed(controller, redis, rdata)
    return 'BAD COMMAND'

def handle_list(controller, redis, rdata):
    ret = []
    with controller.lock:
        for app in controller.applications:
            json_info = app.json_info
            json_info.update(**app.queue_info(redis))
            ret.append(json_info)
    return ret

def handle_get_failed(controller, redis, rdata):
    id = rdata['id']
    with controller.lock:
        for app in controller.applications:
            if app.id == id:
                return { 'status' : 'SUCCESS', 'failed' : app.failed_items, 'app' : app.json_info }
    return { 'status' : 'FAILURE', 'reason' : 'NO SUCH APP ID' }
    

def handle_load_app(controller, redis, rdata):
    apps = controller.load_app(rdata['path'], rdata['entrypoint'], rdata['queue'], None)
    return { 'status' : 'SUCCESS', 'apps' : [app.json_info] }

def handle_load_auto(controller, redis, rdata):
    apps = controller.load_auto(rdata['path'])
    return { 'status' : 'SUCCESS', 'apps' : [app.json_info for app in apps] }


def handle_unload(controller, redis, rdata):
    id = rdata['id']
    with controller.lock:
        for app in controller.applications:
            if app.id == id:
                app.quit()
                break
        else:
            return { 'status' : 'FAILURE', 'reason' : 'NO SUCH APP ID' }
        controller.applications = [a for a in controller.applications if a.id != id]
        return { 'status' : 'SUCCESS', 'app' : app.json_info }

def handle_pause_unpause(controller, redis, rdata):
    id = rdata['id']
    with controller.lock:
        for app in controller.applications:
            if app.id == id:
                if rdata['command'] == 'PAUSE':
                    app.pause()
                else:
                    app.unpause()
                return { 'status' : 'SUCCESS', 'app' : app.json_info }
    return { 'status' : 'FAILURE', 'reason' : 'NO SUCH APP ID' }

