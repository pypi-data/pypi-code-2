#!/usr/bin/env python
#-*- coding: windows-1251 -*-
###############################################################################
#
# This module contains an implementation of e-mail interface (polling over POP3)
# and resource (sending over SMTP). This code also supports POP3S and SMTPS
# (same protocols but over SSL rather than plain TCP) and this is configurable.
#
# Sample e-mail interface configuration (config_interface_email_1.py):
#
# config = dict \
# (
# protocol = "email",                                 # meta
# request_timeout = None,                             # meta, optional
# server_address = ("mail.domain.com", 110),          # tcp
# connect_timeout = 3.0,                              # tcp
# ssl_key_cert_file = None,                           # ssl, optional filename
# ssl_ca_cert_file = None,                            # ssl, optional filename
# interval = 30.0,                                    # email
# username = "user",                                  # email
# password = "pass",                                  # email
# )
#
# Sample processing module (interface_email_1.py):
#
# def process_request(request, response):
#     message_id = request["message_id"]
#     message = request["message"]
#     subject = message["Subject"]
#
# Sample e-mail resource configuration (config_resource_email_1.py)
#
# config = dict \
# (
# protocol = "email",                                 # meta
# server_address = ("mail.domain.com", 25),           # tcp
# connect_timeout = 3.0,                              # tcp
# ssl_key_cert_file = None,                           # ssl, optional filename
# ssl_ca_cert_file = None,                            # ssl, optional filename
# encoding = "windows-1251",                          # email
# helo = "hostname",                                  # email
# username = None,                                    # email, optional
# password = None,                                    # email, optional
# )
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.email_1.send("from@mail", "to@mail", "subject", "message text")
# xa.email_1.send("From <from@mail>", "To <to@mail>", "subject", "message text",
#                 { "X-Header-Field": "Value", ... }, # optional extra header fields
#                 (("foo.jpg", "image/jpeg", b"JPEG"), ...)) # optional attachments
# xa.execute() # sending e-mail message yields no result
#
# Pythomnic3k project
# (c) 2005-2010, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "decode_value", "format_addr" ]

###############################################################################

import email.utils; from email.utils import parseaddr
import email.parser; from email.parser import FeedParser
import email.message; from email.message import Message
import email.header; from email.header import decode_header
import io; from io import StringIO, BytesIO
import re; from re import compile as regex
import base64; from base64 import b64encode
import os; from os import urandom, SEEK_END, path as os_path
import binascii; from binascii import b2a_hex
import threading; from threading import current_thread

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, typecheck_with_exceptions, \
                                        optional, tuple_of, dict_of, by_regex, either
import pmnc.threads; from pmnc.threads import HeavyThread
import pmnc.request; from pmnc.request import fake_request
import pmnc.thread_pool; from pmnc.thread_pool import WorkUnitTimedOut
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource, \
                           ResourceError, ResourceInputParameterError

###############################################################################

@typecheck
def decode_value(s: str) -> str: # takes "=?B?FOO?=", returns "foo"
    try:
        return " ".join(value if isinstance(value, str) else value.decode(charset or "ascii")
                        for value, charset in decode_header(s))
    except (UnicodeDecodeError, LookupError):
        return "?"

def _parse_addr(s: str) -> (str, str): # takes "=?B?FOO?= <foo@bar>", returns ("foo", "foo@bar")
    parsed = parseaddr(s)
    return decode_value(parsed[0]), parsed[1]

@typecheck
def format_addr(s: str) -> str: # takes "=?B?FOO?= <foo@bar>", returns "Foo <foo.bar>"
    name, addr = _parse_addr(s)
    return "{0:s} <{1:s}>".format(name, addr) if name else addr if addr else "<>"

def _encode_value(s, encoding): # takes "foo", returns b"=?B?FOO?="
    try:
        return s.encode("ascii")
    except UnicodeEncodeError:
        return b"=?" + encoding.encode("ascii") + b"?B?" + b64encode(s.encode(encoding)) + b"?="

