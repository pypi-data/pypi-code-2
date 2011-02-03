# -*- coding: utf-8 -*-
'''Common test data for unit tests.'''
# pylint: disable=R0904

## Created: 2010-09-16 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

from io import BytesIO
from hashlib import md5

from matanui import request
from matanui import storerinterface

GOOD_GRIDFS = BytesIO('Hello Test!')
GOOD_GRIDFS.chunk_size = 5
GOOD_GRIDFS.name = '/spam/eggs.txt'
GOOD_GRIDFS.length = len(GOOD_GRIDFS.getvalue())
GOOD_GRIDFS.md5 = md5(GOOD_GRIDFS.getvalue()).hexdigest()
GOOD_GRIDFS.content_type = 'text/plain'
GOOD_GRIDFS.object_id = '4c81ed79634ca0c4e8445967'

GOOD_CONTENT = storerinterface.ContentObject() 
GOOD_CONTENT.data = GOOD_GRIDFS
GOOD_CONTENT.block_size = GOOD_GRIDFS.chunk_size
GOOD_CONTENT.filename = GOOD_GRIDFS.name
GOOD_CONTENT.length = GOOD_GRIDFS.length
GOOD_CONTENT.checksum = GOOD_GRIDFS.md5
GOOD_CONTENT.content_type = GOOD_GRIDFS.content_type
GOOD_CONTENT.object_id = GOOD_GRIDFS.object_id

GOOD_METADATA = {'accessMode': 0600,
                 'metadata': {
                     'project': 'Operation Petticoat',
                     'account': 4711,
                     'samples': [42, 17],
                     'temperature': -273.15,
                     'codes': {'mine': 42, 'theirs': 'xxx'}}}

GOOD_INPUT = storerinterface.ContentObject()
GOOD_INPUT.data = BytesIO('Hello Test!')
GOOD_INPUT.filename = '/spam/eggs.txt'

GOOD_APIS = [('application/x.matanui.content-v0.1',
              (request.CONTENT, None, '0.1')),
             ('application/x.matanui.info-v0.1',
              (request.INFO, None, '0.1')),
             ('application/x.matanui.metadata-v0.1+json',
              (request.METADATA, 'json', '0.1')),
             ('application/x.matanui.list-v0.1+json',
              (request.LIST, 'json', '0.1')),
             ('application/x.matanui.content',
              (request.CONTENT, None, '0.1')),
             ('application/x.matanui.info',
              (request.INFO, None, '0.1')),
             ('application/x.matanui.metadata+json',
              (request.METADATA, 'json', '0.1')),
             ('application/x.matanui.list+json',
              (request.LIST, 'json', '0.1')),
             ('*/*',
              (request.CONTENT, None, '0.1'))]

WRONG_APIS = ['application/x.matanui.content-v0.42',
              'application/x.matanui.info-v1.42',
              'application/x.matanui.metadata-v0.42',
              'application/x.matanui.metadata-v0.42+json',
              'application/x.matanui.metadata-v0.1',
              'application/x.matanui.metadata',
              'application/x.matanui.list-v0.42',
              'application/x.matanui.list-v0.42+json',
              'application/x.matanui.list-v0.1',
              'application/x.matanui.list']

TEST_ENTRIES = ['/foo/bar.txt',
                '/foo/bar.txtx',
                '/foo/bar.png',
                '/foo/baz.txt',
                '/foo/baz.png',
                '/foo/bla.txt',
                '/foo/spam/eggs.txt',
                '/foo/spam/eggs.png',
                '/foo/spam.txt/eggs.txt',
                '/foo/bacon/eggs.png',
                '/spam/eggs.txt',
                '/spam/eggs.png']
TEST_QUERIES = {'/foo': ['/foo'],
                '/foo/': ['/foo/bar.txt',
                          '/foo/bar.txtx',
                          '/foo/bar.png',
                          '/foo/baz.txt',
                          '/foo/baz.png',
                          '/foo/bla.txt',
                          '/foo/spam',
                          '/foo/spam.txt',
                          '/foo/bacon'],
                '/foo/*': ['/foo/bar.txt',
                           '/foo/bar.txtx',
                           '/foo/bar.png',
                           '/foo/baz.txt',
                           '/foo/baz.png',
                           '/foo/bla.txt',
                           '/foo/spam',
                           '/foo/spam.txt',
                           '/foo/bacon'],
                '/foo/*.txt': ['/foo/bar.txt',
                               '/foo/baz.txt',
                               '/foo/bla.txt',
                               '/foo/spam.txt'],
                '/foo/bar.*': ['/foo/bar.txt',
                               '/foo/bar.txtx',
                               '/foo/bar.png'],
                '/foo/ba?.txt': ['/foo/bar.txt',
                                 '/foo/baz.txt'],
                '/foo/ba?.*': ['/foo/bar.txt',
                               '/foo/bar.txtx',
                               '/foo/bar.png',
                               '/foo/baz.txt',
                               '/foo/baz.png'],
                '/bacon': [],
                '/bacon/': [],
                '/bacon/*': [],
                '/bacon/ba?.*': []}

# Each entry: (<call params>, <result>)
PRIVILEGE_TESTS = [(({'accessMode': None, 'owner': 'brian'},
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': None, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ), True),
                   (({'accessMode': None, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': None, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_WRITE), True),
                   (({'accessMode': None, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': None, 'owner': None}, 
                     'brian', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': None, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ_WRITE), True),
                   (({'accessMode': None, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ_WRITE), False),
                   (({'accessMode': None, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ_WRITE), False),
                 
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ), False),
                   (({'accessMode': 0400, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ), False),
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0400, 'owner': None}, 
                     'brian', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ_WRITE), False),
                   (({'accessMode': 0400, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ_WRITE), False),
                   (({'accessMode': 0400, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ_WRITE), False),
                 
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ), False),
                   (({'accessMode': 0600, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ), False),
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_WRITE), True),
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0600, 'owner': None}, 
                     'brian', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ_WRITE), True),
                   (({'accessMode': 0600, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ_WRITE), False),
                   (({'accessMode': 0600, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ_WRITE), False),
                 
                   (({'accessMode': 0602, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': 0604, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ), True),
                   (({'accessMode': 0604, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ), True),
                   (({'accessMode': 0604, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_WRITE), True),
                   (({'accessMode': 0604, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0604, 'owner': None}, 
                     'brian', storerinterface.PRIV_WRITE), False),
                   (({'accessMode': 0604, 'owner': 'brian'}, 
                     'brian', storerinterface.PRIV_READ_WRITE), True),
                   (({'accessMode': 0604, 'owner': 'brian'}, 
                     'loretta', storerinterface.PRIV_READ_WRITE), False),
                   (({'accessMode': 0604, 'owner': None}, 
                     'brian', storerinterface.PRIV_READ_WRITE), False)]
    
    

def make_dummy_fs_entries(filenames):
    metadata_skel = {'length': 42,
                     'chunkSize': 262144,
                     'uploadDate': 1294434408990 / 1000.}
    result = []
    for name in filenames:
        item = metadata_skel.copy() 
        item['filename'] = name
        item['_id'] = str(md5(name).hexdigest())[:24]
        item['md5'] = str(md5(name + 'spam and eggs').hexdigest())
        result.append(item)
    return result
    
