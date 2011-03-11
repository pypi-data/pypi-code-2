import sys; sys.path.append('..')

import time

import wille.client

SERVICES_DIR = '.'
debug = False

if debug: print( "Instantiation Wille Client" )
cl = wille.client.Client()
cl.load_dir(SERVICES_DIR)
cl.services()
params = {'timeout': '0.01'}
desc1 = dict(name='timeout_test', params=params)

# Execute single service
if debug: print( "Execute a single service" )
time1_1 = time.clock()
results = cl.execute_service(name='timeout_test', params=params) 
time1_2 = time.clock()
d1 = time1_2-time1_1
if debug: print( "Single time\t\t: %s" % (d1) )

# Execute n in a group
descs = list()
for i in range(0,5):
	descs.append(desc1)
	time2_1 = time.clock()
	results = cl.execute_services( descs )
	time2_2 = time.clock()
	d5 = time2_2-time2_1
	if debug: print( "%s in a group\t: %s" % (len(descs), d5) )
	integ_last = None
	for result in results:
		integ_this = len(result.data)
		if integ_last is not None and integ_this!=integ_last:
			print( "FAILED: Mismatching results from identical data" )
			assert(0)
	time.sleep(0.1)
