"""This a helper module for multivariance.py"""

import Num
import multivariance_classes as M
import random
import g_implements

class datum_c:
	def __init__(self, vector, classid):
		self.classid = classid
		self.value = vector


def _multi_mu__init__(self, dataset=None, ndim=None, idmap=None, details=None):
		"""You either give it a complete dataset to look at,
		including class IDs, *or* the dimensionality of the data
		(ndim) and a map between classids and integers.
		This map can be obtained from nice_hash.
		"""
		import dictops

		if dataset is not None:
			assert details is None
			assert ndim is None and idmap is None
			import nice_hash
			assert (ndim is None) and (idmap is None)
			h = nice_hash.nice_hash(lambda x:x)
			for t in dataset:
				assert g_implements.impl(t, datum_c), \
					"Bad input type: %s" % g_implements.why(t, datum_c)
				h.add(t.classid)
			ndim = len(dataset[0].value)
			idmap = h.map()
		elif details is not None:
			assert ndim is None and idmap is None
			ndim = details.ndim()
			idmap = details.id_to_int
		assert (ndim is not None) and (idmap is not None)
		self.Nmu = len(idmap)
		self.id_to_int = idmap.copy()
		self.int_to_id = dictops.rev1to1(idmap)
		# print 'MM__init__id_to_int=', self.id_to_int
		# print 'MM__init__int_to_id=', self.int_to_id
		for i in range(len(self.int_to_id)):
			assert i in self.int_to_id, "Not a good mapping to indices."


class multi_mu(M.modeldesc):
	__doc__ = """This describes a quadratic model of a known size,
			with multiple means
			(one for each different class of data)."""

	def __init__(self, dataset=None, ndim=None, idmap=None, details=None):
		M.modeldesc.__init__(self, ndim)
		_multi_mu__init__(self, dataset, ndim, idmap, details)
	__init__.__doc__ = _multi_mu__init__.__doc__


	def modeldim(self):
		m = self.ndim()
		return self.Nmu*m + (m*(m+1))/2


	def unpack(self, prms):
		m = self.ndim()
		assert len(prms) == self.modeldim()
		mu = {}
		for i in range(self.Nmu):
			mu[self.int_to_id[i]] = prms[i*m:(i+1)*m]
		# print 'MMunpackMu=', mu
		invsigma = Num.zeros((m, m), Num.Float)
		j = self.Nmu*m
		for i in range(m):
			tmp = prms[j:j+(m-i)]
			invsigma[i,i:] = tmp
			invsigma[i:,i] = tmp
			j += m-i
		return self.new(mu, invsigma)


	def new(self, mu, invsigma, bias=0.0):
		"""Mu is a mapping of classids to vectors.  invsigma is a square matrix."""
		# print 'new(', mu, invsigma, ')'
		assert type(mu) == type({})
		# print 'NewMu=', mu
		return multi_mu_with_numbers(mu, invsigma, self, bias)


	def start(self, data):
		raise RuntimeError, 'Broken'
		import nice_hash
		h = nice_hash.nice_hash(lambda x: x.classid)
		for datum in data:
			assert g_implements.impl(datum, datum_c)
			h.add(datum)
		if len(data) > 1:
			ivar = M.diag_inv_variance([datum.value for datum in data])
		else:
			ivar = Num.identity(self.ndim())
		divar = Num.diagonal(ivar)
		rnd = {}
		var = {}
		for (k, v) in h.rmap().items():
			# print 'start: k=', k, 'v=', v, 'divar=', divar
			rnd[self.int_to_id[k]] = random.choice(v).value
			var[self.int_to_id[k]] = 1.0/divar
		# print 'ivarsize=', ivar.shape, Num.outerproduct(divar, divar).shape
		return (self.new(rnd, ivar),
			self.new(var, Num.outerproduct(divar,divar))
			)


