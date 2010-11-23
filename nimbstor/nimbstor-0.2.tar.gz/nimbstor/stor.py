#!/usr/pkg/bin/python2.6 -O

BLOCK_SIZE = 1048576 * 4

import os, sys, hashlib, lzma, aes, time, zlib, bz2, email, types
import cPickle as pickle
import adler64
from itertools import ifilter

class stor_buffer:
  def __init__(self, data = ""):
    self._data = [data]
    self._len = len(data)
    self._val = None

  def __len__(self):
    return self._len

  def push(self, data, left = False):
    self._len += len(data)
    if left: self._data.insert(0, data)
    else: self._data.append(data)
    self._val = None

  def _rmsize(self, size):
    new = self._val[size:]
    self._val = None
    self._data = [new]
    self._len = len(new)

  def pop(self, size = None):
    if self._val == None:
      self._val = "".join(self._data)
    if size == None:
      size = self._len
    ret = self._val[:size]
    self._rmsize(size)
    return ret

  def truncate(self, size = None):
    if size == None:
      self._data = []
      self._val = None
      self._len = 0
      return
    if self._val == None:
      self._val = "".join(self._data)
    self._rmsize(size)

  def value(self):
    if self._val == None:
      self._val = "".join(self._data)
    return self._val

class stor_stream:
  def __init__(self, password):
    self._pos = 0
    self._known_blocks = {}
    self._known_parts = {}
    self._known_metadata = []
    if password != None:
      self._aes = aes.Keysetup(hashlib.sha256(password).digest())
      self._pass = hashlib.md5(password).digest()
    else:
      self._aes = None
      self._pass = None
    self._archive = None

  def open(self, backend):
    self._backend = backend

  def checksum(self, data):
    ctx = hashlib.sha256()
    if self._pass != None: ctx.update(self._pass)
    ctx.update(data)
    return ctx.hexdigest().upper()

  def tell(self):
    return self._pos

  def archive(self):
    return self._archive

  def append_block_info(self, number, checksum1, checksum2, backend):
    checksum1 = int(checksum1, 16)
    if number == 0 and checksum2 not in self._known_metadata: self._known_metadata.append(checksum2)
    elif checksum1 == 0: self._known_parts.setdefault(checksum2, []).append(number)
    else: self._known_blocks.setdefault(checksum1, {}).setdefault(checksum2, []).append(number)

  def close(self):
    self._backend.close()

  def _decode_message(self, buffer, checksum, bufflen, meta = False):
    data = buffer
    try:
      if self._aes: data = self._aes.decrypt(data)
      if meta: data = bz2.decompress(data)
      else: data = self._decompress(data)
      if bufflen != 0 and len(data) > bufflen: data = data[:bufflen]
      if self.checksum(data) != checksum:
	raise SystemError()
    except: raise SystemError("Wrong password or invalid data")
    return data

class stor_output(stor_stream):
  def __init__(self, password, compression, parent, description, keywords, onlyifnew = False):
    stor_stream.__init__(self, password)
    self._metadata = {
	'description': description,
	'keywords': keywords,
	'metainfo': [],
	'timestamp': time.time(),
	'parent': parent,
	'compression': compression,
	'blocks': [],
	'size': 0,
    }
    self._buffer = stor_buffer()
    self._bufnum = 1
    self._bufsize = BLOCK_SIZE * 2
    self._checksum2 = None
    self._size = 0
    self._onlyifnew = onlyifnew
    if compression == ('lzma', 10): self._compress = lambda buffer: lzma.compress(buffer, {'level': 9, 'extreme': True})
    elif compression[0] == 'lzma': self._compress = lambda buffer: lzma.compress(buffer, {'level': compression[1]})
    elif compression[0] == 'gzip': self._compress = lambda buffer: zlib.compress(buffer, compression[1])
    elif compression[0] == 'bzip2': self._compress = lambda buffer: bz2.compress(buffer, compression[1])
    elif compression[0] == None: self._compress = lambda buffer: buffer
    else:
      raise SystemError("Unsupported compression type %s" % repr(compression))

  def write(self, buffer):
    buflen = len(buffer)
    self._pos += buflen
    self._buffer.push(buffer)
    self.flush_buffer(self._bufsize)

  def size(self):
    return self._metadata['usage']

  def set_metainfo(self, info):
    self._metadata['metainfo'] = info

  def set_parent(self, parent):
    self._metadata['parent'] = parent

  def block_exist(self, buffer, begin, end, checksum1):
    checksum2 = ctx.hexdigest().upper()
    if self._known_blocks[checksum1].has_key(checksum2):
      self._checksum2 = checksum2
      self._checksumblock = self._known_blocks[checksum1][checksum2]
      return True
    return False

  def close(self):
    self.flush_buffer(BLOCK_SIZE)
    self.commit_buffer(self._buffer.pop(), 0)
    if not self._onlyifnew or self._size > 0:
      self._metadata['usage'] = self._size
      self._metadata['size'] = self._pos
      buffer = pickle.dumps(self._metadata)
      self._bufnum = 0
      self.commit_buffer(buffer, 0, meta = True)
    stor_stream.close(self)

  def flush_buffer(self, tosize):
    while len(self._buffer) >= tosize:
      buffer = self._buffer.value()
      found, pos, dest, fcks, cks = adler64.search(self._known_blocks, self.block_exist, buffer, BLOCK_SIZE)
      if found:
	destlen = len(dest)
	if destlen == BLOCK_SIZE: self.commit_buffer(dest, fcks)
	elif destlen > 0: self.commit_buffer(dest, 0)
	checksum1 = "%016X" % cks
	self._metadata['blocks'].append((self._checksumblock, checksum1, self._checksum2, BLOCK_SIZE))
	self._bufnum += 1
	self._checksum2 = None
	self._buffer.truncate(pos + BLOCK_SIZE + destlen)
      else:
	self.commit_buffer(self._buffer.pop(BLOCK_SIZE), fcks)

  def commit_buffer(self, buffer, checksum1int, meta = False):
    checksum1 = "%016X" % checksum1int
    checksum2 = self.checksum(buffer)
    buflen = len(buffer)
    if checksum1int == 0 and self._known_parts.has_key(checksum2):
      self._metadata['blocks'].append((self._known_parts[checksum2], checksum1, checksum2, buflen))
    else:
      if meta: buffer = bz2.compress(buffer, 9)
      else: buffer = self._compress(buffer)
      bufrest = len(buffer) % 16
      if bufrest > 0:
	buffer = buffer + "\0" * (16 - bufrest)
      if self._aes:
	buffer = self._aes.encrypt(buffer)
      #if self._backend.should_mime():
      #  message = email.mime.multipart.MIMEMultipart()
      #  message.attach(email.mime.application.MIMEApplication(buffer))
      #  message = message.as_string()
      #else: message = buffer
      self._size += len(buffer)
      self._backend.write_buffer(buffer, self._bufnum, checksum1, checksum2)
      self._metadata['blocks'].append((self._bufnum, checksum1, checksum2, buflen))
    if self._bufnum != 0: self._bufnum += 1
    else: self._archive = checksum2

