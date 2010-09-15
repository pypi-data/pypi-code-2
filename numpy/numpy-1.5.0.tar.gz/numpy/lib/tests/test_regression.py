from numpy.testing import *
from numpy.testing.utils import _assert_valid_refcount
import numpy as np

rlevel = 1

class TestRegression(TestCase):
    def test_poly1d(self,level=rlevel):
        """Ticket #28"""
        assert_equal(np.poly1d([1]) - np.poly1d([1,0]),
                     np.poly1d([-1,1]))

    def test_cov_parameters(self,level=rlevel):
        """Ticket #91"""
        x = np.random.random((3,3))
        y = x.copy()
        np.cov(x, rowvar=1)
        np.cov(y, rowvar=0)
        assert_array_equal(x,y)

    def test_mem_digitize(self,level=rlevel):
        """Ticket #95"""
        for i in range(100):
            np.digitize([1,2,3,4],[1,3])
            np.digitize([0,1,2,3,4],[1,3])

    def test_unique_zero_sized(self,level=rlevel):
        """Ticket #205"""
        assert_array_equal([], np.unique(np.array([])))

    def test_mem_vectorise(self, level=rlevel):
        """Ticket #325"""
        vt = np.vectorize(lambda *args: args)
        vt(np.zeros((1,2,1)), np.zeros((2,1,1)), np.zeros((1,1,2)))
        vt(np.zeros((1,2,1)), np.zeros((2,1,1)), np.zeros((1,1,2)), np.zeros((2,2)))

    def test_mgrid_single_element(self, level=rlevel):
        """Ticket #339"""
        assert_array_equal(np.mgrid[0:0:1j],[0])
        assert_array_equal(np.mgrid[0:0],[])

    def test_refcount_vectorize(self, level=rlevel):
        """Ticket #378"""
        def p(x,y): return 123
        v = np.vectorize(p)
        _assert_valid_refcount(v)

    def test_poly1d_nan_roots(self, level=rlevel):
        """Ticket #396"""
        p = np.poly1d([np.nan,np.nan,1], r=0)
        self.assertRaises(np.linalg.LinAlgError,getattr,p,"r")

    def test_mem_polymul(self, level=rlevel):
        """Ticket #448"""
        np.polymul([],[1.])

    def test_mem_string_concat(self, level=rlevel):
        """Ticket #469"""
        x = np.array([])
        np.append(x,'asdasd\tasdasd')

    def test_poly_div(self, level=rlevel):
        """Ticket #553"""
        u = np.poly1d([1,2,3])
        v = np.poly1d([1,2,3,4,5])
        q,r = np.polydiv(u,v)
        assert_equal(q*v + r, u)

    def test_poly_eq(self, level=rlevel):
        """Ticket #554"""
        x = np.poly1d([1,2,3])
        y = np.poly1d([3,4])
        assert x != y
        assert x == x

    def test_mem_insert(self, level=rlevel):
        """Ticket #572"""
        np.lib.place(1,1,1)

    def test_polyfit_build(self):
        """Ticket #628"""
        ref = [-1.06123820e-06, 5.70886914e-04, -1.13822012e-01,
                9.95368241e+00, -3.14526520e+02]
        x = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103,
             104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115,
             116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 129,
             130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141,
             146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157,
             158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169,
             170, 171, 172, 173, 174, 175, 176]
        y = [9.0, 3.0, 7.0, 4.0, 4.0, 8.0, 6.0, 11.0, 9.0, 8.0, 11.0, 5.0,
             6.0, 5.0, 9.0, 8.0, 6.0, 10.0, 6.0, 10.0, 7.0, 6.0, 6.0, 6.0,
             13.0, 4.0, 9.0, 11.0, 4.0, 5.0, 8.0, 5.0, 7.0, 7.0, 6.0, 12.0,
             7.0, 7.0, 9.0, 4.0, 12.0, 6.0, 6.0, 4.0, 3.0, 9.0, 8.0, 8.0,
             6.0, 7.0, 9.0, 10.0, 6.0, 8.0, 4.0, 7.0, 7.0, 10.0, 8.0, 8.0,
             6.0, 3.0, 8.0, 4.0, 5.0, 7.0, 8.0, 6.0, 6.0, 4.0, 12.0, 9.0,
             8.0, 8.0, 8.0, 6.0, 7.0, 4.0, 4.0, 5.0, 7.0]
        tested = np.polyfit(x, y, 4)
        assert_array_almost_equal(ref, tested)


    def test_polydiv_type(self) :
        """Make polydiv work for complex types"""
        msg = "Wrong type, should be complex"
        x = np.ones(3, dtype=np.complex)
        q,r = np.polydiv(x,x)
        assert_(q.dtype == np.complex, msg)
        msg = "Wrong type, should be float"
        x = np.ones(3, dtype=np.int)
        q,r = np.polydiv(x,x)
        assert_(q.dtype == np.float, msg)

    def test_histogramdd_too_many_bins(self) :
        """Ticket 928."""
        assert_raises(ValueError, np.histogramdd, np.ones((1,10)), bins=2**10)

    def test_polyint_type(self) :
        """Ticket #944"""
        msg = "Wrong type, should be complex"
        x = np.ones(3, dtype=np.complex)
        assert_(np.polyint(x).dtype == np.complex, msg)
        msg = "Wrong type, should be float"
        x = np.ones(3, dtype=np.int)
        assert_(np.polyint(x).dtype == np.float, msg)

    def test_ndenumerate_crash(self):
        """Ticket 1140"""
        # Shouldn't crash:
        list(np.ndenumerate(np.array([[]])))

    def test_asfarray_none(self, level=rlevel):
        """Test for changeset r5065"""
        assert_array_equal(np.array([np.nan]), np.asfarray([None]))

    def test_large_fancy_indexing(self, level=rlevel):
        # Large enough to fail on 64-bit.
        nbits = np.dtype(np.intp).itemsize * 8
        thesize = int((2**nbits)**(1.0/5.0)+1)
        def dp():
            n = 3
            a = np.ones((n,)*5)
            i = np.random.randint(0,n,size=thesize)
            a[np.ix_(i,i,i,i,i)] = 0
        def dp2():
            n = 3
            a = np.ones((n,)*5)
            i = np.random.randint(0,n,size=thesize)
            g = a[np.ix_(i,i,i,i,i)]
        self.assertRaises(ValueError, dp)
        self.assertRaises(ValueError, dp2)

    def test_void_coercion(self, level=rlevel):
        dt = np.dtype([('a','f4'),('b','i4')])
        x = np.zeros((1,),dt)
        assert(np.r_[x,x].dtype == dt)

    def test_who_with_0dim_array(self, level=rlevel) :
        """ticket #1243"""
        import os, sys

        sys.stdout = open(os.devnull, 'w')
        try :
            tmp = np.who({'foo' : np.array(1)})
            sys.stdout = sys.__stdout__
        except :
            sys.stdout = sys.__stdout__
            raise AssertionError("ticket #1243")

    def test_bincount_empty(self):
        """Ticket #1387: empty array as input for bincount."""
        assert_raises(ValueError, lambda : np.bincount(np.array([], dtype=np.intp)))

    @dec.deprecated()
    def test_include_dirs(self):
        """As a sanity check, just test that get_include and
        get_numarray_include include something reasonable.  Somewhat
        related to ticket #1405."""
        include_dirs = [np.get_include(), np.get_numarray_include(),
                        np.get_numpy_include()]
        for path in include_dirs:
            assert isinstance(path, (str, unicode))
            assert path != ''

    def test_polyder_return_type(self):
        """Ticket #1249"""
        assert_(isinstance(np.polyder(np.poly1d([1]), 0), np.poly1d))
        assert_(isinstance(np.polyder([1], 0), np.ndarray))
        assert_(isinstance(np.polyder(np.poly1d([1]), 1), np.poly1d))
        assert_(isinstance(np.polyder([1], 1), np.ndarray))


if __name__ == "__main__":
    run_module_suite()