class multi_mu_with_numbers(M.model_with_numbers):
	def __init__(self, mu, invsigma, details, bias=0.0, offset=None):
		"""self.mu, self.invsigma, and self._offset should be considered
		read-only for all users of this class."""
		assert isinstance(details, multi_mu)
		M.model_with_numbers.__init__(self, details, bias)
		self.mu = Num.array(mu, copy=True)
		# print 'MMmu=', mu
		# print 'invsigma.shape=', invsigma.shape
		self.invsigma = Num.array(invsigma)
		self._offset = offset

	def __str__(self):
		return '<multi_mu: mu=%s; invsigma=%s >' % (str(self.mu), str(self.invsigma))

	__repr__ = __str__

	addoff = M._q_addoff	# Will not be called if _offset is not None

	def pack(self):
		n = self.ndim()
		# print 'invsigma.shape=', self.invsigma.shape, 'n=', n
		assert self.invsigma.shape == (n,n)
		assert len(self.mu) == self.desc.Nmu
		tmp = []
		# print 'self.mu=', self.mu
		for i in range(self.desc.Nmu):
			tmp.append( self.mu[self.desc.int_to_id[i]] )
		for i in range(n):
			tmp.append(self.invsigma[i,i:])
		# print 'Pack tmp=', tmp
		return Num.concatenate(tmp)


	def logp(self, datum):
		delta = datum.value - self.mu[datum.classid]
		parab = Num.dot(delta, Num.matrixmultiply(self.invsigma,
							delta))
		if not parab >= 0.0:
			raise M.QuadraticNotNormalizable, "Not positive-definite"
		return -parab/2.0 +  self.offset() + self.bias



class multi_mu_diag(M.modeldesc):
	__doc__ = """This describes a quadratic model of a known size,
			with multiple means (one for each different class of data).
			The covariance matrix is shared and diagonal."""

	def __init__(self, dataset=None, ndim=None, idmap=None, details=None):
		M.modeldesc.__init__(self, ndim)
		_multi_mu__init__(self, dataset, ndim, idmap, details)
	__init__.__doc__ = _multi_mu__init__.__doc__


	def modeldim(self):
		m = self.ndim()
		return self.Nmu*m + m


	def unpack(self, prms):
		m = self.ndim()
		assert len(prms) == self.modeldim()
		mu = {}
		for i in range(self.Nmu):
			mu[self.int_to_id[i]] = prms[i*m:(i+1)*m]
		# print 'MMunpackMu=', mu
		j = self.Nmu*m
		invsigma = prms[j:]
		return self.new(mu, invsigma)


	def new(self, mu, invsigma, bias=0.0):
		"""Mu is a mapping of classids to vectors.  Invsigma is a vector."""
		assert type(mu) == type({})
		return multi_mu_diag_with_numbers(mu, invsigma, self, bias)


	def start(self, data):
		raise RuntimeError, 'Broken'
		import nice_hash
		h = nice_hash.nice_hash(lambda x: x.classid)
		for datum in data:
			assert g_implements.impl(datum, datum_c)
			h.add(datum)
		if len(data) > 1:
			divar = M.vec_inv_variance([datum.value for datum in data])
		else:
			divar = Num.ones((self.ndim(),), Num.Float)
		rnd = {}
		var = {}
		for (k, v) in h.rmap().items():
			# print 'start: k=', k, 'v=', v, 'divar=', divar
			rnd[self.int_to_id[k]] = random.choice(v).value
			var[self.int_to_id[k]] = 1.0/divar
		return (self.new(rnd, divar),
			self.new(var, divar*divar)
			)


class multi_mu_diag_with_numbers(M.model_with_numbers):
	def __init__(self, mu, invsigma, details, bias=0.0, offset=None):
		"""self.mu, self.invsigma, and self._offset should be considered
		read-only for all users of this class."""
		assert isinstance(details, multi_mu_diag)
		M.model_with_numbers.__init__(self, details, bias)
		self.mu = Num.array(mu)
		# print 'MMmu=', mu
		# print 'invsigma.shape=', invsigma.shape
		self.invsigma = Num.array(invsigma)
		self._offset = offset

	def __str__(self):
		return '<multi_mu_diag: mu=%s; invsigma=%s >' % (str(self.mu), str(self.invsigma))

	__repr__ = __str__

	addoff = M._d_addoff	# Will not be called if _offset is not None

	def pack(self):
		n = self.ndim()
		# print 'invsigma.shape=', self.invsigma.shape, 'n=', n
		assert self.invsigma.shape == (n,)
		assert len(self.mu) == self.desc.Nmu
		tmp = []
		# print 'self.mu=', self.mu
		for i in range(self.desc.Nmu):
			tmp.append( self.mu[self.desc.int_to_id[i]] )
		tmp.append( self.invsigma )
		# print 'Pack tmp=', tmp
		return Num.concatenate(tmp)


	def logp(self, datum):
		delta = datum.value - self.mu[datum.classid]
		parab = Num.sum(self.invsigma * delta**2)
		if not parab >= 0.0:
			raise M.QuadraticNotNormalizable, "Not positive-definite"
		return -parab/2.0 + self.offset() + self.bias




