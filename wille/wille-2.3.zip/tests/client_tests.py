import sys; sys.path.append('..')

import wille.client

# Isolation test
client1=wille.client.Client()
client1.load_dir('.')
assert( len(client1.services())>0 )
client2=wille.client.Client()
assert( len(client2.services())==0 )
