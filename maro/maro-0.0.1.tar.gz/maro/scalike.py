# -*- coding:utf-8 -*-

"""
------------------------------
usage this module
------------------------------
>>> class dummy(object):
...     def __init__(self, **kwargs):
...         for k,v in kwargs.items():
...             setattr(self, k, v)
>>> imagawa = dummy(yakata=dummy(maro="hohoho..."))
>>> inagawa = dummy(junji="gagaga...")
>>> # 今川は館を持っている。しかし稲川は持っていない。
>>> some(imagawa).yakata.maro.value == "hohoho..."
True
>>> some(inagawa).yakata.maro.value is None
True
>>> # 今川は淳二を持っていない。しかし稲川は持っている。
>>> some(imagawa).junji.value is None
True
>>> some(inagawa).junji.value == "gagaga..."
True
"""

class some(object):
    def __init__(self, value):
        self.value = value

    def __getattribute__(self, name):
        g = object.__getattribute__
        v = g(self, "value")
        return v if name == "value" else some(g(v, name))

    def __getattr__(self, name):
        return none(None)

    def __call__(self, *args, **kwargs):
        """self.valueを関数とみなして呼びます。 
        ----------
        usage
        ----------
        >>> imagawa = some("ahaha,hohoho,maro")
        >>> imagawa.value.split(",")
        ['ahaha', 'hohoho', 'maro']
        >>> imagawa.split(",")
        ['ahaha', 'hohoho', 'maro']
        """
        return self.value(*args, **kwargs) 

class none(some):
    def __getattr__(self, name):
        return self
    
    def __call__(self, *args, **kwargs):
        """何もしません。自分自身を返します。
        ----------
        usage
        ----------
        >>> imagawa = some("   I hate war.  ")
        >>> imagawa.strip()
        'I hate war.'
        >>> type(imagawa.show()) == none
        True
        """
        return self

if __name__ == "__main__":
    import doctest
    doctest.testmod()

