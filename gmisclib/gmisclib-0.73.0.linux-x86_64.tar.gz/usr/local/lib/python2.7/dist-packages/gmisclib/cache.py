
import os
import sys
import stat
import types
import hashlib
import cPickle
import threading

import die
import gpkmisc

UnpicklingError = cPickle.UnpicklingError

def cachepath(f, tail='', root=''):
	"""OBSOLETE:
	Return a pathname suitable for cacheing some result.
	@return: C{(path_to_root,path_with_tail)}.   C{Path_to_root} is/will be a directory;
		C{path_with_tail} is a path to a data file within that directory.
		Normally, the actual cache is at the location
		C{os.path.join(path_to_root,path_with_tail)} on the disk;
		that is what you would pass as the C{fname} argument to L{load_cache} or
		L{dump_cache}.
	@rtype: C{tuple(str, str)}
	@param f: An arbitrary key, could be a pathname or a tuple of information about a file.
	@type f: often L{str}, but could be anything convertible to a L{str} via L{repr}.
	@param tail: something to add at the end of the constructed path.
	@type tail: str or None
	@except ValueError: if C{suffix_to_del} is specified and C{f} doesn't end that way.
	"""
	if len(f)==0:
		raise ValueError, "Need to specify cache info"
	hf = hashlib.md5(repr(f)).hexdigest()
	d1 = hf[:2]
	d2 = hf[2:4]
	d3 = hf[4:6]
	fc = hf[6:]
	r = os.path.join(root, d1, d2, d3)
	# p = os.path.join(r, fc) + tail
	return (r, "%s%s" % (fc, tail))


def fileinfo(fname, *other):
	"""Collect enough information about a file to determine whether or
	not the cache can be used.
	"""
	if fname is None:
		return None
	try:
		s = os.stat(fname)
	except IOError:
		return None
	return (os.path.normpath(fname),
				# This is OK, as long as access patterns are stable, but it's clearly
				# possible to make the cacheing inefficient by accessing the same file
				# in different ways.   Using os.path.abspath() might be better.
			s[stat.ST_INO],	# This seems to be the same on different machines
					# that NFS mount the same file.
			# s[stat.ST_DEV],	# Not a good idea: this differs from machine to machine
						# when accessing the same file.
			s[stat.ST_SIZE], s[stat.ST_MTIME]) + other


def modFileInfo(fname, *other):
	"""Collect enough information about a file to determine whether or
	not the cache can be used.
	"""
	if fname is None:
		return None
	try:
		s = os.stat(fname)
	except IOError:
		return None
	# This is tuned to match .pyc files that may be identical, even if they
	# were installed at different times.   It's a bit weak, but the alternative
	# (i.e. including inode # or mtime) fails if you are trying to share computation
	# across a cluster.
	return (os.path.abspath(fname), s[stat.ST_SIZE]) + other


class BadFileFormat(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)



def modinfo(m, seen):
	if not isinstance(m, tuple):
		m = (m,)
	return tuple( [ modinfo_guts(mm, seen) for mm in m] )


def modinfo_guts(m, seen):
	assert isinstance(m, types.ModuleType)
	if m.__name__ in seen:
		return m.__name__
	seen.add(m.__name__)
	rv = []
	try:
		rv.append(modFileInfo(m.__file__))
	except AttributeError:
		try:
			rv.append(len(m.__dict__))
		except AttributeError:
			rv.append(None)
	for (nm, o) in m.__dict__.items():
		if isinstance(o, types.ModuleType):
			rv.append(modinfo_guts(o, seen))
	return tuple(rv)


def namedModInfo(nm):
	if not isinstance(nm, tuple):
		nm = (nm,)
	s = set()
	return tuple( [ modinfo(sys.modules[q], s) for q in nm ] )


