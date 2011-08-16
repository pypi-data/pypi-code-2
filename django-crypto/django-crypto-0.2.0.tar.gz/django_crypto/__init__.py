from base64 import b64encode, b64decode
from Crypto.Cipher import AES

from django.conf import settings

from django_crypto.settings import CRYPTO_SECRET, CRYPTO_BLOCK_SIZE, CRYPTO_PADDING_CHAR

# this is the default cipher, generated when the app starts
cipher = AES.new(CRYPTO_SECRET)

def _pad(s):
    '''
    Adds padding characters to the string, so that the len of the string is divisible by the block size.
    '''
    return s + (CRYPTO_BLOCK_SIZE - len(s) % CRYPTO_BLOCK_SIZE) * CRYPTO_PADDING_CHAR

def EncodeAES(s, c=cipher):
    '''
    Actually encode a string using the cipher.
    '''
    return b64encode(c.encrypt(_pad(s)))

def DecodeAES(e, c=cipher):
    '''
    Decode a string using the cipher.
    '''
    return c.decrypt(b64decode(e)).rstrip(CRYPTO_PADDING_CHAR)