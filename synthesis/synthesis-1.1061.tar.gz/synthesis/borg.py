'''
Created on Dec 6, 2010

@author: eric
'''
class Borg:
	''' pseudo singleton
		Use this as a base class to make a singleton type object.
		In your __init__ method, do this:
		Borg.__init__(self)
	'''
	_shred_state = {}

	def __init__(self):
		self.__dict__ = self._shred_state


