
import os
import hashlib

def cachepath(f, suffix_to_del=None, tail='', root=''):
	"""Return a pathname suitable for cacheing some result.
	@return: C{(path_to_root,path_with_tail)}.   C{Path_to_root} is/will be a directory;
		C{path_with_tail} is a path to a data file within that directory.
	@rtype: C{tuple(str, str)}
	@param f: An arbitrary key, could be a pathname.
	@param suffix_to_del: something to delete from the tail of C{f}. (Or none, if nothing is to be deleted.)
	@param tail: something to add at the end of the constructed path.
	@type suffix_to_del: str
	@type tail: str or None
	@type f: str
	@except ValueError: if C{suffix_to_del} is specified and C{f} doesn't end that way.
	"""
	if suffix_to_del is not None:
		if not f.endswith(suffix_to_del):
			raise ValueError, 'f(i.e. "...%s") should end in "%s"' % (f[max(0, len(f)-20):], suffix_to_del)
		f = f[:len(f)-len(suffix_to_del)]
	hf = hashlib.md5(f).hexdigest()
	d1 = hf[:2]
	d2 = hf[2:4]
	d3 = hf[4:6]
	fc = hf[6:]
	r = os.path.join(root, d1, d2, d3)
	return (r, '%s%s' % (fc, tail))
