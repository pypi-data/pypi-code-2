import json

from vogeler.exceptions import VogelerRunnerException
from vogeler.messaging import amqp

class VogelerRunner(object):
    def __init__(self, destination, **kwargs):
        try:
            self.routing_key = destination
            self.ch = amqp.setup_amqp(kwargs['host'], kwargs['username'], kwargs['password'])
        except:
            raise VogelerRunnerException("Unable to connect to %s as %s" % (kwargs['host'], kwargs['username']) )

    def message(self, message, durable=True):
        print "Vogeler(Runner) is sending a message"
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['deliver_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange, routing_key=self.routing_key)
        except:
            raise VogelerRunnerException("Unable to publish message: %s" % message)

    def close(self):
        self.ch.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
