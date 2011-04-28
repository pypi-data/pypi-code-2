import unittest
from reverb import *

class TestReverb(unittest.TestCase):
    def test_Text(self):
        self.assertEqual(Re(Text("abc")).pattern, r"abc")
        self.assertEqual(Re(Text("[abc]")).pattern, r"\[abc\]")
        self.assertEqual(Re(Text("^abc")).pattern, r"\^abc")
        self.assertEqual(Re(Text("^abc")+Text("$")).pattern, r"\^abc\$")
        self.assertEqual(Re(Text("^abc")+"$").pattern, r"\^abc\$")
        self.assertEqual(Re(Text("^abc")&"$").pattern, r"\^abc\$")
        self.assertEqual(Re("$"+Text("^abc")).pattern, r"\$\^abc")
        self.assertRaises(TypeError, lambda: Text("^abc")-"t")

    def test_Repeated(self):
        self.assertEqual(Re(Repeated("a",0)).pattern, r"a*")
        self.assertEqual(Re(Repeated("a",0,1)).pattern, r"a?")
        self.assertEqual(Re(Repeated("a",1)).pattern, r"a+")
        self.assertEqual(Re(Repeated("a",2)).pattern, r"a{2,}")
        self.assertEqual(Re(Repeated("a",1,2)).pattern, r"a{1,2}")
        self.assertEqual(Re(Maybe("a")).pattern, r"a?")
        self.assertEqual(Re(Optional("a")).pattern, r"a*")
        self.assertEqual(Re(Required("a")).pattern, r"a+")

    def test_Group(self):
        self.assertEqual(Re(Group("ab")).pattern, "(ab)")
        self.assertEqual(Re(Group("ab", name="foo")).pattern, "(?P<foo>ab)")

    def test_Set(self):
        self.assertEqual(Re(Set("ab")).pattern, "[ab]")
        self.assertEqual(Re(Set("[ab")).pattern, "[[ab]")

    def test_Set(self):
        self.assertEqual(Re(Set("ab")).pattern, "[ab]")
        self.assertEqual(Re(Set("[ab")).pattern, "[[ab]")

    def test_Greedy(self):
        self.assertEqual(Re(Maybe("a").nongreedy).pattern, r"a??")
        self.assertEqual(Re(Required("a").nongreedy).pattern, r"a+?")
        self.assertEqual(Re(Optional("a").nongreedy).pattern, r"a*?")


unittest.main()


