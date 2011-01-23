from Crypto.Cipher import DES3
import base64
import os

BLOCK_SIZE = 24
PATH ="/home/eric/occws/occws/keys/occ.key"
if os.path.exists(PATH):
    os.remove(PATH)
keyfile = open(PATH, 'w')
#secret = keyfile.read()
#generate a random secret key
secret = os.urandom(BLOCK_SIZE)
keyfile.write(secret)
#print "secret is", secret
