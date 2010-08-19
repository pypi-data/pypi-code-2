"""
.. autoclass:: OperationalError
    :show-inheritance:
.. autoclass:: AMQPCTL
"""

from amqplib.client_0_8.connection import Connection
from amqplib.client_0_8.channel import Channel
from amqplib.client_0_8.exceptions import AMQPChannelException
from optparse import OptionParser
import logging

class OperationalError(Exception):
    """
    Raised when invalid command is given by the user"
    """

class AMQPCTL(object):
    """
    This is the command line class. It reads arguments using the standard
    python :class:optparse.OptionParser and uses `py-amqplib`_ to connect
    to an AMQP Server.

    The various methods in this class might serve as useful examples of
    `py-amqplib`_ usage.

    .. _py-amqplib: http://code.google.com/p/py-amqplib/

    .. automethod:: connect
    .. automethod:: check_exchange
    .. automethod:: declare_exchange
    .. automethod:: delete_exchange
    .. automethod:: check_queue
    .. automethod:: declare_queue
    .. automethod:: delete_queue
    .. automethod:: purge_queue
    """
    parser = OptionParser()
    parser.add_option("-s", "--server",
                      dest="server",
                      default="localhost",
                      help="Hostname of the AMQP Server")
    parser.add_option("-u", "--username",
                      dest="username",
                      default="guest",
                      help="Username (default: guest)")
    parser.add_option("-p", "--password",
                      dest="password",
                      default="guest",
                      help="Password (default: guest)")
    parser.add_option("--quiet",
                      dest="quiet",
                      default=False,
                      action="store_true",
                      help="No verbose output")
    parser.add_option("-e", "--exchange",
                      dest="exchange",
                      default="test_exchange",
                      help="Exchange Name (default: test_exchange)")
    parser.add_option("-t", "--type",
                      dest="exchange_type",
                      default="direct",
                      help="Type of Exchange (direct or fanout)")
    parser.add_option("--durable",
                      dest="durable",
                      default=False,
                      action="store_true",
                      help="Declare queues and exchanges durable")
    parser.add_option("-q", "--queue",
                      dest="queue",
                      default="test_queue",
                      help="Queue Name (default: test_queue)")
    parser.add_option("--exclusive",
                      dest="exclusive",
                      default=False,
                      action="store_true",
                      help="Declare queues as exclusive")
    parser.add_option("--declare-exchange",
                      dest="declare_exchange",
                      default=False,
                      action="store_true",
                      help="Declare the exchange")
    parser.add_option("--delete-exchange",
                      dest="delete_exchange",
                      default=False,
                      action="store_true",
                      help="Delete the exchange")
    parser.add_option("--declare-queue",
                      dest="declare_queue",
                      default=False,
                      action="store_true",
                      help="Declare the queue")
    parser.add_option("--delete-queue",
                      dest="delete_queue",
                      default=False,
                      action="store_true",
                      help="Delete the queue")
    parser.add_option("--purge-queue",
                      dest="purge_queue",
                      default=False,
                      action="store_true",
                      help="Purge messages from the queue")

    def __init__(self):
        self.options, self.args = self.parser.parse_args()
        log_cfg = {
            "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
            }
        if self.options.quiet:
            log_cfg["level"] = logging.DEBUG
        else:
            log_cfg["level"] = logging.INFO
        logging.basicConfig(**log_cfg)
        self.log = logging.getLogger(__name__)

    def command(self):
        self.connect()
        if self.options.delete_exchange:
            if self.check_exchange():
                self.delete_exchange()
            else:
                self.log.info("No such exchange, nothing to delete")
        if self.options.declare_exchange:
            if self.check_exchange():
                self.log.info("Exchange already exists, delete it first")
            else:
                self.declare_exchange()
        if self.options.delete_queue:
            if self.check_exchange():
                self.delete_queue()
            else:
                self.log.info("No such queue, nothing to delete")
        if self.options.declare_queue:
            if self.check_queue():
                self.log.info("Queue already exists, delete it first")
            else:
                self.declare_queue()
        if self.options.purge_queue:
            if self.check_queue():
                self.purge_queue()
            else:
                self.log.info("No such queue")

    def connect(self):
        """
        Connect to the AMQP Server. The connection object wants the server's
        coordinates and the user credentials. Interaction with the server is
        actually done with a :class:`amqplib.client_0_8.channel.Channel` object.
        """
        self.log.info("Connecting: %s@%s" % (self.options.username, self.options.server))
        self.connection = Connection(
            hostname=self.options.server,
            userid=self.options.username,
            password=self.options.password
            )

    def check_exchange(self):
        """
        Check to see if exchange exists
        """
        try:
            channel = Channel(self.connection)
            channel.exchange_declare(
                self.options.exchange,
                self.options.exchange_type,
                passive=True,
                )
            return True
        except AMQPChannelException:
            return False
            
    def declare_exchange(self):
        """
        Declare an exchange
        """
        self.log.info("Declaring exchange: %s type: %s durable: %s" % (
            self.options.exchange,
            self.options.exchange_type,
            self.options.durable
            ))
        channel = Channel(self.connection)
        channel.exchange_declare(
            self.options.exchange,
            self.options.exchange_type,
            passive=False,
            durable=self.options.durable
            )

    def delete_exchange(self):
        """
        Delete an exchange
        """
        self.log.info("Deleting exchange: %s" % (self.options.exchange,))
        channel = Channel(self.connection)
        channel.exchange_delete(self.options.exchange)


    def check_queue(self):
        """
        Check to see if queue exists
        """
        try:
            channel = Channel(self.connection)
            channel.queue_declare(
                self.options.queue,
                passive=True
                )
            return True
        except AMQPChannelException:
            return False
            

    def declare_queue(self):
        """
        Declare a queue
        """
        self.log.info("Declaring queue: %s durable: %s exclusive: %s" % (
            self.options.queue,
            self.options.durable,
            self.options.exclusive
            ))
        channel = Channel(self.connection)
        channel.queue_declare(
            self.options.queue,
            passive=False,
            durable=self.options.durable,
            exclusive=self.options.exclusive
            )

    def delete_queue(self):
        """
        Delete a queue
        """
        self.log.info("Deleting queue: %s" % (self.options.queue,))
        channel = Channel(self.connection)
        channel.queue_delete(self.options.queue)

    def purge_queue(self):
        """
        Purge a queue
        """
        self.log.info("Purging queue: %s" % (self.options.queue,))
        channel = Channel(self.connection)
        channel.queue_purge(self.options.queue)

def amqpctl():
    AMQPCTL().command()
