#!/usr/bin/env python
from amqplib import client_0_8 as amqp
from optparse import OptionParser
import ConfigParser, os, socket, syslog, uuid, sys, errno, pwd, grp

DEFAULT_USERID = "guest"
DEFAULT_PASSWORD = "guest"
DEFAULT_VIRTUAL_HOST = "/"
CONFIG_SECTION = "exchange"

def remove_empty(fname):
    empty = os.stat(fname).st_size == 0
    if empty:
        os.remove(fname)
    return empty

class Receive:
    def __init__(
        self,
        server,
        userid = DEFAULT_USERID,
        password = DEFAULT_PASSWORD,
        virtual_host = DEFAULT_VIRTUAL_HOST):

        self.server = server
        self.virtual_host = virtual_host

        self.conn = amqp.Connection(
            host=server,
            userid=userid,
            password=password,
            virtual_host=virtual_host,
            insist=False)
        self.chan = self.conn.channel()

    def add_exchange(
        self,
        exchange,
        command_path,
        command_argv,
        user,
        queue = None):

        if not queue:
            queue='%s-%s'%(socket.gethostname(), exchange)
        self.consumer_tag = '%s-receive_d' % queue

        self.chan.exchange_declare(
            exchange=exchange,
            type="direct",
            durable=True,
            auto_delete=False)

        self.chan.queue_declare(
            queue=queue,
            durable=True,
            exclusive=False,
            auto_delete=False)

        self.chan.queue_bind(
            queue=queue,
            exchange=exchange)

        spooldir = "/var/tmp/amqp-deliver/%s/messages" % exchange
        uid, gid = pwd.getpwnam(user)[2:4]
        groups = [group.gr_gid for group in grp.getgrall() if user in group.gr_mem]

        if not(os.path.isdir(spooldir)):
            os.makedirs(spooldir)

        def fname(tag, type):
            return "%s/%s.%s" % (spooldir, tag, type)

        def wait_log(pid, tag, msg):
            while True:
                try:
                    pid1, status = os.waitpid(pid, 0)
                    if not(remove_empty(fname(tag, 'stderr')) and
                           remove_empty(fname(tag, 'stdout'))) or status:
                        # If the return result is not an error, or if
                        # There is anything in the log files, then save
                        # the message
                        syslog.syslog(
                            syslog.LOG_ERR,
                            'exchange: %s: child process for %s produced output' % (exchange, tag))
                        msgout = open(fname(tag, 'msg'), 'w')
                        msgout.write(msg.body)
                        msgout.close()

                    if status:
                        syslog.syslog(
                            syslog.LOG_ERR,
                            'exchange: %s: child process for %s exited with status %s'
                            % (exchange, tag, str(status)))
                        return False
                    else:
                        return True
                except OSError, e:
                    # for interrupted system calls, wait again
                    if e.errno != errno.EINTR:
                        syslog.syslog(
                            syslog.LOG_ERR, "error waiting for child to exit: %s" %
                            errno.errorcode[e.errno])
                        raise e

        def received(msg):
            tag = uuid.uuid4()
            syslog.syslog(
                syslog.LOG_DEBUG,
                'exchange: %s: received %s length %i' % (exchange, tag, len(msg.body)))
            msgfname = fname(tag, 'msg')
            outfname = fname(tag, 'stdout')
            errfname = fname(tag, 'stderr')

            message_r, message_w = os.pipe()

            pid = os.fork()
            if pid > 0:
                try:
                    os.close(message_r)
                    data = msg.body
                    while len(data):
                        data = data[os.write(message_w, data):]
                except OSError, e:
                    syslog.syslog(
                        syslog.LOG_ERR, "error waiting for child to exit: %s"
                        % errno.errorcode[e.errno])
                finally:
                    os.close(message_w)

                if wait_log(pid, tag, msg):
                    self.chan.basic_ack(msg.delivery_tag)
            else:
                try:
                    env = {}
                    env.update(os.environ)
                    env.update({
                        'AMQP_EXCHANGE': exchange,
                        'AMQP_VIRTUAL_HOST': self.virtual_host,
                        'AMQP_SERVER': self.server
                        })
                    os.close(message_w)
                    os.dup2(message_r, 0)
                    os.dup2(os.open(fname(tag, 'stdout'), os.O_WRONLY|os.O_APPEND|os.O_CREAT), 1)
                    os.dup2(os.open(fname(tag, 'stderr'), os.O_WRONLY|os.O_APPEND|os.O_CREAT), 2)
                    if gid not in groups:
                        groups.append(gid)
                    os.setgid(gid);
                    os.setuid(uid);

                    # setgroup doesn't work if we are not root, so don't call
                    # it if we don't need to.
                    if set(os.getgroups()) != set(groups):
                        os.setgroups(groups)

                    os.execve(command_path, command_argv, env)
                except OSError, e:
                    syslog.syslog(
                        syslog.LOG_ERR, "error executing command: %s"
                        % errno.errorcode[e.errno])
                    sys.exit(e.errno)
                # should not get here
                sys.exit(1)

        self.chan.basic_consume(
            queue=queue,
            callback=received,
            consumer_tag=self.consumer_tag)

    def wait(self):
        self.chan.wait()

    def close(self):
        self.chan.basic_cancel(self.consumer_tag)

def main(args=None):
    parser = OptionParser(
        usage="usage: %prog [options] exchange-config*",
        add_help_option=False)
    parser.add_option("-?", "--help", action="help")
    parser.add_option(
        "-h", "--host", dest="host",
        help="Connect to AMQP server on HOST",
        metavar="HOST",
        default="localhost")
    parser.add_option(
        "-P", "--port", dest="port",
        help="Connect to AMQP server on PORT",
        metavar="PORT",
        default="5672")
    parser.add_option(
        "-i", "--amqp-userid", dest="userid",
        help="Connect to AMQP server with userid USERID",
        metavar="USERID",
        default=DEFAULT_USERID)
    parser.add_option(
        "-p", "--amqp-password", dest="password",
        help="Connection to AMQP server with password PASSWORD",
        metavar="PASSWORD",
        default=DEFAULT_PASSWORD)
    (options, args) = parser.parse_args()

    server = '%s:%s'%(options.host, options.port)
    receive = Receive(
        server,
        userid = options.userid,
        password = options.password)

    for configfile in args:
        config = ConfigParser.ConfigParser()
        config.read(configfile)
        receive.add_exchange(
            config.get(CONFIG_SECTION, 'exchange'),
            config.get(CONFIG_SECTION, 'exec'),
            config.get(CONFIG_SECTION, 'argv').split(' '),
            config.get(CONFIG_SECTION, 'user'),
            config.get(CONFIG_SECTION, 'queue'))

    try:
        while True:
            receive.wait()
    finally:
        receive.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())

