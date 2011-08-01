import unittest
from __init__ import kwattr


@kwattr.wait.chdir.min.max.hide
def run(*args, **kwargs):
    return args, kwargs

@kwattr.all.dirs
def scan(arg, idir=False, ifile=True, all=False, dirs=False):
    return arg, idir, ifile, all, dirs


class Test(unittest.TestCase):
    def test00(self):
        with self.assertRaises(AttributeError):
            run.bad
        with self.assertRaises(TypeError):
            scan('f', bad=1)

    def test01(self):
        a = run.wait('test one')
        b = (('test one',), {'max': False, 'chdir': False, 'hide': False,
            'wait': True, 'min': False})
        self.assertEqual(a, b)

        a = run.wait.chdir('test one')
        b = (('test one',), {'max': False, 'chdir': True, 'hide': False,
            'wait': True, 'min': False})
        self.assertEqual(a, b)

        a = run('test one')
        b = (('test one',), {'max': False, 'chdir': False, 'hide': False,
            'wait': False, 'min': False})
        self.assertEqual(a, b)

        a = run.hide('f', hide=False)
        b = (('f',), {'max': False, 'chdir': False, 'hide': False,
            'wait': False, 'min': False})
        self.assertEqual(a, b)

    def test02(self):
        test = (kwattr, kwattr.wait, kwattr.wait, kwattr.hide)
        self.assertEqual(len({id(x) for x in test}), 4)
        self.assertEqual(len({id(x.kw) for x in test}), 4)

    def test03(self):
        test = (run, run.wait, run.wait, run.hide)
        self.assertEqual(len({id(x) for x in test}), 4)
        self.assertEqual(len({id(x.kw) for x in test}), 4)

    def test04(self):
        a = scan.all('t')
        b = ('t', False, True, True, False)
        self.assertEqual(a, b)

        a = scan.dirs('t')
        b = ('t', False, True, False, True)
        self.assertEqual(a, b)

        a = scan('t')
        b = ('t', False, True, False, False)
        self.assertEqual(a, b)

        a = scan('t', idir=True)
        b = ('t', True, True, False, False)
        self.assertEqual(a, b)

unittest.main()
