import sys; sys.path.append('..')

import wille.server
import wille.client
import sys

# Settings
port = 2727
debug = False

# Set up server
srv = wille.server.Server(services_dir='.',server_port=port,quiet=True)
srv.run(background=True)
cl = wille.client.Client()
cl.load_url('http://localhost:%s/'%port)

timeouts = [1,2,3,]
for timeout in timeouts:
	if debug: print("Testing %s sec timeout" % timeout)
	r=cl.execute_service(name='timeout_test',params=dict(timeout=('%s'%timeout)))

# Kill server
sys.exit(0)
