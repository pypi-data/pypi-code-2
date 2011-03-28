#!/usr/bin/env python
try:
    import json
except ImportError:
    import simplejson as json

from uuid import uuid4
gen_uuid = lambda : unicode(uuid4())

import amqplib.client_0_8 as amqp

from quebert import common as qc

HIGH = u"high"
MEDIUM = u"medium"
LOW = u"low"

class AMQPBus(object):
    def __init__(self, host, username, password, exchange):
        self.conn = amqp.Connection(host, userid=username, password=password)
        self.ch = self.conn.channel()
        self.ch.exchange_declare(exchange, type='topic', auto_delete=False, durable=True)
        self.exchange = exchange

    def sendto(self, body, key):
        msg = amqp.Message(body, delivery_mode=2)
        self.ch.basic_publish(msg, self.exchange, routing_key=key)

    def close(self):
        self.ch.close()
        self.conn.close()

def add_task(url, params=None, kind="tasks", ttl=0, run_at=None, uuid=None,
             priority=MEDIUM, encode=json.dumps, meta_encode=json.dumps,
             **kw):
    """
    Synchronously add a task to the queue for execution.

    The message itself is composed of the metadata associated and the body.

    @param url: The url that should be called to execute the task
    @type url: C{str}

    @param params: The parameters that should be passed in the request
    @type params: Anything encodable in your format

    @param kind: The base name of routing parameter for this task.
    @type kind: C{str}

    @param ttl: The ttl, in seconds, for the current task, after which the
                 task is discarded.
    @type ttl: C{int}, seconds.

    @param run_at: A C{datetime.datetime} object in UTC timezone of when
                    this task should run. Only supported if your Watcher
                    supports it.
    @type run_at: C{datetime.datetime}

    @param uuid: A unique identifier for the task at hand, you can supply
                 one when the task is queued or you can rely on the system
                 to create one for you.
    @type uuid: C{unicode}

    @param priority: The priority of the current task, it's used with the
                      kind to create the routing key for the queue.
    @type priority: C{str}, can be L{HIGH}, L{MEDIUM} or L{LOW}

    @param encode: Your format encoder, by default it's JSON
    @type encode: function that takes objects and returns encoded strings.

    @param meta_encode: The encoding format used by Quebert and that
                        the mediator expects.
    @type meta_encode: function that takes objects and returns encoded strings.

    @param kw: Extra metadata that you want to add to the base package.
    """
    if params is None:
        params = {}
    uuid = uuid or gen_uuid()
    payload = {'url': url,
               'params': encode(params),
               'timestamp': qc.now_serialized(),
               'ttl': ttl,
               'uuid': uuid}
    if run_at is not None:
        payload['run_at'] = qc.serialize_date(run_at)
    rmq_username = kw.pop("rmq_username", "guest")
    rmq_password = kw.pop("rmq_password", "guest")
    rmq_host = kw.pop("rmq_host", "localhost")
    rmq_exchange = kw.pop("rmq_exchange", "flow")
    payload.update(kw)
    add_raw_task(meta_encode(payload), kind, priority,
                 rmq_username, rmq_password, rmq_host,
                 rmq_exchange)
    return uuid

def add_raw_task(body, kind="tasks", priority=MEDIUM,
                 user="guest", pwd="guest", host="localhost",
                 exchange="flow"):
    """
    Synchronously add a raw task body to the queue. You must
    make sure that this body is actually sane.

    @param body: The encoded body of a task
    @type body: C{str}

    @param kind: The base name of routing parameter for this task.
    @type kind: C{str}

    @param priority: The priority of the current task, it's used with the
                      kind to create the routing key for the queue.
    @type priority: C{str}, can be L{HIGH}, L{MEDIUM} or L{LOW}
    """
    bus = AMQPBus(host, user, pwd, exchange)
    bus.sendto(body, ".".join([kind, priority]))
    bus.close()
