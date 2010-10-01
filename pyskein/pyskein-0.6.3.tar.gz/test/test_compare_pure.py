import skein512
import skein
import unittest
from random import randint, randrange


class TestThreefish(unittest.TestCase):
    def runTest(self):
        for i in range(100):
            key = randombytes(64)
            tweak = randombytes(16)
            plain = randombytes(64)
            gold = skein512.threefish(key, tweak, plain)
            c = skein.threefish(key, tweak)
            self.assertEqual(c.encrypt_block(plain), gold)


class TestSkein(unittest.TestCase):
    TREE_PARAMS = [None] #, (1, 1, 2)]

    def testSequential(self):
        for msg in randomlist():
            for mac in randomlist():
                for pers in randomlist():
                    for nonce in randomlist():
                        for tree in self.TREE_PARAMS:
                            gold = skein512.skein512(msg, mac, pers, nonce,
                                                     tree)
                            c = skein.skein512(msg, mac=mac, pers=pers,
                                               nonce=nonce, tree=tree)
                            self.assertEqual(c.digest(), gold)

    def testTree(self):
        for i in range(100):
            msg, mac, pers, nonce = [ron() for _ in range(4)]
            tree = (randint(1, 10), randint(1, 10), randint(2, 255))
            gold = skein512.skein512(msg, mac=mac, pers=pers, nonce=nonce,
                                     tree=tree)
            c = skein.skein512(msg, mac=mac, pers=pers, nonce=nonce, tree=tree)
            self.assertEqual(c.digest(), gold)

    def testDigestSize(self):
        msg = bytes(randrange(256) for _ in range(100))
        for bits in range(1, 800):
            digest = skein.skein512(msg, digest_bits=bits).digest()
            self.assertEqual(digest, skein512.skein512(msg, digest_bits=bits))


def randombytes(n):
    return bytes(randint(0, 255) for _ in range(n))

def randomlist():
    return [b"", randombytes(randint(1, 10)),
            randombytes(randint(100, 1000))]

def ron():
    if randrange(2):
        return randombytes(randrange(1000))
    else:
        return b""


if __name__ == "__main__":
    unittest.main()