def _encode_addr(addr, encoding): # takes "Foo <foo@bar>", returns b"=?B?FOO?= <foo@bar>"
    name, addr = _parse_addr(addr)
    return _encode_value(name, encoding) + b" <" + addr.encode("ascii") + b">" \
           if name else addr.encode("ascii")

def _encode_auth_plain(username, password): # returns SMTP login token for AUTH PLAIN
    return b64encode(b"\x00" + username.encode("ascii") +
                     b"\x00" + password.encode("ascii")).decode("ascii")

###############################################################################

class Interface: # email (POP3) interface

    @typecheck
    def __init__(self, name: str, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 username: str,
                 password: str,
                 interval: float,
                 request_timeout: optional(float) = None,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_email_X.py

        self._name = name
        self._server_address = server_address
        self._connect_timeout = connect_timeout
        self._ssl_key_cert_file = ssl_key_cert_file
        self._ssl_ca_cert_file = ssl_ca_cert_file
        self._username = username
        self._password = password
        self._interval = interval

        self._request_timeout = request_timeout or \
            pmnc.config_interfaces.get("request_timeout") # this is now static

        # this set tracks messages that have been processed but
        # not deleted on the server due to deletion failure

        self._processed_messages = set()

        if pmnc.request.self_test == __name__: # self-test
            self._process_request = kwargs["process_request"]

    name = property(lambda self: self._name)

    ###################################

    def start(self):
        self._poller = HeavyThread(target = self._poller_proc,
                                   name = "{0:s}:poll".format(self._name))
        self._poller.start()

    def cease(self):
        self._poller.stop()

    def stop(self):
        pass

    ###################################

    # this thread periodically polls the mail server for new messages

    def _poller_proc(self):

        interval = self._interval

        while not current_thread().stopped(interval):
            try:

                # attach a fake request to this thread so that network access
                # in TcpResource times out properly; since this timeout will
                # include connection establishment and POP3 protocol overhead,
                # the timeout is increased by connect_timeout

                timeout = self._connect_timeout + self._request_timeout
                fake_request(timeout = timeout, interface = self._name)
                pmnc.request.describe("polling mailbox")

                # since there is no other way to commit POP3 receiving transaction
                # but to disconnect, we have to limit each session to one message

                self._pop3 = pmnc.protocol_tcp.TcpResource(self._username,
                                                           server_address = self._server_address,
                                                           connect_timeout = self._connect_timeout,
                                                           ssl_key_cert_file = self._ssl_key_cert_file,
                                                           ssl_ca_cert_file = self._ssl_ca_cert_file)
                self._pop3.connect()
                try:

                    self._login()

                    message_count = self._get_message_count()
                    if message_count == 0:
                        self._logout()
                        continue

                    message_id = self._get_message_id()
                    if message_id not in self._processed_messages: # don't process the message again
                        message = self._get_message()
                        delete_message = self._process_message(message_id, message)
                    else:
                        delete_message = True # simply delete the message on the server

                    try:
                        if delete_message:
                            self._delete_message()
                        self._logout()
                    except:
                        if delete_message:               # if there was an error deleting
                            pmnc.log.error(exc_string()) # message, reconnect immediately
                            interval = 0.0
                            continue
                        else:
                            raise

                    if delete_message:
                        self._processed_messages.remove(message_id)

                finally:
                    self._pop3.disconnect()

            except:
                pmnc.log.error(exc_string())
                interval = self._interval
            else:
                interval = self._interval if message_count <= 1 else 0.0

    ###################################

    def _process_message(self, message_id, message):

        # now that the message is parsed, we know more about the request

        subject = message["Subject"]
        subject = decode_value(subject) if subject is not None else ""
        from_ = format_addr(message["From"] or "")

        request_description = "e-mail \"{0:s}\" from {1:s}".format(subject, from_)
        pmnc.request.describe(request_description)

        # create a new request for processing the message, note that the timeout
        # depends on how much time the current request has spent receiving

        request = pmnc.interfaces.begin_request(
                    timeout = min(self._request_timeout, pmnc.request.remain),
                    interface = self._name, protocol = "email",
                    parameters = dict(auth_tokens = dict()),
                    description = request_description)

        # enqueue the request and wait for its completion

        try:
            pmnc.interfaces.enqueue(request, self.wu_process_request,
                                    (message_id, message)).wait()
        except WorkUnitTimedOut:
            pmnc.log.error("message processing timed out")
            success = None
        except:
            pmnc.log.error("message processing failed: {0:s}".format(exc_string()))
            success = False
        else:
            pmnc.log.debug("message processing succeeded")
            self._processed_messages.add(message_id)
            success = True
        finally:
            pmnc.interfaces.end_request(success, request)
            return success == True

    ###################################

    # this method is a work unit executed by one of the interface pool threads
    # if this method fails, the exception is rethrown in _process_message in wait()

    @typecheck
    def wu_process_request(self, message_id: str, message: Message):

        # see for how long the request was on the execution queue up to this moment
        # and whether it has expired in the meantime, if it did there is no reason
        # to proceed and we simply bail out

        if pmnc.request.expired:
            pmnc.log.error("request has expired and will not be processed")
            return

        try:
            with pmnc.performance.request_processing():
                request = dict(message_id = message_id, message = message)
                self._process_request(request, {})
        except:
            pmnc.log.error(exc_string()) # don't allow an exception to be silenced
            raise                        # when this work unit is not waited upon

    ###################################

    def _process_request(self, request, response):
        handler_module_name = "interface_{0:s}".format(self._name)
        pmnc.__getattr__(handler_module_name).process_request(request, response)

    ###################################

    def _login(self):
        self._send_line(None)
        self._send_line("USER {0:s}".format(self._username))
        self._send_line("PASS {0:s}".format(self._password))

    def _get_message_count(self):
        stat = self._send_line("STAT")
        return int(stat.split(" ")[0])

    def _get_message_id(self):
        uidl = self._send_line("UIDL 1")
        return uidl.split(" ")[1]

    def _get_message(self):
        return self._send_line("RETR 1", True)

    def _delete_message(self):
        self._send_line("DELE 1")

    def _logout(self):
        self._send_line("QUIT")

    ###################################

    def _send_line(self, line: optional(str), read_message: optional(bool) = False):

        self._response = BytesIO()
        self._response_offset = 0
        self._read_message = read_message # this triggers the response_handler callback behaviour

        if line: pmnc.log.debug(">> {0:s}".format(line))
        data = "{0:s}\r\n".format(line).encode("ascii") if line is not None else b""
        response = self._pop3.send_request(data, self.response_handler)

        if not read_message:
            pmnc.log.debug("<< {0:s}".format(response))
        else:
            pmnc.log.debug("<< ...message body...")

        return response

    ###################################

    _content_type_charset = regex("^content-type[ \\t]*:[ \\t]*text/.*;[ \\t]*charset=\"?([A-Za-z0-9_-]+)\"?[ \\t]*(?:;|$)")
    _folded_charset = regex("^[ \\t]+charset=\"?([A-Za-z0-9_-]+)\"?[ \\t]*(?:;|$)")

    @typecheck
    def response_handler(self, data: bytes): # this callback method is invoked by
                                             # TcpResource as server response is read

        self._response.seek(0, SEEK_END)
        self._response.write(data)

        while True:

            self._response.seek(self._response_offset)

            line_b = self._response.readline()
            if line_b.endswith(b"\r\n"):
                line_b = line_b[:-2]
            elif line_b.endswith(b"\n"):
                line_b = line_b[:-1]
            else:
                return None # no complete line at the end of buffer, wait for more data

            response_offset, self._response_offset = self._response_offset, self._response.tell()

            if response_offset == 0: # first (possibly the only) line has been read
                line = line_b.decode("ascii", "replace")
                if line.startswith("+OK"):
                    if self._read_message:
                        self._message_parser = FeedParser() # proceed to message parsing
                        self._message_encoding = None
                        continue
                    else:
                        return line[3:].strip() # the successful one-line response
                elif line.startswith("-ERR"):
                    raise Exception(line[4:].strip())
                else:
                    raise Exception(line.strip())

            # hack: convert bytes to str using deduced encoding and detect encoding change

            line = line_b.decode(self._message_encoding or "ascii", "replace")

            line_lc = line.lower()
            charset_match = self._content_type_charset.match(line_lc) or \
                            self._folded_charset.match(line_lc)
            if charset_match:
                charset = charset_match.groups()[0]
                try:
                    assert b"123".decode(charset) == "123"
                except:
                    pass
                else:
                    self._message_encoding = charset

            # message lines are fed into the parser one by one

            if line != ".":
                self._message_parser.feed(line + "\r\n")
            else:
                return self._message_parser.close() # return the parsed message

###############################################################################

class Resource(TransactionalResource): # email (SMTP) resource

    valid_mime_type = by_regex("^[A-Za-z0-9~`!#$%^&*+|{}'._-]+/[A-Za-z0-9~`!#$%^&*+|{}'._-]+$")

    @typecheck
    def __init__(self, name: str, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 encoding: str,
                 helo: str,
                 username: optional(str),
                 password: optional(str)):

        TransactionalResource.__init__(self, name)

        self._encoding = encoding
        self._helo = helo
        self._username = username
        self._password = password

        self._smtp = \
            pmnc.protocol_tcp.TcpResource(name,
                                          server_address = server_address,
                                          connect_timeout = connect_timeout,
                                          ssl_key_cert_file = ssl_key_cert_file,
                                          ssl_ca_cert_file = ssl_ca_cert_file)

    ###################################

    def connect(self):
        TransactionalResource.connect(self)
        self._smtp.connect()
        self._send_line(None, { 220 })
        self._send_line("HELO {0:s}".format(self._helo), { 250 })
        if self._username and self._password:
            auth_plain = _encode_auth_plain(self._username, self._password)
            self._send_line("AUTH PLAIN {0:s}".format(auth_plain), { 235 })
        self._graceful_close = True

    ###################################

    def begin_transaction(self, *args, **kwargs):
        TransactionalResource.begin_transaction(self, *args, **kwargs)
        self._message_sent = False

    ###################################

    @typecheck_with_exceptions(input_parameter_error = ResourceInputParameterError)
    def send(self, from_addr: str, to_addr: str, subject: str, text: str,
             headers: optional(dict_of(str, str)) = None,
             attachments: optional(tuple_of((str, valid_mime_type, either(str, bytes)))) = None):

        try:

            from_ = _parse_addr(from_addr)[1]
            to_ = _parse_addr(to_addr)[1]
            from_name = _encode_addr(from_addr, self._encoding)
            to_name = _encode_addr(to_addr, self._encoding)

            message_data = self._wrap_message(from_name, to_name, subject, text,
                                              headers or {}, attachments or ())

            pmnc.log.info("sending e-mail message \"{0:s}\" for {1:s}".\
                          format(subject, format_addr(to_addr)))
            try:
                self._send_line("MAIL FROM:<{0:s}>".format(from_), { 250 })
                self._send_line("RCPT TO:<{0:s}>".format(to_), { 250 })
                self._send_line("DATA", { 354 })
                self._message_sent = True
                self._send_bytes(message_data)
            except:
                pmnc.log.warning("sending e-mail message \"{0:s}\" for {1:s} failed: {2:s}".\
                                 format(subject, format_addr(to_addr), exc_string()))
                raise

        except ResourceError: # server response with unexpected code
            raise
        except:
            ResourceError.rethrow(recoverable = True) # no irreversible changes

    ###################################

    def commit(self):
        self._send_line(".", { 250 })
        pmnc.log.info("e-mail message has been sent")

    ###################################

    def rollback(self):
        self._graceful_close = False
        self.expire() # there is no other way to interrupt message sending but to disconnect

    ###################################

    def disconnect(self):
        try:
            try:
                if self._graceful_close:
                    self._send_line("QUIT", { 221 })
                elif self._message_sent:
                    pmnc.log.info("e-mail message has been aborted")
            finally:
                self._smtp.disconnect()
        except:
            pmnc.log.error(exc_string()) # log and ignore
        finally:
            TransactionalResource.disconnect(self)

    ###################################

    _response_line_parser = regex("^([0-9]+)([ -])(.*)$")

    # this callback method is invoked by TcpResource as server response is read

    @typecheck
    def response_handler(self, data: bytes) -> optional((int, str)):

        self._response.seek(0, SEEK_END)
        self._response.write(data.decode("ascii", "replace"))

        while True: # SMTP response can consist of multiple lines

            self._response.seek(self._response_offset)
            line = self._response.readline()

            if line.endswith("\r\n"):
                line = line[:-2]
            elif line.endswith("\n"):
                line = line[:-1]
            else:
                return None # no complete line at the end of buffer

            self._response_offset = self._response.tell()

            try:
                retcode, delim, message = \
                    self._response_line_parser.findall(line)[0]
            except:
                raise Exception("invalid server response: {0:s}".format(line))

            if delim == " ": # this is the last line of the response
                return int(retcode), message

    ################################### NETWORK-RELATED METHODS

    def _send_bytes(self, data, positive_retcodes = None):

        self._response = StringIO() # SMTP server responses are treated as ascii-only
        self._response_offset = 0

        if positive_retcodes:
            retcode, message = self._smtp.send_request(data, self.response_handler)
            pmnc.log.debug("<< {0:d} {1:s}".format(retcode, message))
            if retcode not in positive_retcodes:
                raise ResourceError(code = retcode, description = message, recoverable = True)
        else:
            pmnc.log.debug(">> ...message body...")
            self._smtp.send_request(data)

    ###################################

    def _send_line(self, line, positive_retcodes):

        if line: pmnc.log.debug(">> {0:s}".format(line))

        data = "{0:s}\r\n".format(line).encode("ascii") if line else b""
        self._send_bytes(data, positive_retcodes)

    ################################### MESSAGE ASSEMBLING METHODS

    @typecheck
    def _wrap_message(self, from_name: bytes, to_name: bytes, subject: str, text: str, headers: dict_of(str, str),
                      attachments: tuple_of((str, str, either(str, bytes)))) -> bytes:

        result = BytesIO()

        boundary = self._make_boundary() # this random boundary separates message parts (ex. attachments)

        # email-specific fields are contained in the outer envelope

        result.write(b"MIME-Version: 1.0\r\n" \
                     b"Content-Type: multipart/mixed; boundary=\"" + boundary + b"\"\r\n" \
                     b"From: " + from_name + b"\r\n" \
                     b"To: " + to_name + b"\r\n" \
                     b"Subject: " + _encode_value(subject, self._encoding) + b"\r\n")

        # append user-defined header fields

        for k, v in headers.items():
            result.write(k.encode("ascii") + b": " + _encode_value(v, self._encoding) + b"\r\n")

        # append textual body

        result.write(b"\r\n" \
                     b"--" + boundary + b"\r\n" + \
                     self._wrap_body(text))

        # append attachments

        for filename, mime_type, content in attachments:
            if mime_type.startswith("text/"):
                if isinstance(content, str):
                    content = content.encode(self._encoding)
                    mime_type += "; charset={0:s}".format(self._encoding)
            else:
                assert isinstance(content, bytes), "attachment not of type text/* should be bytes"
            result.write(b"--" + boundary + b"\r\n" +
                         self._wrap_attachment(filename, mime_type, content))

        # complete the message and return the entire stream contents

        result.write(b"--" + boundary + b"--\r\n")

        return result.getvalue()

    ###################################

    def _make_boundary(self):
        return b2a_hex(urandom(16))

    ###################################

    def _wrap_body(self, text):
        return self._wrap_part({ "Content-Type": "text/plain; charset={0:s}".format(self._encoding),
                                 "Content-Disposition": "inline" },
                               text.encode(self._encoding))

    ###################################

    def _wrap_attachment(self, filename, mime_type, data):
        filename = _encode_value(filename, self._encoding).decode("ascii")
        return self._wrap_part({ "Content-Type": mime_type,
                                 "Content-Disposition": "attachment; filename=\"{0:s}\"".format(filename) },
                               data)

    ###################################

    @staticmethod
    @typecheck
    def _wrap_part(headers: dict_of(str, str), content: bytes) -> bytes:

        result = BytesIO()

        headers["Content-Transfer-Encoding"] = "base64"
        for k, v in headers.items():
            result.write(k.encode("ascii") + b": " + v.encode("ascii") + b"\r\n")
        result.write(b"\r\n")

        content = BytesIO(content)
        raw_line = content.read(57)
        while raw_line:
            result.write(b64encode(raw_line) + b"\r\n")
            raw_line = content.read(57)

        return result.getvalue()

###############################################################################

def self_test():

    from expected import expected
    from time import sleep
    from interlocked_queue import InterlockedQueue
    from pmnc.self_test import active_interface

    ###################################

    test_interface_config = dict \
    (
    protocol = "email",
    server_address = ("mail.domain.com", 110),
    connect_timeout = 3.0,
    ssl_key_cert_file = None,
    ssl_ca_cert_file = None,
    username = "to",   # recipient's POP3 username
    password = "pass", # recipient's POP3 password
    interval = 3.0,
    )

    def interface_config(**kwargs):
        result = test_interface_config.copy()
        result.update(kwargs)
        return result

    ###################################

    from_addr = "from@domain.com" # sender's address
    to_addr = "to@domain.com"     # recipient's address

    russian = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя"

    ###################################

    def _decode_message_part(m):
        if m.get_filename():
            if m.get_content_maintype() == "text":
                return m.get_filename(), m.get_payload(decode = True).decode(m.get_content_charset("ascii"))
            else:
                return m.get_filename(), m.get_content_type(), m.get_payload(decode = True)
        else:
            if m.get_content_maintype() == "text":
                return m.get_payload(decode = True).decode(m.get_content_charset("ascii"))
            else:
                return m.get_content_type(), m.get_payload(decode = True)

    ###################################

    def test_encoding_routines():

        assert _encode_value("", "windows-1251") == b""
        assert _encode_value("foo@bar", "windows-1251") == b"foo@bar"
        assert _encode_value(russian, "windows-1251") == \
               b"=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva" \
               b"3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?="
        assert _encode_value("foo@bar", "cp866") == b"foo@bar"
        assert _encode_value(russian, "cp866") == \
               b"=?cp866?B?gIGCg4SF8IaHiImKi4yNjo+QkZKTlJWWl5iZnJuan" \
               b"Z6foKGio6Sl8aanqKmqq6ytrq/g4eLj5OXm5+jp7Ovq7e7v?="

        assert decode_value("") == ""
        assert decode_value("foo@bar") == "foo@bar"
        assert decode_value("=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva"
                            "3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?=") == russian
        assert decode_value("=?cp866?B?gIGCg4SF8IaHiImKi4yNjo+QkZKTlJWWl5iZnJuan"
                            "Z6foKGio6Sl8aanqKmqq6ytrq/g4eLj5OXm5+jp7Ovq7e7v?=") == russian

        assert decode_value("=?windows-1251?B?gIGCg4SF8IaHiImKi4yNjo+QkZKTlJWWl5iZnJuan"
                            "Z6foKGio6Sl8aanqKmqq6ytrq/g4eLj5OXm5+jp7Ovq7e7v?=") == "?"
        r1 = "АБВ"; r2 = "абв"
        r = b"foo " + _encode_value(r1, "windows-1251") + b" " + _encode_value(r2, "cp866")
        assert pmnc.protocol_email.decode_value(r.decode("ascii")) == "foo АБВ абв"

        assert decode_value("=?windows-1251?Q?=C0=C1=C2?=") == "АБВ"
        assert decode_value("=?ascii?Q?=FF=FF=FF?=") == "?"
        assert decode_value("=?never-existed?Q?foo?=") == "?"

        assert _parse_addr("foo@bar") == _parse_addr("<foo@bar>") == ("", "foo@bar")
        assert _parse_addr("Foo <foo@bar>") == ("Foo", "foo@bar")
        r = _encode_value(russian, "windows-1251").decode("ascii")
        assert _parse_addr("Foo " + r + " <foo@bar>") == ("Foo " + russian, "foo@bar")

        assert _encode_auth_plain("user", "pass") == "AHVzZXIAcGFzcw=="

        assert _encode_addr("", "windows-1251") == b""
        assert _encode_addr("foo@bar", "windows-1251") == _encode_addr("<foo@bar>", "cp866") == b"foo@bar"
        assert _encode_addr("Foo <foo@bar>", "windows-1251") == b"Foo <foo@bar>"
        assert _encode_addr(russian + " <foo@bar>", "windows-1251") == \
               b"=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva" \
               b"3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?= <foo@bar>"

        assert format_addr("") == "<>"
        assert format_addr("foo@bar") == "foo@bar"
        assert format_addr("Foo <foo@bar>") == "Foo <foo@bar>"
        assert pmnc.protocol_email.format_addr("=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva"
                                               "3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?= <foo@bar>") == \
               russian + " <foo@bar>"

    test_encoding_routines()

    ###################################

    def test_wrapping_methods():

        assert Resource._wrap_part({ "X-Foo": "Bar", "X-Biz": "baz" }, b"data") == \
               b"Content-Transfer-Encoding: base64\r\nX-Biz: baz\r\nX-Foo: Bar\r\n\r\nZGF0YQ==\r\n"

        assert Resource._wrap_part({ "X-Foo": "Bar", "X-Biz": "baz" }, b"data" * 20) == \
               b"Content-Transfer-Encoding: base64\r\nX-Biz: baz\r\nX-Foo: Bar\r\n\r\n" \
               b"ZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFk\r\n" \
               b"YXRhZGF0YWRhdGFkYXRhZGF0YWRhdGE=\r\n"

        with expected(UnicodeEncodeError): # headers must contain ascii only
            Resource._wrap_part({ "X-Foo": russian }, b"")

        with expected(UnicodeEncodeError): # headers must contain ascii only
            Resource._wrap_part({ russian: "Bar" }, b"")

        r = Resource("test_resource_wrap_message", server_address = ("", 0),
                     connect_timeout = 1.0, ssl_key_cert_file = None, ssl_ca_cert_file = None,
                     encoding = "windows-1251", helo = "test", username = None, password = None)

        r._make_boundary = lambda: b"abcdef" # test-only hack

        assert r._wrap_message(b"from@host", b"to@host", "subject", "text", {}, ()) == \
               b"MIME-Version: 1.0\r\n" \
               b"Content-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\n" \
               b"To: to@host\r\n" \
               b"Subject: subject\r\n" \
               b"\r\n" \
               b"--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\n" \
               b"Content-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n" \
               b"\r\n" \
               b"dGV4dA==\r\n" \
               b"--abcdef--\r\n"

        assert r._wrap_message(b"from@host", b"to@host", "", "", { "X-Foo": "bar" }, ()) == \
               b"MIME-Version: 1.0\r\n" \
               b"Content-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\n" \
               b"To: to@host\r\n" \
               b"Subject: \r\n" \
               b"X-Foo: bar\r\n" \
               b"\r\n" \
               b"--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\n" \
               b"Content-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n" \
               b"\r\n" \
               b"--abcdef--\r\n"

        assert r._wrap_message(b"from@host", b"to@host", russian, russian, {},
                               (("foo.jpg", "image/jpeg", b"JPEG"), ("foo.txt", "text/plain", "TEXT"))) == \
               b"MIME-Version: 1.0\r\n" \
               b"Content-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\n" \
               b"To: to@host\r\n" \
               b"Subject: =?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?=\r\n" \
               b"\r\n" \
               b"--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\n" \
               b"Content-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n" \
               b"\r\n" \
               b"wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX2\r\n" \
               b"9/j5/Pv6/f7/\r\n" \
               b"--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\n" \
               b"Content-Type: image/jpeg\r\n" \
               b"Content-Disposition: attachment; filename=\"foo.jpg\"\r\n" \
               b"\r\n" \
               b"SlBFRw==\r\n" \
               b"--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\n" \
               b"Content-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: attachment; filename=\"foo.txt\"\r\n" \
               b"\r\n" \
               b"VEVYVA==\r\n" \
               b"--abcdef--\r\n"

    test_wrapping_methods()

    ###################################

    def test_invalid_parameters():

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.email_1.send("", "", "", b"") # bytes for text ?!
        with expected(ResourceInputParameterError):
            xa.execute()

    test_invalid_parameters()

    ###################################

    def drain_mailbox():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):
            while loopback_queue.pop(10.0) is not None:
                pass

    drain_mailbox()

    ###################################

    def test_send_simple():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):

            fake_request(10.0)

            xa = pmnc.transaction.create()
            xa.email_1.send(from_addr, to_addr, "subject", ".")
            xa.execute()

            m = loopback_queue.pop(10.0)

        assert m["Subject"] == "subject"

        mps = [ _decode_message_part(mp) for mp in m.walk() if not mp.is_multipart() ]
        assert len(mps) == 1
        assert mps[0] == "."

        assert loopback_queue.pop(30.0) is None

    test_send_simple()

    ###################################

    def test_send_complex():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):

            fake_request(10.0)

            xa = pmnc.transaction.create()
            xa.email_1.send("Отправитель <{0:s}>".format(from_addr),
                            "Получатель <{0:s}>".format(to_addr),
                            "тема", "текст" * 1000, { "X-Foo": "Bar" },
                            (("текст", "text/plain", russian),
                             ("image.jpg", "image/jpeg", b"\x00\x00\x00")))
            xa.execute()

            m = loopback_queue.pop(10.0)

        assert decode_value(m["Subject"]) == "тема"
        assert m["X-Foo"] == "Bar"

        mps = [ _decode_message_part(mp) for mp in m.walk() if not mp.is_multipart() ]
        assert len(mps) == 3
        assert mps[0] == "текст" * 1000
        assert mps[1] == ("=?windows-1251?B?8uXq8fI=?=", russian)
        assert mps[2] == ("image.jpg", "image/jpeg", b"\x00\x00\x00")

    test_send_complex()

    ###################################

    def test_sending_failure():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):

            fake_request(10.0)

            xa = pmnc.transaction.create()
            xa.email_1.send(from_addr, "", "subject", "text")
            try:
                xa.execute()
            except ResourceError as e:
                assert e.code == 501 # syntax error in parameters or arguments
                assert e.recoverable and e.terminal

            assert loopback_queue.pop(10.0) is None

    test_sending_failure()

    ###################################

    def test_processing_failure():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            1 / 0

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.email_1.send(from_addr, to_addr, "subject", "text")
        xa.execute()

        with active_interface("email_1", **interface_config(process_request = process_request)):
            assert loopback_queue.pop(10.0) is None

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):
            assert loopback_queue.pop(10.0) is not None

    test_processing_failure()

    ###################################

    def test_processing_timeout():

        loopback_queue = InterlockedQueue()

        def process_request(request, response):
            sleep(pmnc.request.remain + 1.0)

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.email_1.send(from_addr, to_addr, "subject", "text")
        xa.execute()

        with active_interface("email_1", **interface_config(process_request = process_request)):
            assert loopback_queue.pop(10.0) is None

        def process_request(request, response):
            loopback_queue.push(request["message"])

        with active_interface("email_1", **interface_config(process_request = process_request)):
            assert loopback_queue.pop(10.0) is not None

    test_processing_timeout()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
