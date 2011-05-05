#!/usr/bin/env python3
# vim:fileencoding=utf-8

'''
path.py - An object that handles path more easily.

lilydjwg <lilydjwg@gmail.com>

2010 年 11 月 13 日
'''

# Inspired by http://www.jorendorff.com/articles/python/path ver 3.0b1

import os
from datetime import datetime

__version__ = '0.2'

class path:
  def __init__(self, string='.'):
    self.value = str(string)

  def __str__(self):
    return self.value

  def __repr__(self):
    return '%s(%r)' % (self.__class__.__name__, str(self))

  def __hash__(self):
    st = self.stat()
    return int('%d%d%02d%d' % (st.st_ino, st.st_dev,
        len(str(st.st_ino)), len(str(st.st_dev))))

  def __add__(self, more):
    return self.__class__(self).join(more)

  def __radd__(self, more):
    return self.__class__(self).head(more)

  def __eq__(self, another):
    '''Determine two given files are same or not.'''
    return os.path.samefile(self.value, str(another))

  def __contains__(self, another):
    '''Determine 'another' belongs to given path or not.'''
    child = os.path.abspath(str(another))
    parent = self.abspath
    if parent == child:
      return True
    if child.startswith(parent) and child[len(parent)] == '/':
      return True
    else:
      return False

  def __lt__(self, another):
    return str.__lt__(str(self), str(another))

  @property
  def abspath(self):
    return os.path.abspath(self.value)

  @property
  def basename(self):
    return os.path.basename(self.value)

  @property
  def rootname(self):
    '''Eliminate ext of basename'''
    return os.path.splitext(self.basename)[0]

  @property
  def extension(self):
    '''Ext name'''
    return os.path.splitext(self.basename)[1]

  @property
  def realpath(self):
    return os.path.realpath(self.value)

  @property
  def mode(self):
    return self.stat().st_mode

  @property
  def inode(self):
    return self.stat().st_ino

  @property
  def dev(self):
    return self.stat().st_dev

  @property
  def size(self):
    '''Display file size in byte'''
    return self.stat().st_size

  @property
  def atime(self):
    return datetime.fromtimestamp(self.stat().st_atime)
  @property
  def mtime(self):
    return datetime.fromtimestamp(self.stat().st_mtime)
  @property
  def ctime(self):
    return datetime.fromtimestamp(self.stat().st_ctime)
  def stat(self):
    return os.stat(self.value)
  def access(self, mode):
    return os.access(self.value, mode)
  def olderthan(self, another):
    '''Compare last modified time of the file'''
    if not isinstance(another, path):
      raise TypeError('Cannot compare with non path object')
    return self.mtime < another.mtime
  def newerthan(self, another):
    return another.olderthan(self)
  def readlink(self):
    return os.readlink(self.value)
  def join(self, *more):
    '''join path'''
    self.value = os.path.join(self.value, *(str(x) for x in more))
    return self

  def head(self, *more):
    '''join path at the beginning'''
    header = os.path.join(*(str(x) for x in more))
    self.value = os.path.join(header, self.value)
    return self

  def expanduser(self):
    self.value = os.path.expanduser(self.value)
    return self

  def expandvars(self):
    self.value = os.path.expandvars(self.value)
    return self

  def normpath(self):
    self.value = os.path.normpath(self.value)
    return self

  def expand(self):
    '''expand everything, include expanduser, expandvars and normpath'''
    self.expanduser().expandvars().normpath()
    return self

  def toabspath(self):
    '''tranform given path to absolute path'''
    self.value = os.path.abspath(self.value)
    return self

  def torealpath(self):
    '''tranform given path to real path'''
    self.value = os.path.realpath(self.value)
    return self

  def islink(self):
    return os.path.islink(self.value)

  def isdir(self):
    return os.path.isdir(self.value)

  def isfile(self):
    return os.path.isfile(self.value)

  def exists(self):
    return os.path.exists(self.value)

  def lexists(self):
    return os.path.lexists(self.value)

  def parent(self):
    '''parent directory'''
    return self.__class__(self.value).join('..').normpath()

  def list(self, nameonly=False):
    '''
    list everthing in give path，like os.listdir()，exclude . and ..

    nameonly determines to return name or path object
    '''
    if nameonly:
      return os.listdir(self.value)
    else:
      return [self + self.__class__(x) for x in os.listdir(self.value)]

  def dirs(self, nameonly=False):
    '''all directories in given path'''
    if nameonly:
      return [x.basename for x in self.list() if x.isdir()]
    else:
      return [x for x in self.list() if x.isdir()]

  def files(self, nameonly=False):
    '''all files in given path'''
    if nameonly:
      return [x.basename for x in self.list() if x.isfile()]
    else:
      return [x for x in self.list() if x.isfile()]

  def rmdir(self):
    os.rmdir(self.value)
    return self

  def unlink(self, recursive=False):
    '''delete given path'''
    if self.isdir():
      if recursive:
        for x in self.list():
          x.unlink(True)
      os.rmdir(self.value)
    else:
      os.unlink(self.value)

    return self

  def linksto(self, target, hardlink=False):
    target = str(target)
    if hardlink:
      os.link(target, self.value)
    else:
      os.symlink(target, self.value)

  def mkdir(self, *dirs):
    '''
    Use given path to make directory, in the meanwhile make parent directory;
    or make directory in given path, the given path must exist
    '''
    if dirs:
      if self.exists():
        for d in dirs:
          (self+d).mkdir()
      else:
        raise OSError(2, os.strerror(2), str(self))
    else:
      if self.parent().isdir():
        os.mkdir(str(self))
      elif not self.parent().exists():
        self.parent().mkdir()
        os.mkdir(str(self))
      else:
        raise OSError(17, os.strerror(17), str(self.parent()))

  def rename(self, newname):
    '''Rename file，and refresh path object itself'''
    os.rename(self.value, newname)
    self.value = newname
    return self

  def copyto(self, newpath):
    '''Copy file，and refresh object itself'''
    newpath = self.__class__(newpath)
    if newpath.isdir():
      newpath.join(self.basename)
    import shutil
    shutil.copy2(self.value, newpath.value)
    self.value = newpath.value

  def moveto(self, newpath):
    '''Move file，and refresh object itself'''
    newpath = self.__class__(newpath)
    if newpath.isdir():
      newpath.join(self.basename)
    import shutil
    shutil.move(self.value, newpath.value)
    self.value = newpath.value

  def glob(self, pattern):
    '''Return list'''
    import glob
    return list(map(path, glob.glob(str(self+pattern))))

  def copy(self):
    '''Copy object'''
    return self.__class__(self.value)

  def open(self, mode='r', buffering=2, encoding=None, errors=None,
      newline=None, closefd=True):
    '''Open file'''
    #XXX 文档说buffering默认值为 None，但事实并非如此。使用full buffering好了
    return open(self.value, mode, buffering, encoding, errors, newline, closefd)

  def traverse(self):
    '''Traverse the directory'''
    for i in self.list():
      yield i
      if i.isdir():
        for j in i.traverse():
          yield j

class sha1path(path):
  '''Determine two files have same path or not with sha1'''
  def __eq__(self, another):
    # 先比较文件大小
    if self.size != another.size:
      return False
    return self.sha1() == another.sha1()
  def sha1(self, force=False):
    '''If force is true, reads the file again'''
    if not hasattr(self, '_sha1') or force:
      import hashlib
      s = hashlib.sha1()
      with self.open('rb') as f:
        while True:
          data = f.read(4096)
          if data:
            s.update(data)
          else:
            break
      self._sha1 = s.hexdigest()
    return self._sha1
