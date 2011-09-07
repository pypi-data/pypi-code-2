class Myobject(object):
    def __hash__(self):
        print "__hash__", self
        return hash(self.pk)
    def __eq__(self, other):
        print "__eq__", self, other
        return (type(other) == type(self) and
                other.__dict__.keys() == self.__dict__.keys() and
                all(getattr(other, key) == getattr(self, key)
                    for key in self.__dict__.keys()))
    def __ne__(self, other):
        print "__ne__", self, other
        if type(other) != type(self): return True
        if any(getattr(other, key) != getattr(self, key) \
                   for key in self.__dict__.keys()):
            return True

class HashAndEqTest(): #unittest.TestCase):
    def test_it(self):
        a = Myobject()
        a.pk = 1
        b = Myobject()
        b.pk = 1
        b.anotherattr = "value"
        myset = set()
        myset.add(a)
        myset.add(b)

        assert len(myset) == 1, len(myset)
        assert a != b
