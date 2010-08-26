from pyf.transport import encode_packet_flow, Packet
from pyf.transport.packets import decode_packet_flow
from pyf.splitter.inputsplitter import tokenize
import sys
import time
import socket
from itertools import chain
from pyjon.events import EventDispatcher

class ServerError(Exception):
    pass

class StationClient(object):
    __metaclass__ = EventDispatcher
    
    finished_message = 'good.'
    
    def __init__(self, host, port=6789,
                 waits_for_success=False,
                 separator='\r\n\0'):
        self.host = host
        self.port = port
        self.waits_for_success = waits_for_success
        self.separator = separator
        
    def __get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        
        return s
    
    def handle_message(self, sock, item):
        self.emit_event('message_received',
                        item)
        if item.type == 'error':
            sock.close()
            self.emit_event('failure', item)
            raise ServerError, item.message
        
        elif item.type == 'appinfo':
            self.emit_event('appinfo',
                            item.get('key'),
                            item.get('value'))
            
        elif item.type == 'success':
            self.emit_event('success', item)
            
        else:
            self.emit_event('other',
                            item)
        
    def receive_data(self, sock, remaining=""):
        sep = self.separator
        
        try:
            out = remaining + sock.recv(1024)
        except socket.error:
            out = remaining
            
        if out:
            if sep not in out:
                remaining += out
            else:
                items, remaining = tokenize(out, sep)
                
                return remaining, decode_packet_flow(iter(items),
                                                     separator=sep,
                                                     pure_flow=True)
        
        else:
            return remaining, []

    def call(self, content, header=None):
        s = self.__get_socket()
        
        if header is not None:
            if isinstance(header, dict):
                header = Packet(header)
                
            content = chain([header], content)
        
        remaining = ""
        sep = self.separator
        for i, data in enumerate(encode_packet_flow(content,
                                       separator=sep,
                                       compress=False)):
            if not i % 2:
                yield True
                
            s.sendall(data)
            
            s.setblocking(False)
            
            remaining, out_items = self.receive_data(s, remaining)
            for item in out_items:
                self.handle_message(s, item)
                yield item
                
#            try:
#                out = remaining + s.recv(1024)
#            except socket.error:
#                out = remaining
#                
#            if out:
#                if sep not in out:
#                    remaining += out
#                
#                else:
#                    items, remaining = tokenize(out, sep)
#                    
#                    for item in decode_packet_flow(iter(items),
#                                                   separator=sep,
#                                                   pure_flow=True):
#                        self.handle_message(sock, item)
#                        
#                        yield item
            s.setblocking(True)
        
        if self.waits_for_success:
            finished = False
            fsent = False
            s.setblocking(False)
            
            while not finished:
                if not fsent:
                    try:
                        s.sendall(self.finished_message + sep)
                        fsent = True
                    except socket.error:
                        pass
                
                remaining, out_items = self.receive_data(s, remaining)
                for item in out_items:
                    self.handle_message(s, item)
                    if item.get('type') == 'success':
                        finished = True
                        
                    yield item
        else:
            s.sendall(self.finished_message + sep)
            
        s.close()

if __name__ == '__main__':
    client = StationClient('127.0.0.1', 6789, True)
    
    def message_handler(message_packet):
        print message_packet
    
    client.add_listener('message_received', message_handler)
    flow = (Packet(dict(Field1=i+1,
                        Field2=('titi', 'tata')[i%2], num=i+1,
                        Field3=(i+1)*10))
            for i in range(10000))
    
    values = client.call(
         flow,
         header=dict(authtkt='125fa7e6398fdede0cdbfb700251ae934bffbaeemanager!',
                     action='launch_tube',
                     object_name='simple'))
    
    for i, value in enumerate(values):
        if not i % 5000:
            print i
            
        # Alternative way to handle messages, in the flow directly :
#        if isinstance(value, Packet):
#            print value