"""Simple vector if pymunk is not available"""

class Vec2d(object):
	def __init__(self, x=0, y=0):
		"""Initialise"""
		self.x = x
		self.y = y

	def __div__(self, other):
		"""Divide"""
		return Vec2d(self.x/other, self.y/other)

	def __add__(self, other):
		"""Add"""
		return Vec2d(self.x+other.x, self.y+other.y)

	def __iter__(self):
		"""Iterate"""
		return iter((self.x, self.y))
