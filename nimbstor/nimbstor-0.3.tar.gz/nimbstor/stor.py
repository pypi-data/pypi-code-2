#!/usr/pkg/bin/python2.6

BLOCK_SIZE = 1048576 * 4

import os, sys, hashlib, lzma, aes, time, zlib, bz2, email, types
import cPickle as pickle
import adler64
from itertools import ifilter

class stor_buffer:
  """Manage buffer for nimbstor.

  Not a performant implementation, should be optimized one day.

  """

  def __init__(self, data = ""):
    """Initialize the buffer.

    Args:
      data (str): Preset buffer content.

    >>> stor_buffer("asdf").value()
    'asdf'
    """
    self._data = [data]
    self._len = len(data)
    self._val = None

  def __len__(self):
    """Return buffer content length.

    >>> len(stor_buffer("asdfqw"))
    6
    """
    return self._len

  def push(self, data, left = False):
    """Push data to the buffer.

    Args:
      data (str): Data to be pushed.
      left (bool): Push to begin of the buffer (default: False)

    >>> buf = stor_buffer('asdf')
    >>> buf.push('qwer')
    >>> buf.push('zxcv', True)
    >>> buf.value()
    'zxcvasdfqwer'
    """
    self._len += len(data)
    if left: self._data.insert(0, data)
    else: self._data.append(data)
    self._val = None

  def _rmsize(self, size):
    """Internal function to remove some data from buffer.

    Args:
      size (int): Amount of data to remove.

    This function expects, that self._val has correct value.

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.value()
    'asdfqwer'
    >>> buf._rmsize(3)
    >>> buf.value()
    'fqwer'
    """
    new = self._val[size:]
    self._val = None
    self._data = [new]
    self._len = len(new)

  def pop(self, size = None):
    """Pop some data from buffer.

    Args:
      size (int): Amount of data to pop.

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.pop(3)
    'asd'
    >>> buf.value()
    'fqwer'
    """
    if self._val == None: self._val = "".join(self._data)
    if size == None: size = self._len
    ret = self._val[:size]
    self._rmsize(size)
    return ret

  def truncate(self, size = None):
    """Remove some amount of data from buffer.

    Args:
      size (int): Amount of data to remove (default: all).

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.truncate(3)
    >>> buf.value()
    'fqwer'
    """
    if size == None:
      self._data = []
      self._val = None
      self._len = 0
      return
    if self._val == None: self._val = "".join(self._data)
    self._rmsize(size)

  def value(self):
    """Return the buffer value.

    >>> stor_buffer('asdf').value()
    'asdf'
    """
    if self._val == None: self._val = "".join(self._data)
    return self._val

