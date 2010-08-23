import asynchat
import logging
import multiprocessing

from mopidy.frontends.mpd.protocol import ENCODING, LINE_TERMINATOR, VERSION
from mopidy.utils.log import indent
from mopidy.utils.process import pickle_connection

logger = logging.getLogger('mopidy.frontends.mpd.session')

class MpdSession(asynchat.async_chat):
    """
    The MPD client session. Keeps track of a single client and passes its
    MPD requests to the dispatcher.
    """

    def __init__(self, server, client_socket, client_socket_address,
            core_queue):
        asynchat.async_chat.__init__(self, sock=client_socket)
        self.server = server
        self.client_address = client_socket_address[0]
        self.client_port = client_socket_address[1]
        self.core_queue = core_queue
        self.input_buffer = []
        self.set_terminator(LINE_TERMINATOR.encode(ENCODING))

    def start(self):
        """Start a new client session."""
        self.send_response(u'OK MPD %s' % VERSION)

    def collect_incoming_data(self, data):
        """Collect incoming data into buffer until a terminator is found."""
        self.input_buffer.append(data)

    def found_terminator(self):
        """Handle request when a terminator is found."""
        data = ''.join(self.input_buffer).strip()
        self.input_buffer = []
        try:
            request = data.decode(ENCODING)
            logger.debug(u'Input from [%s]:%s: %s', self.client_address,
                self.client_port, indent(request))
            self.handle_request(request)
        except UnicodeDecodeError as e:
            logger.warning(u'Received invalid data: %s', e)

    def handle_request(self, request):
        """Handle request by sending it to the MPD frontend."""
        my_end, other_end = multiprocessing.Pipe()
        self.core_queue.put({
            'command': 'mpd_request',
            'request': request,
            'reply_to': pickle_connection(other_end),
        })
        my_end.poll(None)
        response = my_end.recv()
        if response is not None:
            self.handle_response(response)

    def handle_response(self, response):
        """Handle response from the MPD frontend."""
        self.send_response(LINE_TERMINATOR.join(response))

    def send_response(self, output):
        """Send a response to the client."""
        logger.debug(u'Output to [%s]:%s: %s', self.client_address,
            self.client_port, indent(output))
        output = u'%s%s' % (output, LINE_TERMINATOR)
        data = output.encode(ENCODING)
        self.push(data)
