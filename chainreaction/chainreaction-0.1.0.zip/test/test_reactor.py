'''
Created on 2011/07/11

@author: Keita Oouchi
'''
import sys, os

sys.path.append("./src")


import unittest
from collections import OrderedDict
from chainreaction.reactor import react, SeqChain, SetChain, StrChain, Chainable, DictChain, IterChain

class TestReactor(unittest.TestCase):

    def setUp(self):
        self.ispy3 = True if sys.version >= '3.0' else False
        self.targets = []

    def teatDown(self):
        self.targets = []

    def testAttrError(self):
        self.targets.append(1)
        self.targets.append(True)
        self.targets.append(False)
        self.targets.append(None)
        self.targets.append(object)
        for elem in self.targets:
            self.assertRaises(AttributeError, react, elem)

    def testAttrAcceptable(self):
        self.targets.append(str)
        self.targets.append("")
        self.targets.append("123")
        self.targets.append(list)
        self.targets.append([])
        self.targets.append([1, 2, 3])
        self.targets.append(tuple)
        self.targets.append(())
        self.targets.append((1, 2, 3))
        self.targets.append(set)
        self.targets.append({})
        self.targets.append({1, 2, 3})
        self.targets.append(dict)
        self.targets.append({"1":1, "2":2, "3":3})
        self.targets.append(bytes)
        self.targets.append(b"123")

        class StrChild(str):pass
        class ListChild(list):pass
        class TupleChild(tuple):pass
        class SetChild(set):pass
        class DictChild(set):pass

        self.targets.append(StrChild())
        self.targets.append(ListChild())
        self.targets.append(SetChild())
        self.targets.append(DictChild())
        for elem in self.targets:
            target = react(elem)
            self.assertTrue(issubclass(type(target), Chainable))
            self.assertEqual(type(elem), target.type)

    def testStr(self):
        original = "hello world"
        wrapped = react(original)

        #filter returns str wrapped obj.
        filtered = wrapped.filter(lambda x: ord(x) > ord('l'))
        self.assertEqual(filtered.type, str)
        self.assertIsInstance(filtered, StrChain)
        self.assertEqual(filtered.counts(), 4)

        #map returns map wrapped obj.
        mapped = wrapped.map(lambda x: ord(x))
        expect = map if self.ispy3 else list 
        self.assertEqual(mapped.type, expect)
        self.assertIsInstance(mapped, Chainable)
        self.assertEqual(mapped.counts(), 11)

        #take returns str wrapped obj.
        taken = wrapped.takewhile(lambda x: x > ' ')
        self.assertEqual(taken.type, str)
        self.assertIsInstance(taken, StrChain)
        self.assertEqual(taken.counts(), 5)

        #drop returns str wrapped obj.
        dropped = wrapped.dropright(lambda x: x > ' ')
        self.assertEqual(dropped.type, str)
        self.assertIsInstance(dropped, StrChain)
        self.assertEqual(dropped.counts(), 6)

        #reverse returns str wrapped obj.
        reversed = wrapped.reverse
        self.assertEqual(reversed.type, str)
        self.assertIsInstance(dropped, StrChain)
        self.assertEqual(reversed.unwrap, "dlrow olleh")

        #original method's of wrapped obj returns its type of return value wrapped.
        splitted = wrapped.split(" ")
        self.assertEqual(splitted.type, list)
        self.assertIsInstance(splitted, SeqChain)
        self.assertEqual(splitted.counts(), 2)
        self.assertAlmostEqual(splitted.mkstring().unwrap, "helloworld")

        tobewrapped = "hello"
        wrapped = react(tobewrapped)
        wrapped = wrapped.upper().map(lambda c: ord(c))
        self.assertEqual([chr(c) for c in wrapped.unwrap],
                         [c for c in tobewrapped.upper()])

    def testDict(self):
        original = OrderedDict()
        original["k1"] = "v1"
        original["k2"] = "v2"
        wrapped = react(original)

        self.assertEqual(wrapped.mkstring().unwrap, "k1=v1&k2=v2")

        gotten = wrapped["k1"]
        self.assertEqual(gotten.type, str)
        self.assertIsInstance(gotten, StrChain)
        self.assertEqual(gotten.unwrap, "v1")

        #filter
        filtered = wrapped.filter(lambda t: t[1] == "v1")
        self.assertEqual(filtered.type, OrderedDict)
        self.assertIsInstance(filtered, DictChain)
        self.assertEqual(filtered.mkstring().unwrap, "k1=v1")

        #map
        mapped = wrapped.map(lambda t: (t[0], " "))
        self.assertEqual(mapped.type, OrderedDict)
        self.assertIsInstance(mapped, DictChain)
        self.assertEqual(mapped.mkstring().unwrap, "k1= &k2= ")

        cleared = wrapped.clear()
        self.assertEqual(cleared.type, OrderedDict)
        self.assertIsInstance(cleared, DictChain)
        self.assertEqual(cleared.counts(), 0)

    def testSet(self):
        original = set([1, 2, 3])
        wrapped = react(original)

        self.assertEqual(wrapped.type, set)
        self.assertIsInstance(wrapped, SetChain)

        #filter
        filtered = wrapped.filter(lambda x: x > 2)
        self.assertEqual(filtered.type, set)
        self.assertIsInstance(filtered, SetChain)
        self.assertEqual(filtered.counts(), 1)

        #map
        mapped = wrapped.map(lambda x: x * 2)
        self.assertEqual(mapped.type, set)
        self.assertIsInstance(mapped, SetChain)
        self.assertEqual(mapped.reduce(lambda x, y: x + y), 12)

        unionized = wrapped.union(set([4, 5, 6]))
        self.assertEqual(unionized.type, set)
        self.assertIsInstance(unionized, SetChain)
        self.assertEqual(unionized.unwrap, set([1, 2, 3, 4, 5, 6]))


    def testSeq(self):
        original = [1, 2, 3]
        wrapped = react(original)

        #filter
        filtered = wrapped.filter(lambda x: x > 2)
        self.assertEqual(filtered.type, list)
        self.assertIsInstance(filtered, SeqChain)
        self.assertEqual(filtered.counts(), 1)

        #map
        mapped = wrapped.map(lambda x: x * 2)
        self.assertEqual(mapped.type, list)
        self.assertIsInstance(mapped, SeqChain)
        self.assertEqual(mapped.reduce(lambda x, y: x + y), 12)

        appended = wrapped.append(4)
        self.assertEqual(appended.type, list)
        self.assertIsInstance(appended, SeqChain)
        self.assertEqual(appended.counts(), 4)
        self.assertEqual(wrapped.counts(), 4)

        converted = wrapped.toset
        self.assertEqual(converted.type, set)
        self.assertIsInstance(converted, SetChain)

        sorted = react([3, 2, 1]).sort
        self.assertEqual(sorted.type, list)
        self.assertIsInstance(sorted, SeqChain)
        self.assertEqual(sorted.unwrap, [1, 2, 3])

    def testIter(self):
        original = iter([1, 2, 3])
        wrapped = react(original)
        expect = "__next__" if self.ispy3 else "next"
        self.assertTrue(hasattr(wrapped._iterator, expect))
        self.assertIsInstance(wrapped, IterChain)
        self.assertEqual(wrapped.counts(), 3)
        itercount = 0
        for x in original:
            itercount += 1
        self.assertEqual(itercount, 0)

        it = iter([1, 2, 3])
        mapped = map(lambda x: x * 2, it)
        filtered = filter(lambda x: x > 4, mapped)
        self.assertEqual(sum(filtered), 6)

        wrapped = react(iter([1, 2, 3]))
        mapped = wrapped.map(lambda x: x * 2)
        self.assertIsInstance(mapped, Chainable)
        filtered = mapped.filter(lambda x: x >= 4)
        if self.ispy3:
            self.assertTrue(filtered.isiterator)
        self.assertEqual(filtered.reduce(lambda x, y: x + y), 10)

        wrapped = react(iter([1, 2, 3]))
        listed = wrapped.tolist
        self.assertEqual(listed.type, list)
        self.assertIsInstance(listed, SeqChain)
        src = os.path.join("test", "used_in_test.data")        
        if os.path.exists(src):
            f = open(src)
            filechain = react(f)
            self.assertIsInstance(filechain, Chainable)
            self.assertEqual(filechain.counts(), 9)
            filechain.close()
            self.assertRaises(ValueError, filechain.read)
            self.assertTrue(f.closed)
    
            f = open(src)
            result = []
            with react(f) as filechain:
                filechain.foreach(lambda ln: result.append(ln))
            self.assertTrue(f.closed)
            self.assertEqual(len(result), 9)
        
        test = bytearray("hello world-._~", encoding="UTF-8")
        wrapped = react(test)
        safe = set()
        react("0123456789").foreach(lambda c: safe.add(ord(c)))
        react(range(ord('a'), ord('z') + 1)).foreach(lambda b: safe.add(b))
        react(range(ord('A'), ord('Z') + 1)).foreach(lambda b: safe.add(b))
        react("-._~").foreach(lambda c: safe.add(ord(c)))
        test = wrapped.map(
            lambda b: b if b > 0 else 256 + b).map(
            lambda i: '+' if chr(i).isspace() else chr(i) if i in safe else "%{0:x}".format(i))
        self.assertEqual(test.mkstring().unwrap, "hello+world-._~")

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TestReactor))
  return suite
  
if __name__ == "__main__":
    suite()
