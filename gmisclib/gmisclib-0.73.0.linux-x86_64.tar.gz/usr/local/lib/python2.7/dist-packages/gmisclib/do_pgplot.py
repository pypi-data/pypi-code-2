import pgplot.cpgplot
pl = pgplot.cpgplot


__version__ = "$Revision: 1.1 $"


class plot:
	def __init__(self, dev=None):
		if dev is None:
			dev = 'localhost:0/xw'
		pl.cpgopen(dev)
		self.fresh = 1
		self.ask(0)

	def __del__(self):
		pl.cpgclos()

	def next(self):
		if self.newsize:
			pl.cpgpap(self.width, self.aspect)
			self.newsize = 0
		pl.cpgpage()

	def ask(self, onoff=1):
		pl.cpgask(onoff)

	def size(self, width, aspect):
		if not self.fresh:
			self.width = width
			self.aspect = aspect
			self.newsize = 1
		else:
			pl.cpgpap(width, aspect)
			self.newsize = 0

	def panels(self, w, h):
		pl.cpgsubp(w, h)

	def flush(self):
		pl.cpgupdt()

	def start(self):
		pl.cpgvstd()	# standard viewport
