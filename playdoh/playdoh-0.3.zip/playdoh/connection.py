from debugtools import *
from userpref import *
import multiprocessing, multiprocessing.connection, threading, logging
from multiprocessing.connection import Listener, Client
import os, sys, zlib, cPickle, time, traceback, gc, socket, base64, math, binascii, hashlib

BUFSIZE = 1024*32
try:
    LOCAL_IP = socket.gethostbyname(socket.gethostname())
except:
    LOCAL_IP = '127.0.0.1'

__all__ = ['accept', 'connect', 'LOCAL_IP']

class Connection(object):
    """
    Handles chunking and compression of data.
    
    To minimise data transfers between machines, we can use data compression,
    which this Connection handles automatically.
    """
    def __init__(self, conn, chunked=False, compressed=False):
        self.conn = conn
        self.chunked = chunked
        self.compressed = compressed
        self.BUFSIZE = BUFSIZE
        
    def send(self, obj):
        s = cPickle.dumps(obj, -1)
        self.conn.send(s)
            
    def recv(self):
        trials = 5
        for i in xrange(trials):
            try:
                s = self.conn.recv()
                break
            except Exception as e:
                log_warn("Connection error (%d/%d): %s" % (i+1, trials, str(e)))
                time.sleep(.1*2**i)
                if i==trials-1: return None
        return cPickle.loads(s)
    
    def close(self):
        if self.conn is not None:
            r = self.conn.close()
            self.conn = None




def accept(address):
    """
    Accept a connection and return a Connection object.
    """
    listener = Listener(address, authkey=USERPREF['authkey'])
    conn = listener.accept()
    client = listener.last_accepted
    return Connection(conn), client[0]

def connect(address):
    """
    Connect to a server and return a Connection object.
    """
    trials = 5
    conn = None
    for i in xrange(trials):
        try:
            conn = Client(address, authkey=USERPREF['authkey'])
            break
        except Exception as e:
            log_debug("Connection error: %s, trying again... (%d/%d)" % (str(e), i+1, trials))
            time.sleep(.1*2**i)
    if conn is None:
        log_warn("Connection error")
        return None
    return Connection(conn)
