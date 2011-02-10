
from kombu import BrokerConnection, Exchange, Queue, Consumer, Producer

class KombuLogger(object):
    def __init__(self, host="localhost", user="guest", password="guest", vhost="/", exchange="analytics"):
        self.connection = BrokerConnection(host, user, password, vhost)
        self.channel = self.connection.channel()
        self.exchange = Exchange(exchange, "topic", durable=True, auto_delete=False)
        self.producer = Producer(self.channel, exchange=self.exchange, serializer="json")
    
    def write(self, event, timestamp, attributes):
        self.producer.publish({"event": event, "ts": timestamp, "attr": attributes}, routing_key=event)

class KombuConsumer(KombuLogger):
    def __init__(self, logger, eventspec="#", queue="analytics.logger", **kwargs):
        super(KombuConsumer, self).__init__(**kwargs)
        self.logger = logger
        self.queue = Queue(queue, exchange=self.exchange, routing_key=eventspec, auto_delete=False, durable=True, exclusive=False)
    
    def run(self):
        consumer = Consumer(self.channel, self.queue, callbacks=[self.handle_message])
        consumer.consume()
        while True:
            try:
                self.connection.drain_events()
            except KeyboardInterrupt:
                return
    
    def handle_message(self, body, message):
        self.logger.write(body["event"], body["ts"], body["attr"])
        message.ack()
