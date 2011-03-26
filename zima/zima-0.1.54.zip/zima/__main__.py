import sys
from zima import start

config = None

if len(sys.argv) > 1:
	import imp
	config = imp.load_source('config', sys.argv[1])

start(config)
