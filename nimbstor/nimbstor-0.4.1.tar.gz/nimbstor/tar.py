#!/usr/pkg/bin/python2.6 -O

import os, sys, time
from tarfile import TarFile, PAX_FORMAT, open as taropen, filemode, CHRTYPE, BLKTYPE, SYMTYPE, LNKTYPE, DIRTYPE

class NimbTarFile(TarFile):
  def __init__(self, verbose, *options, **keywords):
    TarFile.__init__(self, *options, **keywords)
    self._recorded_files_list = []
    self._verbose = verbose

  def addfile(self, tarinfo, fileobj = None):
    self._recorded_files_list.append(tarinfo.get_info('UTF-8', 'replace'))
    if self._verbose:
      print tarinfo.name
    return TarFile.addfile(self, tarinfo, fileobj)

  def recorded_files(self):
    return self._recorded_files_list

def create_archive(output, files, verbose = False):
  tar = NimbTarFile(
      verbose = verbose,
      fileobj = output,
      mode = 'w',
      encoding = PAX_FORMAT)
  for filename in files:
    tar.add(filename, recursive = True)
  tar.close()
  output.set_metainfo(tar.recorded_files())

def extract_archive(input, files = [], verbose = False):
  tar = taropen(fileobj = input, mode = 'r|')
  member = tar.next()
  while member:
    if len(files) > 0:
      if member.name in files:
        tar.extract(member)
        if verbose:
          print member.name
          sys.stdout.flush()
    else:
      tar.extract(member)
      if verbose:
        print member.name
        sys.stdout.flush()
    member = tar.next()
  tar.close()
  input.close()

def list_archive(input, files = [], verbose = False):
  for finfo in input.metainfo():
    if len(files) > 0 and finfo['name'] not in files: continue
    if verbose:
      print filemode(finfo['mode']),
      print "%s/%s" % (finfo['uname'] or finfo['uid'], finfo['gname'] or finfo['gid']),
      if finfo['type'] == CHRTYPE or finfo['type'] == BLKTYPE:
        print "%10s" % ("%d,%d" % (finfo['devmajor'], finfo['devminor'])),
      else: print "%10d" % finfo['size'],
      print "%d-%02d-%02d %02d:%02d:%02d" % time.localtime(finfo['mtime'])[:6],
    print finfo['name'],
    if verbose:
      if finfo['type'] == SYMTYPE: print "->", finfo['linkname'],
      if finfo['type'] == LNKTYPE: print "link to", finfo['linkname'],
    print
  input.close()

def search_archive(util, keywords, verbose = False):
  result, parents, errors = util.search(keywords)
  print "% 6s" % "WEIGHT",
  print "%- 64s" % "ARCHIVE",
  print " %- 17s" % "CREATED",
  print " %- 13s" % "SIZE",
  print " %- 13s" % "USAGE",
  print "DESCRIPTION"
  for res in result:
    if not verbose and parents.has_key(res['id']): continue
    print "% 6d" % res['weight'],
    print res['id'],
    print " " + time.strftime("%F %R", time.localtime(res['timestamp'])),
    print " %- 13d" % res['size'],
    print " %- 13d" % res['usage'],
    print " " + res['description']
  if verbose:
    for metadata, error in errors:
      print "ERROR:", repr(error)

def list_keywords(util, verbose = False):
  keywords, errors = util.keywords()
  keywords = keywords.items()
  keywords.sort(key = lambda x: x[0])
  print "%- 30s%- 5s" % ("KEYWORD", "USAGE")
  for kwd, usage in keywords:
    print "%- 30s%- 5d" % (kwd, usage)
  if verbose:
    for metadata, error in errors:
      print "ERROR:", metadata, repr(error)

def copy_archive(source_stor, dest_stor, archive, verbose = False):
  block_list = source_stor.blocks(archive)
  if verbose:
    sys.stdout.write("Copy %d blocks " % len(block_list))
    sys.stdout.flush()
  for number, checksum1, checksum2, length in block_list:
    if not dest_stor.block_exists(number, checksum1, checksum2):
      buffer = source_stor.read_buffer(number, checksum1, checksum2).next()
      dest_stor.write_buffer(buffer, number, checksum1, checksum2)
      if verbose: sys.stdout.write('.'); sys.stdout.flush()
    else:
      if verbose: sys.stdout.write('+'); sys.stdout.flush()
  if verbose:
    sys.stdout.write(' done.\n')

__all__ = (
    'create_archive',
    'extract_archive',
    'list_archive',
    'search_archive',
    'list_keywords',
    'copy_archive',
)