class stor_input(stor_stream):
  def __init__(self, password, archive):
    stor_stream.__init__(self, password)
    self._archive_checksum = archive
    self._buffer = ""
    self._bufferlen = 0
    self._bufferpos = 0
    self._archive = archive

  def open(self, backend):
    stor_stream.open(self, backend)
    if self._archive_checksum not in self._known_metadata:
      raise SystemError("Archive %s not found." % repr(self._archive_checksum))
    self._metadata = self._backend.read_buffer(0, "%016X" % 0, self._archive_checksum,
	lambda buf: pickle.loads(self._decode_message(buf, self._archive_checksum, 0, meta = True)))
    self._decompress = lambda buffer: bz2.decompress(buffer)
    if self._metadata['compression'][0] == 'lzma': self._decompress = lambda buffer: lzma.decompress(buffer)
    elif self._metadata['compression'][0] == 'gzip': self._decompress = lambda buffer: zlib.decompress(buffer)
    elif self._metadata['compression'][0] == 'bzip2': self._decompress = lambda buffer: bz2.decompress(buffer)
    elif self._metadata['compression'][0] == None: self._decompress = lambda buffer: buffer
    else: raise SystemError("Unsupported compression type %s" % repr(compression))
    self._blocks = self._metadata['blocks'][:]

  def read(self, size):
    while len(self._buffer) < size and len(self._blocks) > 0:
      num, ck1, ck2, blen = self._blocks.pop(0)
      data = self._backend.read_buffer(num, ck1, ck2, lambda buf: self._decode_message(buf, ck2, blen))
      self._buffer = self._buffer + data
      self._bufferlen += len(data)
    data = self._buffer[:size]
    self._buffer = self._buffer[len(data):]
    return data

  def metainfo(self):
    return self._metadata['metainfo']

class stor_util(stor_stream):
  def __init__(self, password):
    stor_stream.__init__(self, password)

  def search(self, keywords):
    result = []; parents = {}; errors = []
    checksum1 = "%016X" % 0
    for metadata in self._known_metadata:
      try: data = self._backend.read_buffer(0, checksum1, metadata,
            lambda buf: pickle.loads(self._decode_message(buf, metadata, 0, meta = True)))
      except Exception, err:
	errors.append((metadata, err))
	continue
      if len(keywords) > 0:
        weight = 0
        for kwd in keywords:
          for fnd in ifilter(lambda x: x == kwd, data['keywords']): weight += 10
          for fnd in ifilter(lambda x: kwd in x and x != kwd, data['keywords']): weight += 2
          if kwd.lower() in data['description'].lower(): weight += 5
          if kwd in repr(data['metainfo']): weight += 1
        result.append({
          'weight':       weight,
          'id':           metadata,
          'description':  data['description'],
          'keywords':     data['keywords'],
          'size':         data['size'],
          'usage':        data['usage'],
          'timestamp':    data['timestamp'],
          'parent':       data['parent'],
        })
      else:
        result.append({
          'weight':       0,
          'id':           metadata,
          'description':  data['description'],
          'keywords':     data['keywords'],
          'size':         data['size'],
          'usage':        data['usage'],
          'timestamp':    data['timestamp'],
          'parent':       data['parent'],
        })
      parents.setdefault(data['parent'], []).append(metadata)
    if len(keywords) > 0: result.sort(key = lambda x: x['weight'])
    else: result.sort(key = lambda x: x['description'])
    return (result, parents, errors)

  def keywords(self):
    checksum1 = "%016X" % 0
    keywords = {}
    errors = []
    for metadata in self._known_metadata:
      try: data = self._backend.read_buffer(0, checksum1, metadata,
            lambda buf: pickle.loads(self._decode_message(buf, metadata, 0, meta = True)))
      except Exception, err:
	errors.append((metadata, err))
	continue
      for kwd in data['keywords']:
	keywords[kwd] = keywords.get(kwd, 0) + 1
    return (keywords, errors)

__all__ = ('stor_output', 'stor_input', 'stor_util')
