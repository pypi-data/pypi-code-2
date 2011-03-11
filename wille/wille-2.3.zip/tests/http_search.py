import sys; sys.path.append('..')
SERVICES_DIR = '.'

import wille.server, sys
from wille.services import HTTPServicePool

# Start 2 servers
srv = wille.server.Server(services_dir=SERVICES_DIR,server_port=2727,quiet=True)
srv2 = wille.server.Server(services_dir=SERVICES_DIR,server_port=2728,quiet=True)
srv.run(background=True)
srv2.run(background=True)

# Create http pool instance for first server
pool = HTTPServicePool('http://localhost:2727/')

# Count services by name on a single server
count = len(pool.services(name='timeout_test'))
assert ( count == 1 )

# Connect to second server
pool.connect_to('http://localhost:2728/')

# Count services by name on two servers
count = len(pool.services(name='timeout_test'))
assert ( count == 2 )

# Count services by type on two servers
count = len(pool.services(type='test'))
assert( count == 4 )

# Kill servers
sys.exit(0)