class cache_info(object):
	def __init__(self, root, info=(), fname=None, modname=None, mod=None):
		self.info = info
		if fname is not None:
			self.info += fileinfo(fname)
		if modname is not None:
			self.info += namedModInfo(modname)
		if mod is not None:
			self.info += modinfo(mod, set())
		self.root = root
		self.tail = '.pickle'
		self._dname = None	#: Pathname info, computed only when needed
		self._fpath = None	#: Pathname info, computed only when needed
		# self.dname, self.fpath = _cachepath(self.info, tail=self.tail, root=self.root)

	def __repr__(self):
		return "<cache_info %s %s %s>" % (self.root, self.info, self.tail)

	def copy(self):
		return cache_info(self.root, info=self.info)


	def addinfo(self, *s, **kv):
		"""
		@note: This does I{not} modify self!  It creates a new object.
		"""
		return cache_info(root=self.root, info=self.info+s,
					fname=kv.get('fname', None),
					modname=kv.get('modname', None),
					mod=kv.get('mod', None)
					)


	def dump(self, e):
		"""Cache some data on the disk.
		@rtype: could be anything picklable.
		@return: whatever was passed as C{e}.
		@param e: the data to write.
		@type e: anything picklable.
		"""
		dname, fpath = self.cachepath()
		gpkmisc.makedirs(dname)
		# ftmp = fpath + '.%d.tmp' % os.getpid()
		# fd = open(ftmp, 'w')
		fd = open(fpath, 'w')
		li = len(self.info)
		assert li>0
		i1 = self.info[:(1+li)//2]
		i2 = self.info[(li-1)//2:]
		try:
			# We are assuming that the pickel protocol is sequential,
			# and that disk writes are sequential, so that if the two
			# ends of the dump are correct (i1 and i2) then the stuff
			# in between will be correct.
			cPickle.dump((i1, e, i2), fd, protocol=cPickle.HIGHEST_PROTOCOL)
		except:
			# os.remove(ftmp)
			os.remove(fpath)
			raise
		finally:
			fd.close()
		# os.rename(ftmp, fpath)
		return e
	

	def bg_dump(self, e):
		if len(self.info)==0:
			raise ValueError, "Need to specify cache info"
		t = threading.Thread(target=self.dump, args=(e,), name='cache_dumper%s' % id(e))
		t.start()


	def load(self):
		"""Pull in some data from the disk.
		@rtype: could be anything picklable.
		@return: whatever was cached on disk.
		@except BadFileFormat: when the data isn't valid.
		"""
		dname, fpath = self.cachepath()
		fd = open(fpath, 'r')
		x = cPickle.load(fd)
		li = len(self.info)
		assert li>0
		if(isinstance(x, tuple) and len(x)==3
			and len(x[0])>0 and len(x[2])>0 and len(x[0])+len(x[2])==li+1
			and x[0][-1]==x[2][0]
			and x[0]==self.info[:(1+li)//2] and x[2]==self.info[(li-1)//2:]
			):
			die.info("Cache hit: %s" % fpath)
			return x[1]
		die.info("Cache fail: %s" % fpath)
		# Cache fail should catch cases of file truncation and data corruption,
		# even if the cPickle.load call doesn't.
		raise BadFileFormat


	def cachepath(self):
		"""Return a pathname suitable for cacheing some result.
		@return: C{(path_to_root,path_with_tail)}.   C{Path_to_root} is/will be a directory;
			C{path_with_tail} is a path to a data file within that directory.
			Normally, the actual cache is at the location
			C{os.path.join(path_to_root,path_with_tail)} on the disk;
			that is what you would pass as the C{fname} argument to L{load_cache} or
			L{dump_cache}.
		@rtype: C{tuple(str, str)}
		@except ValueError: if you haven't specified any C{info} yet.
		"""
		if self._dname is not None:
			return (self._dname, self._fpath)
		if len(self.info)==0:
			raise ValueError, "Need to specify cache info"
		hf = hashlib.md5(repr(self.info)).hexdigest()
		d1 = hf[:2]
		d2 = hf[2:4]
		d3 = hf[4:6]
		fc = hf[6:]
		self._dname = os.path.join(self.root, d1, d2, d3)
		self._fpath = os.path.join(self._dname, fc) + self.tail
		return (self._dname, self._fpath)

	
	Errors = (IOError, EOFError, UnpicklingError, BadFileFormat)

if __name__ == '__main__':
	print namedModInfo(__name__)
