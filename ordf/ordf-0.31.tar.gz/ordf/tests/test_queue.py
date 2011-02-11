from ordf.handler.queue import RabbitHandler
from ordf.handler import Handler, HandlerPlugin
from ordf.tests import our_test_graph
from time import sleep

class LoggingHandler(HandlerPlugin):
    def put(self, store):
        for ctx in store.contexts():
            print "recv graph", ctx.identifier

receiver = RabbitHandler(hostname="localhost", userid="guest", password="guest", exchange="ordf_test")
receiver.register_writer(LoggingHandler())

sender = Handler()

class TestClassRabbit(object):
    def test_01_connect_sender(self):
        sender.register_writer("rabbit", hostname="localhost", userid="guest", password="guest", exchange="ordf_test")
        sender.__writers__[0].connect()
        sleep(1)
    def test_02_connect_receiver(self):
        receiver.connect(queue="nosetests")
        sleep(1)
    def test_03_send(self):
        ctx = sender.context("test_rabbit", "test_rabbit")
        ctx.add(our_test_graph())
        ctx.commit()
    def test_10_close(self):
        sleep(1)
        receiver.close()
