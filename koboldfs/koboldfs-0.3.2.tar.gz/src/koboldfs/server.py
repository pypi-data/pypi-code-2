# koboldfs
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import sys
import time
import shutil
import struct
import socket
import signal
import random
import asyncore
import optparse
import operator
import string
import tempfile
import threading

import logging
import logging.handlers

from ConfigParser import ConfigParser
from datetime import datetime

from sqlalchemy import and_, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from koboldfs import protocol
from koboldfs.client import Client
from koboldfs.models import Base, File, Domain, Replica, Server, ServerDomain

try:
    from hashlib import md5
except:                         #pragma NO COVER
    from md5 import md5         #pragma NO COVER


STATE_WAITING = 0
STATE_COMMAND = 1
STATE_ARGUMENT_SIZE = 2
STATE_ARGUMENT_VALUE = 3
STATE_EXECUTE = 4
STATE_RECEIVE_FILE_SIZE = 5
STATE_RECEIVE_FILE_CONTENT = 6
STATE_RECEIVE_FILE_CHECKSUM = 7


class ServerChannel(asyncore.dispatcher):
    """Channel dispatcher"""

    def __init__(self, channel, options, session, logger):
        self._options = options
        self._session = session
        self._logger = logger
        self._buffer = ''
        self._ibuffer = ''
        self._pending = {}
        self._reset()
        asyncore.dispatcher.__init__(self, channel)

    def _reset(self, status=None):
        self._status = STATE_WAITING
        self._command = None
        self._arguments = []
        self._arguments_number = None
        self._arguments_position = None
        self._size = None
        self._output = None
        self._output_domain = None
        self._output_key = None
        self._output_filename = None
        self._output_size = None
        self._output_md5 = None
        if status is not None:
            self._buffer += status

    def log_info(self, message, type='info'):
        if type in ('error', 'warning'):
            self._logger.error('(%s:%s) - %s ' % \
                (self.addr[0], self.addr[1], message))
        else:
            self._logger.debug('(%s:%s) - %s ' % \
                (self.addr[0], self.addr[1], message))

    def handle_error(self):
        nil, t, v, tbinfo = asyncore.compact_traceback()
        self_repr = repr(self)
        self.log_info('Python exception, closing channel %s (%s:%s %s)' % \
            (self_repr, t, v, tbinfo), 'error')
        self.handle_close()

    def writable(self):
        return len(self._buffer) > 0

    def handle_close(self):
        self._session.close()
        self.connected = False
        self.abort()
        self.close()
        self.log_info('Closed connection.')

    def handle_write(self):
        sent = self.send(self._buffer)
        self._buffer = self._buffer[sent:]

    def handle_read(self):
        data = self._ibuffer
        # read from the socket
        try:
            data += self.recv(protocol.BLOCKSIZE)
        except socket.error, exception:
            self.handle_error()
            return
        # if the socket is not connected, skip the data
        if not self.connected:
            return
        # receiving a file (size)
        elif self._status == STATE_RECEIVE_FILE_SIZE and len(data) >= 4:
            self._size = struct.unpack('I', data[:4])[0]
            self._status = STATE_RECEIVE_FILE_CONTENT
            data = data[4:]
        # receiving a file (content)
        if self._status == STATE_RECEIVE_FILE_CONTENT and len(data) >= 1:
            remaining = self._size - self._output_size
            content = data[:remaining]
            self._output.write(content)
            self._output_size += len(content)
            self._output_md5.update(content)
            data = data[remaining:]
            if self._output_size == self._size:
                self._status = STATE_RECEIVE_FILE_CHECKSUM
        # receiving a file (checksum)
        if self._status == STATE_RECEIVE_FILE_CHECKSUM and len(data) >= 32:
            checksum = data[:32]
            data = data[32:]
            self.handle_cmd_put_completed(checksum)
        # command
        if self._status == STATE_WAITING and len(data) >= 1:
            self._command = data[0]
            self._status = STATE_COMMAND
            data = data[1:]
        # number of parameters
        if self._status == STATE_COMMAND and len(data) >= 1:
            self._arguments_number = struct.unpack('B', data[0])[0]
            self._arguments_position = 0
            self._status = STATE_ARGUMENT_SIZE
            data = data[1:]
        # loop on the parameters
        while self._status in (STATE_ARGUMENT_SIZE, STATE_ARGUMENT_VALUE) and \
              len(self._arguments) < self._arguments_number:
            # argument size
            if self._status == STATE_ARGUMENT_SIZE and len(data) >= 4:
                self._size = struct.unpack('I', data[:4])[0]
                self._status = STATE_ARGUMENT_VALUE
                data = data[4:]
            # argument value
            elif self._status == STATE_ARGUMENT_VALUE and \
                 len(data) >= self._size:
                self._arguments.append(data[:self._size])
                self._status = \
                    len(self._arguments) < self._arguments_number and \
                    STATE_ARGUMENT_SIZE or STATE_EXECUTE
                data = data[self._size:]
            # not enough data to continue
            else: break
        # update the input buffer
        self._ibuffer = data
        # not enough data to continue
        if self._status in (STATE_ARGUMENT_SIZE, STATE_ARGUMENT_VALUE) and \
           len(self._arguments) == self._arguments_number:
            self._status = STATE_EXECUTE
        # execute the commands
        if self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_PING:
            self.handle_cmd_ping(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_PUT:
            self.handle_cmd_put(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_GET:
            self.handle_cmd_get(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_GET_URL:
            self.handle_cmd_get_url(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_DELETE:
            self.handle_cmd_delete(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_PREPARE:
            self.handle_cmd_prepare(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_COMMIT:
            self.handle_cmd_commit(self._arguments)
        elif self._status == STATE_EXECUTE and \
           self._command == protocol.CMD_ABORT:
            self.handle_cmd_abort(self._arguments)
        elif self._status == STATE_EXECUTE:
            self._reset(protocol.RES_ERR_COMMAND)

    def handle_cmd_ping(self, arguments):
        # log the request
        self.log_info('PING')
        # reply to the request
        self._reset(protocol.RES_OK)

    def handle_cmd_put(self, arguments):
        # log the request
        self.log_info('PUT (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self._options.domains.get(domain)
        if domain is None:
            self._reset(protocol.RES_ERR_DOMAIN)
            return
        # prepare the system to receive the file from the client
        self._status = STATE_RECEIVE_FILE_SIZE
        self._output_domain = domain
        self._output_key = key
        self._output_filename = tempfile.mktemp(
            prefix='koboldfs-', dir=self._options.tmp)
        self._output = open(self._output_filename, 'wb')
        self._output_size = 0
        self._output_md5 = md5()
        self._buffer += protocol.RES_WAITING

    def _filename(self, domain, key, checksum, url=False):
        parts = not url and [self._options.data, domain[2]] or []
        parts.extend((
            checksum[0:2],
            checksum[2:4],
            checksum[4:6],
            checksum[6:8],
            checksum[8:12],
            checksum[12:16],
            checksum[16:24],
            checksum[24:32],
        ))
        parts.append(key)
        return not url and os.path.join(*parts) or '/'.join(parts)

    def handle_cmd_put_completed(self, checksum):
        # log the request
        self.log_info('PUT_COMPLETED (%s, %s)' % \
            (self._output_domain[1], self._output_key))
        # database connection and cursor: look-up the file by file id
        session = self._session
        # the upload is successful
        self._output.close()
        if checksum == self._output_md5.hexdigest():
            filename = self._filename(self._output_domain,
                self._output_key, checksum)
            # database connection and cursor: look-up the file by key
            file = session.query(File).filter_by(
                domain_id=self._output_domain[0],
                key=self._output_key.decode('utf-8'), status=u'R').first()
            # if a different file with the same key already exists, delete it
            if file is not None and file.checksum != checksum:
                file.status = u'D'
                file.deleted_on = datetime.now()
            # move the file and register it into the database
            if file is None or file.checksum != checksum:
                file = File(domain_id=self._output_domain[0], replicas=1,
                    key=self._output_key.decode('utf-8'), status=u'R',
                    bytes=self._output_size, checksum=checksum)
                session.add(file)
                replica = Replica(file=file, server_id=self._options.server_id)
                session.add(replica)
                # add the file to the list of pending changes
                self._pending[file.key] = (self._output_filename, filename)
            # file already exist, remove the temporary file
            else:
                os.unlink(self._output_filename)
            self._reset(protocol.RES_OK)
        # the upload is NOT successful
        else:
            self._reset(protocol.RES_KO)

    def handle_cmd_get(self, arguments):
        # log the request
        self.log_info('GET (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self._options.domains.get(domain)
        if domain is None:
            self._reset(protocol.RES_ERR_DOMAIN)
            return
        # database connection and cursor: look-up the file by key
        session = self._session
        file = session.query(File).filter_by(domain_id=domain[0],
            key=key.decode('utf-8'), status=u'R').first()
        # if the file does not exist, return error
        if file is None:
            self._reset(protocol.RES_ERR_NOTFOUND)
            return
        # get the filename, checking the pending changes
        if file.key in self._pending:
            filename = self._pending[file.key][0]
        else:
            filename = self._filename(domain, file.key, file.checksum)
        # if we don't have the file on the file system, get it from the network
        if not os.path.isfile(filename):
            # get the list of servers we can find the file on
            servers = list(session.query(Server).filter(and_(
                Replica.file_id == file.id, Replica.server_id == Server.id,
                Server.id <> self._options.server_id, Server.status == u'Y',
            )).order_by('RANDOM()'))
            # if we do not have servers to take the file from, return
            if not servers:
                self._reset(protocol.RES_ERR_NOTFOUND)
            # send the redirect command reset the status
            else:
                host = servers[0].host.encode('utf-8')
                self.log_info('REDIRECT (%s)' % host)
                self._buffer += (protocol.RES_REDIRECT + struct.pack('I',
                    len(host)) + host)
                self._reset()
        # send the file content to the client
        else:
            source = open(filename, 'rb')
            source.seek(0, 2)
            size = source.tell()
            source.seek(0)
            self._buffer += (protocol.RES_TRANSFER + struct.pack('I', size))
            while True:
                data = source.read(protocol.BLOCKSIZE)
                if not data:
                    break
                self._buffer += data
            # send the file checksum and reset the status
            source.close()
            self._buffer += file.checksum.encode('utf-8')
            self._reset()

    def handle_cmd_get_url(self, arguments):
        # log the request
        self.log_info('GET_URL (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self._options.domains.get(domain)
        if domain is None:
            self._reset(protocol.RES_ERR_DOMAIN)
            return
        # database connection and cursor: look-up the file by key
        session = self._session
        options = list(session.query(File.key, File.checksum, Server.name,
            ).filter(and_(
                File.id == Replica.file_id, Replica.server_id == Server.id,
                File.domain_id == domain[0], File.key == key.decode('utf-8'),
                File.status == u'R', Server.status == u'Y')))
        # if the file does not exist, return error
        if not options:
            self._reset(protocol.RES_ERR_NOTFOUND)
            return
        # choose a random replica, and return the URL
        replica = random.choice(options)
        filename = self._filename(domain, replica[0], replica[1], url=True)
        url = domain[3] % {
            'filename': filename, 'domain': domain[1], 'server': replica[2],
        }
        url = url.encode('utf-8')
        # reset the status
        self._buffer += protocol.RES_TRANSFER + \
            struct.pack('I', len(url)) + url
        self._reset()

    def handle_cmd_delete(self, arguments):
        # log the request
        self.log_info('DELETE (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self._options.domains.get(domain)
        if domain is None:
            self._reset(protocol.RES_ERR_DOMAIN)
            return
        # database connection and cursor: look-up the file by key
        session = self._session
        file = session.query(File).filter_by(domain_id=domain[0],
            key=key.decode('utf-8'), status=u'R').first()
        # if the file does not exist, return an error
        if file is None:
            self._reset(protocol.RES_ERR_NOTFOUND)
            return
        # remove the file
        file.status = u'D'
        file.deleted_on = datetime.now()
        # reset the status
        self._reset(protocol.RES_OK)

    def handle_cmd_prepare(self, arguments):
        # log the request
        self.log_info('PREPARE')
        # reply to the request
        try:
            self._session.prepare()
        except SQLAlchemyError:
            self._reset(protocol.RES_KO)
        else:
            self._reset(protocol.RES_OK)

    def handle_cmd_commit(self, arguments):
        # log the request
        self.log_info('COMMIT')
        # move the pending files to the right position
        for key in self._pending.keys():
            filename, target = self._pending[key]
            directory = os.path.split(target)[0]
            if not os.path.isdir(directory):
                os.makedirs(directory)
            shutil.move(filename, target)
        # commit the transaction
        self._session.commit()
        # reply to the request
        self._pending = {}
        self._reset(protocol.RES_OK)

    def abort(self):
        # remove the pending files from the filesystem
        for key in self._pending.keys():
            filename, target = self._pending[key]
            os.unlink(filename)
        # rollback the transaction
        self._session.rollback()
        # reset the status
        self._pending = {}

    def handle_cmd_abort(self, arguments):
        # log the request
        self.log_info('ABORT')
        self.abort()
        # reply to the request
        self._reset(protocol.RES_OK)


class ServerDispatcher(asyncore.dispatcher):
    """Server network dispatcher"""

    def __init__(self, server):
        asyncore.dispatcher.__init__(self)
        self._options = server.options
        self._logger = server.logger
        self._session = server.session
        self._server = server

    def handle_accept(self):
        channel, addr = self.accept()
        c = ServerChannel(channel, self._options, self._session(), self._logger)
        c.log_info('New connection ...')

    def sigterm_handler(self, signum, frame):
        self._logger.info("Caught SIGTERM, shutting down the server.")
        self._server.running = False
        asyncore.socket_map.clear()

    def run(self, test=False):
        if not test:
            signal.signal(signal.SIGTERM, self.sigterm_handler)
        host, port = self._options.listen.split(':', 1)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, int(port)))
        self.listen(5)
        self._logger.info("The server is ready to accept connections:")
        self._logger.info('+ Server name: %s' % self._options.name)
        self._logger.info('+ Enabled domains: %s' % \
            ','.join(self._options.domains.keys()))
        server = self._server
        try:
            while server.running:
                asyncore.poll(1.0)
        except KeyboardInterrupt:
            self._logger.info("Caught KeyboardInterrupt, shutting down the "
                "server.")
        for x in asyncore.socket_map.values():
            x.socket.close()


class DataManager(threading.Thread):
    """Generic data manager"""

    def __init__(self, server):
        super(DataManager, self).__init__()
        self._server = server
        self._options = server.options
        self._session = server.session
        self._logger = server.logger
        self._interval = int(server.options.interval)

    def _filename(self, domain, key, checksum, url=False):
        parts = not url and [self._options.data, domain[2]] or []
        parts.extend((
            checksum[0:2],
            checksum[2:4],
            checksum[4:6],
            checksum[6:8],
            checksum[8:12],
            checksum[12:16],
            checksum[16:24],
            checksum[24:32],
        ))
        parts.append(key)
        return not url and os.path.join(*parts) or '/'.join(parts)

    def run(self):
        timer = time.time()
        while self._server.running:
            if time.time() - timer >= self._interval:
                session = self._session()
                self._logger.debug('(d-m) Running: domains')
                self.handler_domains(session)
                self._logger.debug('(d-m) Running: purge')
                self.handler_purge(session)
                self._logger.debug('(d-m) Running: sync')
                self.handler_sync(session)
                self._logger.debug('(d-m) Done, sleeping for %s seconds' %
                    self._interval)
                session.close()
                timer = time.time()
            time.sleep(1)

    def handler_domains(self, session):
        self._server.update_domains(session, self._options)
        self._logger.debug('(d-m) - Enabled domains: %s' % \
            ', '.join(sorted(self._options.domains.keys())))

    def handler_purge(self, session):
        options = self._options
        # select all the files which are marked for removal
        results = session.query(Replica.id, Domain.name, File.key,
            File.checksum).filter(and_(
                Domain.id == File.domain_id,
                Replica.file_id == File.id,
                Replica.server_id == options.server_id,
                File.replicas > 0,
                File.status == u'D',
            )).order_by(File.deleted_on)[:100]
        to_be_removed = []
        for r in results:
            filename = self._filename(options.domains[r[1]], r[2], r[3])
            to_be_removed.append(filename)
            replica = session.query(Replica).filter_by(id=r[0]).first()
            replica.file.replicas -= 1
            session.delete(replica)
        # commit on the database
        session.commit()
        # remove the files from the file system
        for filename in to_be_removed:
            if not os.path.isfile(filename):
                self._logger.error("(d-m) - No such file `%s'" % filename)
                continue
            os.unlink(filename)
            head, tail = os.path.split(filename)
            while head and tail:
                try:
                    os.rmdir(head)
                except os.error:
                    break
                head, tail = os.path.split(head)
                if head == options.data:
                    break
        # log the result
        n = len(to_be_removed)
        if n > 0:
            self._logger.info('(d-m) - Purged %d files from the file system' % n)

    def handler_sync(self, session):
        options = self._options
        domains = map(int, options.rdomains.keys())
        server_id = self._options.server_id
        # select all the files which we do not have locally
        results = session.query(File.id, File.domain_id, File.key,File.checksum,
            ).filter(and_(
                File.replicas < File.class_, File.status == u'R',
                File.domain_id.in_(domains),
                ~File.replicas_.any(Replica.server_id == server_id)
            )).order_by(File.created_on)[:100]
        # loop on the results, sync files we don't have locally
        n = 0
        for r in results:
            self._sync(session, r[0], options.rdomains[r[1]], r[2], r[3])
            n += 1
        # commit on the database
        session.commit()
        # log the result
        if n > 0:
            self._logger.info('(d-m) - Synchronized %d files from the network' % n)

    def _sync(self, session, fid, domain, key, checksum):
        # get the list of servers we can find the file on
        results = session.query(Server.host).filter(and_(
            Server.id == Replica.server_id, Replica.file_id == fid))
        servers = map(operator.itemgetter(0), results)
        # if we do not have servers, return
        if not servers:
            return False
        # connect to the servers, and download the file
        random.shuffle(servers)
        client = Client(domain[1], servers=servers, timeout=10.0)
        tmpfile = tempfile.mktemp(prefix='koboldfs-', dir=self._options.tmp)
        output = open(tmpfile, 'wb')
        success = client.get(key, output)
        output.close()
        # move the file to the right position and register the replica
        if success:
            filename = self._filename(domain, key, checksum)
            directory = os.path.split(filename)[0]
            if not os.path.isdir(directory):
                os.makedirs(directory)
            shutil.move(tmpfile, filename)
            replica = Replica(file_id=fid, server_id=domain[4])
            session.add(replica)
            file = session.query(File).filter_by(id=fid).first()
            file.replicas += 1
        # error while trasferring the file: abort and remove the temporary file
        else:
            self._logger.error("(d-m) - Unable to sync (`%s', `%s') from the "
                "network" % (domain[1], key))
            os.unlink(tmpfile)


class ServerHandler(object):
    """Server for the koboldfs distributed filesystem"""

    def __init__(self):
        self.running = True

    def parse_arguments(self, argv):
        """Parse command line arguments"""
        parser = optparse.OptionParser(version="%prog " + protocol.VERSION)
        parser.add_option("-d", "--debug", action="store_true", dest="debug",
            help="run the server in debug mode", default=False)
        parser.add_option("", "--config", action="store", dest="config",
            help="read the options from the specified configuration file",
            default=None)
        parser.add_option("", "--name", action="store", dest="name",
            help="the name of the server instance, defaults to localhost")
        parser.add_option("", "--dsn", action="store", dest="dsn",
            help="the database URI where to store the metadata")
        parser.add_option("", "--twophase", action="store_true", default=False,
            dest="twophase", help="enable two phase transactions")
        parser.add_option("", "--data", action="store", dest="data",
            help="directory where to store the repository")
        parser.add_option("", "--tmp", action="store", dest="tmp",
            help="directory where to store the temporary files")
        parser.add_option("", "--log", action="store", dest="log",
            help="directory where to store the log files")
        parser.add_option("", "--interval", action="store", dest="interval",
            help="interval for batch operations, defaults to 60", default=60)
        parser.add_option("", "--listen", action="store", dest="listen",
            help="address and port the server listens to, defaults to "
            "'localhost:9876'", default='localhost:9876')
        (options, args) = parser.parse_args(argv)
        if options.config:
            self.parse_options(options)
        mandatories = ['name', 'dsn', 'data', 'tmp']
        for m in mandatories:
            if not options.__dict__[m]:
                print "Mandatory option is missing: %s\n" % m
                parser.print_help()
                sys.exit(1)
        if not os.path.isdir(options.data):
            print "Repository directory `%s' does not exist!" % options.data
            sys.exit(1)
        elif not os.path.isdir(options.tmp):
            print "Repository temporary directory `%s' does not exist!" % options.tmp
            sys.exit(1)
        options.data = os.path.normpath(options.data)
        options.tmp = os.path.normpath(options.tmp)
        return (parser, options, args)

    def parse_options(self, options):
        if not os.path.isfile(options.config):
            print "Configuration file `%s' does not exist!" % options.config
            sys.exit(1)
        if options.config.endswith('.ini'):
            config = ConfigParser()
            config.read([options.config])
            for key, value in config.items('koboldfs'):
                setattr(options, key, value)
        else:
            for r in open(options.config):
                r = r.strip()
                if r.startswith('#') or '=' not in r:
                    continue
                key, value = map(string.strip, r.split('=', 1))
                setattr(options, key, value)

    def start_logging(self, options):
        """Start logging infrastructure"""
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        if not options.log:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.handlers.TimedRotatingFileHandler(
                os.path.join(options.log, 'koboldfsd.log'), 'D', 1, 7)
        handler.setFormatter(formatter)
        handler.setLevel(options.debug and logging.DEBUG or logging.INFO)
        logger = logging.getLogger()
        logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
        logger.addHandler(handler)
        return logger

    def setup_database(self, options):
        # SQLAlchemy connection setup
        self.engine = create_engine(options.dsn, convert_unicode=True)
        Base.metadata.bind = self.engine
        Base.metadata.create_all()
        Session = sessionmaker(twophase=bool(options.twophase))
        Session.bind = self.engine
        # get the list of domains
        session = Session()
        name = options.name.decode('utf-8')
        server = session.query(Server).filter_by(name=name).first()
        if server is None:
            server = Server(name=name, host=options.listen.decode('utf-8'))
            session.add(server)
            session.commit()
        options.server_id = server.id
        options.domains = {}
        options.rdomains = {}
        self.update_domains(session, options)
        session.close()
        # return the database object
        return Session

    def update_domains(self, session, options):
        domains = {}
        rdomains = {}
        for r in session.query(Domain.id, Domain.name, Domain.folder,
            Domain.url, Server.id).filter(and_(
                Domain.id == ServerDomain.domain_id,
                Server.id == ServerDomain.server_id,
                Server.name == options.name.decode('utf-8'))):
            domains[r[1]] = tuple(r)
            rdomains[r[0]] = tuple(r)
        options.domains = domains
        options.rdomains = rdomains
        return (options.domains, options.rdomains)

    def main(self, argv, test=False):
        # parse the command line arguments
        (parser, self.options, args) = self.parse_arguments(argv)
        # start the server and the related threads
        self.logger = self.start_logging(self.options)
        self.session = self.setup_database(self.options)
        threads = []
        threads.append(DataManager(self))
        for t in threads:
            t.start()
        try:
            ServerDispatcher(self).run(test=test)
        except socket.error, e:
            self.logger.error(str(e))
        # shutdown the server
        self.running = False
        for t in threads:
            t.join()
        self.engine.dispose()
        for handler in self.logger.handlers:
            handler.close()


def main(argv=sys.argv, test=False):
    """Run the koboldfs server"""
    ServerHandler().main(argv, test=test)
