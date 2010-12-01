# This file is taken from the Mongrel2 source tree:
#
# Copyright (c) 2010, Zed A. Shaw and Mongrel2 Project Contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the Mongrel2 Project, Zed A. Shaw, nor the names
#       of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:
    import json
except: # pragma nocover
    import simplejson as json


def parse_netstring(ns):
    len, rest = ns.split(':', 1)
    len = int(len)
    assert rest[len] == ',', "Netstring did not end in ','"
    return rest[:len], rest[len+1:]

class Request(object):

    def __init__(self, sender, conn_id, path, headers, body):
        self.sender = sender
        self.path = path
        self.conn_id = conn_id
        self.headers = headers
        self.body = body
        
        if self.headers['METHOD'] == 'JSON':
            self.data = json.loads(body)
        else:
            self.data = {}

    @staticmethod
    def parse(msg):
        sender, conn_id, path, rest = msg.split(' ', 3)
        headers, rest = parse_netstring(rest)
        body, _ = parse_netstring(rest)

        headers = json.loads(headers)

        return Request(sender, conn_id, path, headers, body)

    def is_disconnect(self):
        if self.headers.get('METHOD') == 'JSON':
            return self.data['type'] == 'disconnect'

    def should_close(self):
        # TODO: hmm, these headers need to be normalized or we need a new
        # data structure for it so we can do case-insensitive handling
        if self.headers.get('connection') == 'close':
            return True
        elif self.headers.get('VERSION') == 'HTTP/1.0':
            return True
        else:
            return False

