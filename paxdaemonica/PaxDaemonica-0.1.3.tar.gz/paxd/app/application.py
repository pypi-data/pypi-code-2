import traceback
import sys
import time
from threading import RLock, Thread
import uuid
import importlib
from redis import Redis
from multiprocessing import Process, Pipe, Pool, cpu_count
from paxd.process import print_exc
from paxd.app.msg import BaseRequest, BaseResponse

def init_process(path, env):
    import sys
    import os
    sys.path.insert(0, path)
    for k, v in env.iteritems():
        os.environ[k] = v

WORKER_FUNCTIONS = {}
def worker_fun(entry, args, kwds, format):
    import json
    import cPickle as pickle
    if format == 'pickle':
        deserialize = pickle.loads
    else:
        deserialize = json.loads
    try:
        if entry not in WORKER_FUNCTIONS:
            module, _, fun = entry.rpartition('.')
            module = importlib.import_module(module)
            WORKER_FUNCTIONS[entry] = getattr(module, fun)
        args = deserialize(args)
        kwds = deserialize(kwds)
        return WORKER_FUNCTIONS[entry](*args, **kwds)
    except KeyboardInterrupt:
        time.sleep(0.3)
        raise
    except Exception, e:
        e.traceback = traceback.format_exc()
        raise e

class Application(object):
    def __init__(self, instance_id, name, path, entry, queue, logger, environment=None, unstoppable=False, id=None):
        # basic Application properties
        self.instance_id = instance_id
        if not id:
            id = uuid.uuid4().hex
        self.id = id
        self.name = name
        self.entry = entry
        self.path = path
        self.queue = queue
        self.logger = logger
        self.status = 'stopped'
        self.environment = {}
        if environment:
            self.environment = environment
        self.unstoppable = unstoppable
        self.manager = AppManager(self)

    def get_status():
        if self.status == 'stopping' and not self.poll():
            self.status = 'stopped'
        return self.status
    
    def run(self):
        self.manager.daemon = True
        self.manager.start()
        # self.process = Process(target=runapp, args=(self.path, self.entry, self.logger, child, self.queue))
        # self.process.start()
        self.status = 'active'
        print 'STARTING APPLICATION', self.name, self.manager.num_processes, 'processes'
    
    def poll(self):
        return self.process.is_alive()
    
    def pause(self):
        if self.unstoppable:
            return
        self.manager.paused = True
        self.status = 'paused'
    
    @property
    def failed_items(self):
        return self.manager.failed_items
    
    def unpause(self):
        if self.unstoppable:
            return
        self.manager.paused = False
        self.status = 'active'
    
    def quit(self):
        if self.unstoppable:
            return
        self.manager.exit = True
        self.status = 'stopping'
    
    def force_quit(self, system_force=False):
        if self.unstoppable and not system_force:
            return
        # self.parent.send('exit')
        self.manager.exit = True
        for i in range(0, 4):
            if not self.poll():
                break
            time.sleep(1)
        else:
            self.process.terminate()
        self.status = 'stopped'
    
    def system_quit(self):
        return self.force_quit(system_force=True)
    
    @property
    def json_info(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'path' : self.path,
            'entry' : self.entry,
            'queue' : self.queue,
            'status' : self.status,
            'environment' : self.environment,
            'unstoppable' : self.unstoppable,
        }
    
    def queue_info(self, redis):
        success = redis.get(self.queue+':success')
        if success is None:
            success = 0
        return {
            'queued' : redis.llen(self.queue),
            'active' : redis.hlen(self.queue+':active')+redis.llen(self.queue+':pending'),
            'failed' : redis.llen(self.queue+':failed'),
            'success' : success,
        }

