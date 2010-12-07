from amqplib import client_0_8 as amqp

class AMQPLogger(object):
    def __init__(self, host, user, password, vhost="/", exchange="analytics"):
        self.exchange = exchange

        self.conn = amqp.Connection(
            host = host,
            userid = user,
            password = password,
            virtual_host = vhost,
            insist = False)

        self.chan = self.conn.channel()

    def write(self, line):
        msg = amqp.Message(line)
        self.chan.basic_publish(msg, exchange=self.exchange)

class AMQPWorker(object):
    exchange_name = "analytics"
    queue_name = "analytics_logger"
    consumer_tag = "analytics_Worker"

    def __init__(self, logger, amqp_host, amqp_user, amqp_password, amqp_vhost="/"):
        self.logger = logger

        self.conn = amqp.Connection(
            host = amqp_host,
            userid = amqp_user,
            password = amqp_password,
            virtual_host = amqp_vhost,
            insist = False)

        self.chan = self.conn.channel()
        self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)
        self.chan.exchange_declare(exchange=self.exchange_name, type="fanout", durable=True, auto_delete=False)
        self.chan.queue_bind(queue=self.queue_name, exchange=self.exchange_name)

    def work(self):
        self.chan.basic_consume(queue=self.queue_name, no_ack=False, callback=self._msg_callback, consumer_tag=self.consumer_tag)
        while True:
            try:
                self.chan.wait()
            except KeyboardInterrupt:
                return
        self.chan.basic_cancel(self.consumer_tag)

    def _msg_callback(self, msg):
        self.logger.write(msg.body)
        self.chan.basic_ack(msg.delivery_tag)
