import sys; sys.path.append('..')

import wille.server
import wille.client
import sys
import random, string
import time

from upload_test.upload_test import checksum_simple
from wille.utils import random_string

debug = False
port = 2727
srv = wille.server.Server(services_dir='.',server_port=port,quiet=True)
srv.run(background=True)
cl = wille.client.Client()
cl.load_url('http://localhost:%s/'%port)

raw_data_1mb = random_string(1024*1024)
filesizes = [1,5,10,]
for filesize in filesizes:
	raw_data = ''
	
	if debug: print("Generating %s MB of random data.." % (filesize))
	raw_data = ''
	for i in range(0,filesize): raw_data += raw_data_1mb
	calc_checksum = checksum_simple(raw_data)
	if debug: print("Trying %s MB upload... (checksum=%s)" % (len(raw_data)/1024/1024.0, calc_checksum))
	time1 = time.clock()
	r=cl.execute_service(name='upload_test',params=dict(checksum=calc_checksum,raw_data=raw_data))
	time2 = time.clock()
	if debug: print("Total execution time: %s s (%s MB/s)" % (time2-time1, (filesize*1.0/(time2-time1))))
	if debug: print("[%s]"%r.data)
	assert( r.metadata['http_response']['status']=='200' )
