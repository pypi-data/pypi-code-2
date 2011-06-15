
import random

KEYLENGTH = 6
ALLOWED_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class KeyManager:

    def generate(self):
        key = ''
        for i in range(KEYLENGTH):
            key += random.choice(ALLOWED_CHARS)
        return key

    def verify(self, key):
        if key is None:
            return False
        if len(key) != KEYLENGTH:
            return False
        for c in key:
            if c not in ALLOWED_CHARS:
                return False
        return True

