from Crypto.Cipher import AES

from django.conf import settings

CRYPTO_SECRET = getattr(settings, 'CRYPTO_SECRET', '')

if not CRYPTO_SECRET:
    raise Exception('You must define CRYPTO_SECRET in your projects settings.py')

CRYPTO_BLOCK_SIZE = getattr(settings, 'CRYPTO_BLOCK_SIZE', 32)
CRYPTO_PADDING_CHAR = getattr(settings, 'CRYPTO_PADDING_CHAR', '{')