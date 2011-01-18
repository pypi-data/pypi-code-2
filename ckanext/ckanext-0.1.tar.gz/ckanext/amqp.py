from pprint import pformat
from traceback import format_exc
try:
    from json import dumps
except ImportError:
    from simplejson import dumps
import subprocess
from carrot.messaging import Consumer, Publisher
from carrot.connection import BrokerConnection
from ckanext.command import Command

log = __import__("logging").getLogger("amqp_listener")

class Listener(Command):
    usage = "Usage: %prog [options]"
    parser = Command.StandardParser(usage=usage)
    parser.add_option("-s", "--server",
                      dest="server",
                      help="Hostname of the AMQP Server (default: localhost)")
    parser.add_option("-u", "--username",
                      dest="username",
                      help="Username (default: guest)")
    parser.add_option("-p", "--password",
                      dest="password",
                      help="Password (default: guest)")
    parser.add_option("-e", "--exchange",
                      dest="exchange",
                      help="Exchange Name")
    parser.add_option("-t", "--type",
                      dest="exchange_type",
                      help="Type of Exchange (direct, topic or fanout)")
    parser.add_option("-q", "--queue",
                      dest="queue",
                      help="Queue Name")
    parser.add_option("-k", "--routing-key",
                      dest="routing_key",
                      help="Routing Key")
    parser.add_option("--durable",
                      dest="durable",
                      action="store_true",
                      help="Declare queues and exchanges durable")
    parser.add_option("--exclusive",
                      dest="exclusive",
                      action="store_true",
                      help="Declare queues as exclusive")

    defaults = {
        "server": "localhost",
        "username": "guest",
        "password": "guest",
        "exchange": "fnord.ckan.net",
        "exchange_type": "topic",
        "queue": "amqp_listener",
        "routing_key": "#",
        "durable": False,
        "exclusive": False,
        }
    def cfgvar(self, name):
        cmdopt = getattr(self.options, name)
        if cmdopt is None:
            cmdopt = self.config.get(name, self.defaults.get(name))
        return cmdopt
    
    @property
    def connection(self):
        kw = {
            "hostname": self.cfgvar("server"),
            "userid": self.cfgvar("username"),
            "password": self.cfgvar("password"),
            }
        log.info("Connecting to AMQP Server %(userid)s@%(hostname)s" % kw)
        return BrokerConnection(**kw)

    @property
    def consumer(self):
        kw = {
            "exchange": self.cfgvar("exchange"),
            "exchange_type": self.cfgvar("exchange_type"),
            "queue": self.cfgvar("queue"),
            "durable": self.cfgvar("durable"),
            "exclusive": self.cfgvar("exclusive"),
            }
        if kw["exchange_type"] is not "fanout":
            kw["routing_key"] = self.cfgvar("routing_key")

        connection = self.connection
        log.info("Binding %(queue)s@%(exchange)s" % kw)
        return Consumer(connection=connection, **kw)
    
    def command(self):
        consumer = self.consumer
        consumer.register_callback(self._process)

        log.info("Waiting for messages")
        for _unused in consumer.iterconsume():
            pass

    def _process(self, content, message):
        log.debug("Received:\n%s" % pformat(content))
        try:
            retcode = self.process(content, message)
            if not retcode:
                message.ack()
        except:
            log.error("Exception:\n%s" % format_exc())

    def process(self, content, message):
        data = dumps(content)
        proc = subprocess.Popen(self.args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.stdin.write(data)
        proc.stdin.close()
        proc.stdin = None
        stdout, stderr = proc.communicate()
        log = __import__("logging").getLogger("amqp_child")
        if stderr:
            log.warn(stderr)
        if stdout:
            log.info(stdout)
        retcode = proc.wait()
        if retcode != 0:
            log.warn("Command [%s] exit status %d" % (self.args[0], retcode))
        return retcode
                     

def listener():
    Listener().command()