class stor_stream:
  """Base class for storage streams."""

  def __init__(self, password = None):
    """Initialize base stream.

    Args:
      password (str): Optional password to enable encryption.

    >>> stor_stream('asdf')._pass == stor_stream('qwer')._pass
    False
    """
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
    """Initialize and open the stream.

    This function is used in backends to connect the stor_stream with an
    backend.
    """
    self._backend = backend

  def checksum(self, data):
    """Calculate checksum for given data.
    
    Args:
      data (str): Data buffer.

    Checksum is calculated on data and the password, given in constructor.
    """
    ctx = hashlib.sha256()
    if self._pass != None: ctx.update(self._pass)
    ctx.update(data)
    return ctx.hexdigest().upper()

  def tell(self):
    """Return the current position in stream."""
    return self._pos

  def archive(self):
    """Tell the archive name.

    The archive name (checksum) is on input streams immediatly available, but
    on output streams is only available after close.
    """
    return self._archive

  def append_block_info(self, number, checksum1, checksum2, backend):
    """Register block info.

    Args:
      number (int): Block number.
      checksum1 (int): Adler64 checksum.
      checksum2 (str): Block checksum as returned by self.checksum(data)
      backend (object): Backend reference, which can read this block.

    Backends use this function to register known blocks.
    """
    checksum1 = int(checksum1, 16)
    if number == 0 and checksum2 not in self._known_metadata: self._known_metadata.append(checksum2)
    elif checksum1 == 0: self._known_parts.setdefault(checksum2, []).append(number)
    else: self._known_blocks.setdefault(checksum1, {}).setdefault(checksum2, []).append(number)

  def close(self):
    """Close the stream.

    The backends close will be also called.
    """
    self._backend.close()

  def _decode_message(self, buffer, checksum, bufflen, meta = False):
    """Internal function to decode message.

    Args:
      buffer (str): Data buffer.
      checksum (str): Checksum as returned by self.checksum(data)
      bufflen (str): Correct data length to return or 0.
      meta (boolean): Meta blocks are handled somewhat different.
    """
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
  """Storage output stream."""

  def __init__(self, password, compression, parent, description, keywords, onlyifnew = False):
    """Initialization of output stream.

    Args:
      password (str): Password for encryption (None to disable encryption).
      compression ((str, int)): Compression type as tupple of (method, level).
      parent (str): Name of the parent archive or None.
      description (str): Description of archive.
      keywords (list): List of keyword strings.
      onlyifnew (boolean): Set to True to commit empty (fully deduplicated) archives.
    """
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
    """Write function.

    Use this function to write data to the stream.
    """
    buflen = len(buffer)
    self._pos += buflen
    self._buffer.push(buffer)
    self.flush_buffer(self._bufsize)

  def size(self):
    """Returns the size (length) of stream."""
    return self._metadata['usage']

  def set_metainfo(self, info):
    """Set the meta information, user defined."""
    self._metadata['metainfo'] = info

  def set_parent(self, parent):
    """Set the parent archive name."""
    self._metadata['parent'] = parent

  def block_exist(self, buffer, begin, end, checksum1):
    """Checks if the given block already exists.

    Args:
      buffer (str): Data buffer.
      begin (int): Block start position.
      end (int): Block end position.

    Call only if the block with given Adler64 checksum really exist (it means
    that it was registred with append_block_info).
    """
    checksum2 = ctx.hexdigest().upper()
    if self._known_blocks[checksum1].has_key(checksum2):
      self._checksum2 = checksum2
      self._checksumblock = self._known_blocks[checksum1][checksum2]
      return True
    return False

  def close(self):
    """Close the output stream.

    This function write also the metadata, without metadata the archive does
    not exist.
    """
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
    """Flush data from buffer.
    
    This function do the deduplication with Adler64.
    """
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
    """Write data to the beckend.

    Args:
      buffer (str): Block buffer.
      checksum1int (int): Adler64 checksum of the buffer.
      meta (boolean): Set to True if the buffer contains metadata.
    """
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
      self._size += len(buffer)
      self._backend.write_buffer(buffer, self._bufnum, checksum1, checksum2)
      self._metadata['blocks'].append((self._bufnum, checksum1, checksum2, buflen))
    if self._bufnum != 0: self._bufnum += 1
    else: self._archive = checksum2

class stor_input(stor_stream):
  """Storage input stream."""

  def __init__(self, password, archive):
    """Initialization of input stream.

    Args:
      password (str): Password for decrypting data (or None).
      archive (str): Name of the archive (checksum).
    """
    stor_stream.__init__(self, password)
    self._archive_checksum = archive
    self._buffer = ""
    self._bufferlen = 0
    self._bufferpos = 0
    self._archive = archive

  def open(self, backend):
    """Initialize backend for reading.

    To read data, we need to read the metadata first. This function should be
    called by backend, if the backend is ready.
    """
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
    """Read data of given size.

    Use this function to read the data.
    """
    while len(self._buffer) < size and len(self._blocks) > 0:
      num, ck1, ck2, blen = self._blocks.pop(0)
      data = self._backend.read_buffer(num, ck1, ck2, lambda buf: self._decode_message(buf, ck2, blen))
      self._buffer = self._buffer + data
      self._bufferlen += len(data)
    data = self._buffer[:size]
    self._buffer = self._buffer[len(data):]
    return data

  def metainfo(self):
    """Returns user defined metadata."""
    return self._metadata['metainfo']

class stor_util(stor_stream):
  """Storage stream utility.

  This storage type is used to manage the archives, f.e. to search, copy,
  remove, ...
  """

  def __init__(self, password):
    stor_stream.__init__(self, password)
    self._errors = []
    self._metadata_data = {}

  def open(self, backend):
    stor_stream.open(self, backend)
    checksum1 = "%016X" % 0
    for metadata in self._known_metadata:
      try: data = self._backend.read_buffer(0, checksum1, metadata,
            lambda buf: pickle.loads(self._decode_message(buf, metadata, 0, meta = True)))
      except Exception, err:
	self._errors.append((metadata, err))
	continue
      self._metadata_data[metadata] = data

  def search(self, keywords):
    """Search for an archive.

    Args:
      keywords (list): List of strings, for which should be searched.

    The search function search for an archive, gives each archive weight (how
    good it matches with given keywords), sort it in ascend order and return
    the list of archvies, the dependecies between archives and list of errors
    on search.
    """
    result = []; parents = {}
    for metadata, data in self._metadata_data.items():
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
    return (result, parents, self._errors)

  def keywords(self):
    """Return list of used keywords."""
    keywords = {}
    for metadata, data in self._metadata_data.items():
      for kwd in data['keywords']:
	keywords[kwd] = keywords.get(kwd, 0) + 1
    return (keywords, self._errors)

__all__ = ('stor_output', 'stor_input', 'stor_util')
