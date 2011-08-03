import os
import time
import unittest

import FixPath
from MiscUtils import PickleCache as pc

# the directory that this file is in:
progPath = os.path.join(os.getcwd(), __file__)
progDir = os.path.dirname(progPath)
assert os.path.basename(progDir) == 'Tests' and \
	os.path.basename(os.path.dirname(progDir)) == 'MiscUtils', \
	'Test needs to run in MiscUtils/Tests.'


class TestPickleCache(unittest.TestCase):

	def test(self):
		# print 'Testing PickleCache...'
		iterations = 2
		for iter in range(iterations):
			# print 'Iteration', iter + 1
			self.oneIterTest()
		# print 'Success.'

	def oneIterTest(self):
		sourcePath = self._sourcePath = os.path.join(progDir, 'foo.dict')
		picklePath = self._picklePath = pc.PickleCache().picklePath(sourcePath)
		self.remove(picklePath) # make sure we're clean
		data = self._data = {'x': 1}
		self.writeSource()
		try:
			# test 1: no pickle cache yet
			assert pc.readPickleCache(sourcePath) is None
			self.writePickle()
			if pc.havePython22OrGreater:
				# test 2: correctness
				assert pc.readPickleCache(sourcePath) == data
				# test 3: wrong pickle version
				assert pc.readPickleCache(sourcePath, pickleVersion=2) is None
				self.writePickle() # restore
				# test 4: wrong data source
				assert pc.readPickleCache(sourcePath, source='notTest') is None
				self.writePickle() # restore
				# test 5: wrong Python version
				v = list(pc.versionInfo)
				v[-1] += 1 # increment serial number
				v, pc.versionInfo = pc.versionInfo, tuple(v)
				try:
					assert pc.readPickleCache(sourcePath) is None
					self.writePickle() # restore
				finally:
					pc.versionInfo = v
				# test 6: source is newer
				self.remove(picklePath)
				self.writePickle()
				# we have to allow for the granularity of getmtime()
				# (see the comment in the docstring of PickleCache.py)
				time.sleep(2)
				self.writeSource()
				assert pc.readPickleCache(sourcePath) is None
				self.writePickle() # restore
		finally:
			self.remove(sourcePath)
			self.remove(picklePath)

	def remove(self, filename):
		try:
			os.remove(filename)
		except OSError:
			pass

	def writeSource(self):
		f = open(self._sourcePath, 'w')
		f.write(str(self._data))
		f.close()

	def writePickle(self):
		assert not os.path.exists(self._picklePath)
		pc.writePickleCache(self._data, self._sourcePath,
			pickleVersion=1, source='test')
		if pc.havePython22OrGreater:
			assert os.path.exists(self._picklePath)


if __name__ == '__main__':
	unittest.main()
