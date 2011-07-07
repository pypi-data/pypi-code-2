import sys
try:
	__mod = __import__(sys.platform)
	Manager = __mod.Manager
except ImportError:
	raise
	from base import BaseManager as Manager
