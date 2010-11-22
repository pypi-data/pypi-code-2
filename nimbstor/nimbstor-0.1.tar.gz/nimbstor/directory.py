#!/usr/pkg/bin/python2.6 -O

import os, sys, random

def read_directory_content(directory):
  content = []
  for fname in os.listdir(directory):
    number, checksum1, checksum2 = fname.split('.')
    number = int(number)
    content.append((number, checksum1, checksum2))
  return content

class directory_backend:
  def __init__(self, nimbstor, directorylist, redundancy = 1):
    self._directorylist = directorylist
    self._redundancy = redundancy
    self._nimbstor = nimbstor
    self._block_directory = {}
    for directory in directorylist:
      for number, checksum1, checksum2 in read_directory_content(directory):
	self._block_directory.setdefault((number, checksum1, checksum2), []).append(directory)
	self._nimbstor.append_block_info(number, checksum1, checksum2)
    self._nimbstor.open(self)

  def write_buffer(self, buffer, number, checksum1, checksum2):
    written_count = 0
    write_dirs = self._directorylist[:]
    while written_count < self._redundancy:
      if len(write_dirs) == 0 and written_count == 0:
	raise SystemError("Could not write to destination directories")
      elif len(write_dirs) == 0 and written_count > 0:
	sys.stderr.write("Could only write %d blocks for %s\n" % (written_count, repr((number, checksum1, checksum2))))
	break
      directory = write_dirs.pop(random.randint(0, len(write_dirs) - 1))
      fname = os.path.join(directory, "%07d.%s.%s" % (number, checksum1, checksum2))
      try:
	fd = open(fname, 'w')
	fd.write(buffer)
	fd.close()
      except: continue
      written_count += 1

  def read_buffer(self, number, checksum1, checksum2):
    directorylist = self._block_directory[(number, checksum1, checksum2)]
    buffer = None
    for directory in directorylist:
      try:
	fname = os.path.join(directory, "%07d.%s.%s" % (number, checksum1, checksum2))
	fd = open(fname, 'r')
	buffer = fd.read()
	fd.close()
	break
      except: pass
    if buffer == None:
      raise SystemError("Failed to read block: " + repr((number, checksum1, checksum2)))
    return buffer

  def should_mime(self):
    return False

  def close(self):
    pass

__all__ = ('directory_backend',)
