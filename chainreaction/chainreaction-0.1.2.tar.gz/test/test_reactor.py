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
        
        #for expression
        self.assertEqual(wrapped.unwrap, "".join([c for c in wrapped]))

        #__repr__
        self.assertEqual(str(wrapped), "'hello world':StrChain")

        #__getitem__
        self.assertEqual(wrapped[0].type, str)
        self.assertEqual(wrapped[0].unwrap, "h")

        #tostring & mkstring
        self.assertIs(wrapped.tostring, original)
        self.assertEqual(wrapped.mkstring(",").unwrap, "h,e,l,l,o, ,w,o,r,l,d")

        #dump
        self.assertEqual(wrapped.dump, "[Dumped Information]\nStrChain\nstr\nhello world")

        #forall
        forall = wrapped.forall(lambda c: ord(c) >= ord(" "))
        self.assertTrue(forall)
        forall = wrapped.forall(lambda c: ord(c) != ord(" "))
        self.assertFalse(forall)

        #forany
        forany = wrapped.forany(lambda c: ord(c) == ord(" "))
        self.assertTrue(forany)
        forany = wrapped.forany(lambda c: ord(c) == ord("?"))
        self.assertFalse(forany)

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

        #takeright
        taken = wrapped.takeright(lambda x: x > ' ')
        self.assertEqual(taken.type, str)
        self.assertIsInstance(taken, StrChain)
        self.assertEqual(taken.unwrap, "world")

        #drop returns str wrapped obj.
        dropped = wrapped.dropright(lambda x: x > ' ')
        self.assertEqual(dropped.type, str)
        self.assertIsInstance(dropped, StrChain)
        self.assertEqual(dropped.counts(), 6)

        #dropwhile
        dropped = wrapped.dropwhile(lambda c: c != ' ')
        self.assertEqual(dropped.type, str)
        self.assertIsInstance(dropped, StrChain)
        self.assertEqual(dropped.unwrap, " world")

        #contains returns true of false
        self.assertTrue(wrapped.contains(" "))
        self.assertFalse(wrapped.contains("?"))

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

        tobewrapped = "hello"
        wrapped = react(bytearray(tobewrapped, encoding="UTF-8"))
        self.assertEqual(wrapped.tostring, tobewrapped)

    def testDict(self):
        original = OrderedDict()
        original["k1"] = "v1"
        original["k2"] = "v2"
        wrapped = react(original)

        self.assertEqual(wrapped.mkstring().unwrap, "k1=v1&k2=v2")
        self.assertEqual(wrapped.tostring, "k1=v1&k2=v2")
        
        #for statement
        expect = ["{0}={1}".format(k, v) for k,v in wrapped]
        self.assertEqual("&".join(expect), "k1=v1&k2=v2")

        #__getitem__
        gotten = wrapped["k1"]
        self.assertEqual(gotten.type, str)
        self.assertIsInstance(gotten, StrChain)
        self.assertEqual(gotten.unwrap, "v1")
        wrapped2 = react({"k":1})
        self.assertEqual(wrapped2["k"], 1)

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
        self.assertEqual(mapped.tostring, "k1= &k2= ")

        cleared = wrapped.clear()
        self.assertEqual(cleared.type, OrderedDict)
        self.assertIsInstance(cleared, DictChain)
        self.assertEqual(cleared.counts(), 0)



    def testSet(self):
        original = set([1, 2, 3])
        wrapped = react(original)

        self.assertEqual(wrapped.type, set)
        self.assertIsInstance(wrapped, SetChain)
        
        #for statement
        expect = set([x for x in wrapped])
        self.assertEqual(expect, wrapped.unwrap)

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

        self.assertEqual(len(wrapped.tostring), len(original))

        #min & max
        self.assertEqual(wrapped.min, 1)
        self.assertEqual(wrapped.max, 3)


    def testSeq(self):
        original = [1, 2, 3]
        wrapped = react(original)
        
        #for statement
        self.assertEqual(wrapped.unwrap, [i for i in wrapped])

        #__getitem__
        self.assertIsInstance(wrapped[0], int)

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

        #list.append
        appended = wrapped.append(4)
        self.assertEqual(appended.type, list)
        self.assertIsInstance(appended, SeqChain)
        self.assertEqual(appended.counts(), 4)
        self.assertEqual(wrapped.counts(), 4)

        #list to set
        converted = wrapped.toset
        self.assertEqual(converted.type, set)
        self.assertIsInstance(converted, SetChain)

        #sort
        sorted = react([3, 2, 1]).sort
        self.assertEqual(sorted.type, list)
        self.assertIsInstance(sorted, SeqChain)
        self.assertEqual(sorted.unwrap, [1, 2, 3])

        #reverse
        reversed = react([1, 2, 3]).reverse
        self.assertEqual(reversed.type, list)
        self.assertIsInstance(reversed, SeqChain)
        self.assertEqual(reversed.unwrap, [3, 2, 1])

        #accumulate
        accumed = react([1, 2, 3]).accumulate(lambda x, y: x * y)
        self.assertEqual(accumed.type, list)
        self.assertIsInstance(accumed, SeqChain)
        self.assertEqual(accumed.unwrap, [1, 2, 6])

    def testIter(self):
        original = iter([1, 2, 3])
        wrapped = react(original)
        expect = "__next__" if self.ispy3 else "next"
        #__next__:py3.x, next:py2.x
        self.assertTrue(hasattr(wrapped._iterator, expect))
        self.assertIsInstance(wrapped, IterChain)

        #iterator was consumed.
        self.assertEqual(wrapped.counts(), 3)
        itercount = 0
        for x in original:
            itercount += 1
        self.assertEqual(itercount, 0)
        
        #for statement
        wrapped = react(iter([1,2,3]))
        self.assertEqual([i for i in wrapped], [1,2,3])

        wrapped = react(iter([1, 2, 3]))
        mapped = wrapped.map(lambda x: x * 2)
        expect = IterChain if self.ispy3 else SeqChain
        self.assertIsInstance(mapped, expect)
        filtered = mapped.filter(lambda x: x >= 4)
        self.assertIsInstance(filtered, expect)
        expect = True if self.ispy3 else False
        self.assertEqual(filtered.isiterator, expect)
        self.assertEqual(filtered.reduce(lambda x, y: x + y), 10)

        #type converting
        wrapped = react(iter([1, 2, 3]))
        listed = wrapped.tolist
        self.assertEqual(listed.type, list)
        self.assertIsInstance(listed, SeqChain)

        wrapped = react(iter([1, 2, 3]))
        tupled = wrapped.totuple
        self.assertEqual(tupled.type, tuple)
        self.assertIsInstance(tupled, SeqChain)

        wrapped = react(iter([1, 2, 3]))
        setted = wrapped.toset
        self.assertEqual(setted.type, set)
        self.assertIsInstance(setted, SetChain)

    def testFile(self):
        #file iteration
        src1 = "used_in_test.data"
        src2 = os.path.join("test", src1)
        src = src1 if os.path.exists(src1) else src2
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
            
            with open(src) as f:
                wrapped = react(f)
                contents = [ln for ln in wrapped]
                self.assertEqual("".join(contents).replace("\n", ""), "123456789")
                self.assertFalse(f.closed)
            self.assertTrue(f)
            self.assertTrue(wrapped.unwrap.closed)

    def testPercentEncoding(self):
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