class AppManager(Thread):
    def __init__(self, application):
        Thread.__init__(self)
        self.application = application
        self.redis = Redis('localhost')
        self.lock = RLock()
        # state
        self.exit = False
        self.paused = False
        self.num_processes = cpu_count()
        self.pool = Pool(processes=self.num_processes, initializer=init_process, initargs=[self.application.path, self.application.environment])
        self.pending = []
    
    @property
    def queue(self):
        return self.application.queue
    
    @property
    def active_queue(self):
        return '%s:active' % self.queue
    
    @property
    def failed_queue(self):
        return '%s:failed' % self.queue

    @property
    def success_count(self):
        return '%s:success' % self.queue
    
    @property
    def pending_queue(self):
        return '%s:pending' % self.queue
    
    def poll(self):
        with self.lock:
            return len(self.pending) == 0 and self.exit
    
    def new_item(self):
        item = self.redis.brpoplpush(self.queue, self.pending_queue, 1)
        if item is None:
            return None
        pipe = self.redis.pipeline()
        pipe.hset(self.active_queue, item, self.application.instance_id)
        pipe.lrem(self.pending_queue, item, 1)
        pipe.execute()
        return item
    
    @property
    def failed_items(self):
        import json
        return [json.loads(x[5:]) for x in self.redis.lrange(self.failed_queue, 0, -1)]
    
    def clear_old(self):
        def handle_old(request, del_cmd):
            request_parsed = BaseRequest.from_serialized(request)
            response = request_parsed.response_class(request_parsed.response_queue, 'INCOMPLETE', None)
            pipe = self.redis.pipeline()
            pipe.lpush(self.failed_queue, response.serialize_failed_resp(request_parsed))
            del_cmd(pipe, request)
            pipe.execute()
        
        for request, v in self.redis.hgetall(self.active_queue).iteritems():
            if v != self.application.instance_id:
                continue
            handle_old(request, lambda pipe, k : pipe.hdel(self.active_queue, k))
        # this could /technically/ delete something pending, but the pending 
        # queue is used for a very short period of time and if the system is 
        # up long enough to delete the pending item it should be OK
        for request in self.redis.lrange(self.pending_queue, 0, -1):
            handle_old(request, lambda pipe, k : pipe.lrem(self.pending_queue, k, 1))
    
    def run(self):
        ResultWriter(self).start()
        with print_exc:
            self.clear_old()
        while True:
            if self.exit:
                break
            if self.paused:
                time.sleep(0.5)
                continue
            with self.lock:
                if len(self.pending) >= self.num_processes:
                    continue
            with print_exc:
                self.run_fun()
    
    def run_fun(self):
        if not self.queue:
            self.pending.append({
                'async' : self.pool.apply_async(worker_fun, [self.application.entry]),
                'request' : request,
            })
            return self.fun()
        
        # Get item
        request = self.new_item()
        if not request:
            return
        
        request = BaseRequest.from_serialized(request)
        
        # run fun
        kwds = {
            'entry' : self.application.entry,
            'args' : request.args,
            'kwds' : request.kwds,
            'format' : request.format,
        }
        # args = [self.application.entry]
        # args.extend([a for a in request.args])
        self.pending.append({
            'async' : self.pool.apply_async(worker_fun, kwds=kwds),
            'request' : request,
        })

class ResultWriter(Thread):
    daemon = True
    def __init__(self, manager):
        Thread.__init__(self)
        self.manager = manager
    
    def run(self):
        while True:
            if not self.check_pending():
                time.sleep(0.1)
    
    def check_pending(self):
        with self.manager.lock:
            for p in self.manager.pending:
                if not p['async'].ready():
                    continue
                break
            else:
                return False
            self.manager.pending = [x for x in self.manager.pending if x['request'].response_queue != p['request'].response_queue]
        try:
            request = p['request']
            ret = p['async'].get()
            response = request.response_class(request.response_queue, 'SUCCESS', ret)
            error = False
        except Exception, e:
            response = request.response_class(request.response_queue, 'ERROR', None)
            response.set_exception(e)
            error = True
        self.respond(request, response, error=error)
        return True
    
    def respond(self, request, response, error=False, retry=True):
        if not request.response_queue:
            print 'NO Q'
            return
        try:
            pipe = self.manager.redis.pipeline()
            pipe.lpush(request.response_queue, response.serialize_resp())
            pipe.expire(request.response_queue, request.timeout)
            if error:
                pipe.lpush(self.manager.failed_queue, response.serialize_failed_resp(request))
            else:
                pipe.incr(self.manager.success_count)
            pipe.hdel(self.manager.active_queue, request.raw)
            pipe.execute()
            time.sleep(1)
            # print >>sys.stderr, 'PUSHIN DATA', request.queue, request.response_queue, len(response.serialize_resp())
        except KeyboardInterrupt:
            if retry:
                self.respond(request, response, error=error, retry=False)
