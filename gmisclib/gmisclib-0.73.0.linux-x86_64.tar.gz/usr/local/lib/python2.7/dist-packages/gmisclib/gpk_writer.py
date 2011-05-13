import os

class writer(object):
	def comments(self, comments):
		"""Add comments to the data file.
		Comments can appear anywhere.
		"""
		for comment in comments:
			self.comment(comment)

	def comment(self, comment):
		raise RuntimeError, "Virtual Function"

	def header(self, k, v):
		raise RuntimeError, "Virtual Function"
	
	def headers(self, h):
		hdritems = h.items()
		hdritems.sort()
		for (k, v) in hdritems:
			self.header(k, v)


	def __init__(self, fd):
		self.fd = fd

	def data(self, dataset):
		"""Write a series of lines to the output file."""
		for datum in dataset:
			self.datum(datum)
	
	def extend(self, d):
		self.data(d)

	def append(self, d):
		self.datum(d)

	def datum(self, data_item):
		raise RuntimeError, "Virtual Function"
	

	def flush(self):
		if hasattr(self.fd, 'flush'):
			self.fd.flush()
			# os.fsync(self.fd.fileno())

	def close(self):
		# Don't explicitly close it, as self.fd
		# could be sys.stdout.   We just de-refererence
		# it, so that it automatically closes if nothing
		# else keeps it open.
		if self.fd:
			self.flush()
		self.fd = None



class null_writer(writer):
	def comments(self, comments):
		pass

	def comment(self, comment):
		pass

	def header(self, k, v):
		pass
	
	def headers(self, h):
		pass

	def __init__(self):
		pass

	def data(self, dataset):
		pass
	
	def datum(self, data_item):
		pass
	
	def __del__(self):
		self.close()

	def flush(self):
		pass

	def close(self):
		pass
