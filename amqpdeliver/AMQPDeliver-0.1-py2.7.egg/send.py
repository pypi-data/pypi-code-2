#!/usr/bin/env python
import sys, uuid
from amqplib import client_0_8 as amqp
from optparse import OptionParser

DEFAULT_USERID = "guest"
DEFAULT_PASSWORD = "guest"
DEFAULT_VIRTUAL_HOST = "/"
DEFAULT_SERVER = "localhost"

def send(server,
         exchange,
         body,
         userid = DEFAULT_USERID,
         password = DEFAULT_PASSWORD,
         virtual_host = DEFAULT_VIRTUAL_HOST,
         message_id = None):
    conn = amqp.Connection(
        host=server,
        userid=userid,
        password=password,
        virtual_host=virtual_host,
        insist=False)
    chan = conn.channel()

    chan.exchange_declare(
        exchange=exchange,
        type="direct",
        durable=True,
        auto_delete=False)

    msg = amqp.Message(body)
    msg.properties["delivery_mode"] = 2
    msg.properties["message_id"] = message_id or str(uuid.uuid4())
    chan.basic_publish(msg,exchange=exchange)
    chan.close()
    conn.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    parser = OptionParser(usage="usage: %prog [options] exchange",
                          add_help_option=False)
    parser.add_option("-?", "--help", action="help")
    parser.add_option(
        "-h", "--host", dest="host",
        help="Connect to AMQP server on HOST",
        metavar="HOST",
        default=DEFAULT_SERVER)
    parser.add_option(
        "-P", "--port", dest="port",
        help="Connect to AMQP server on PORT",
        metavar="PORT",
        default="5672")
    parser.add_option(
        "-u", "--userid", dest="userid",
        help="Connect to AMQP server with userid USERID",
        metavar="USERID",
        default=DEFAULT_USERID)
    parser.add_option(
        "-p", "--password", dest="password",
        help="Connection to AMQP server with password PASSWORD",
        metavar="PASSWORD",
        default=DEFAULT_PASSWORD)
    parser.add_option(
        "-v", "--virtual-host", dest="virtual_host",
        help="Connect to the specified VIRTUAL-HOST",
        metavar="VIRTUAL-HOST",
        default=DEFAULT_VIRTUAL_HOST)

    (options, args) = parser.parse_args(args=argv[1:])
    if len(args) != 1:
        parser.error("Exactly one argument is required: the exchange name")
        return 1

    send(server = '%s:%s'%(options.host, options.port),
         exchange = args[0],
         body = sys.stdin.read(),
         userid = options.userid,
         password = options.password,
         virtual_host = options.virtual_host)

    return 0

if __name__ == "__main__":
    sys.exit(main())

