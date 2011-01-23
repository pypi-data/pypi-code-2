from Crypto.Cipher import DES3
import base64
import os

'''
from https://secure.wikimedia.org/wikipedia/en/wiki/Triple_DES:

The standards define three keying options:

    * Keying option 1: All three keys are independent.
    * Keying option 2: K1 and K2 are independent, and K3 = K1.
    * Keying option 3: All three keys are identical, i.e. K1 = K2 = K3.

Keying option 1 is the strongest, with 3 x 56 = 168 independent key bits.

Keying option 2 provides less security, with 2 x 56 = 112 key bits. This option is stronger than simply DES encrypting twice, e.g. with K1 and K2, because it protects against meet-in-the-middle attacks.

Keying option 3 is equivalent to DES, with only 56 key bits. This option provides backward compatibility with DES, because the first and second DES operations cancel out. It is no longer recommended by the National Institute of Standards and Technology (NIST),[6] and is not supported by ISO/IEC 18033-3.
'''
#So let's try to get Keying option one working

#Not sure how the cipher object (block size) arrives at picking the keying option?
# the block size for the cipher object; must be 16, 24, or 32 for AES (bytes)
#for DES3 in pycrypto, the block size is 16 or 24 bytes, I just picked 16 because I think that's the compatible size used
#BLOCK_SIZE = 16 #This yields a 16 x 8 = 128 bit 3DES key, which makes no sense given the wikipedia options above.  Must be some translation involved in pycrypto here
BLOCK_SIZE = 24 #hopefully, this achieves the highest keying option (#1) 

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
#Path to OCC's 3DES 

#use the gendeskey.py file to make a new 3DES secret key

KEY_PATH ="/home/eric/occws/occws/keys/occ.key"

def removePadding(BLOCK_SIZE, s):
    'Remove rfc 1423 padding from string.'
    n = ord(s[-1]) # last byte contains number of padding bytes
    if n > BLOCK_SIZE or n > len(s):
        raise Exception('invalid padding')
    return s[:-n]
  
def nrPadBytes(BLOCK_SIZE, size):
    'Return number of required pad bytes for block of size.'
    if not (0 < BLOCK_SIZE < 255):
        raise Exception('BLOCK_SIZE must be between 0 and 255')
    return BLOCK_SIZE - (size % BLOCK_SIZE)

def appendPadding(BLOCK_SIZE, s):
    '''Append rfc 1423 padding to string.

    RFC 1423 algorithm adds 1 up to BLOCK_SIZE padding bytes to string s. Each 
    padding byte contains the number of padding bytes.
    '''
    n = nrPadBytes(BLOCK_SIZE, len(s))
    return s + (chr(n) * n)
# one-liners to encrypt/encode and decrypt/decode a stringe
# encrypt with 3DES, encode with base64

def encodeDES3(cipher, plain_text_string):
    encoded_string = base64.b64encode(cipher.encrypt(appendPadding(BLOCK_SIZE, plain_text_string)))
    return encoded_string

def encryptFile(unencrypted_filepath, path_to_encrypt_to):
    keyfile = open(KEY_PATH, 'r')
    secret = keyfile.read()
    file_to_encrypt = open(unencrypted_filepath, 'r')
    text_to_encrypt = file_to_encrypt.read()
    cipher = DES3.new(secret)
    encrypted_text = encodeDES3(cipher, text_to_encrypt)
    encrypted_file = open(path_to_encrypt_to,'w')
    encrypted_file.write(encrypted_text)
    return encrypted_file

file_to_encrypt = '/home/eric/Desktop/just.xml'
path_to_encrypt_to = '/home/eric/Desktop/HUD_HMIS_OCC_11-01-2010_1.xml.enc'
encryptFile(file_to_encrypt, path_to_encrypt_to)