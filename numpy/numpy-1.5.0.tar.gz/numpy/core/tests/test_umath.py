import sys

from numpy.testing import *
import numpy.core.umath as ncu
import numpy as np


class TestDivision(TestCase):
    def test_division_int(self):
        # int division should follow Python
        x = np.array([5, 10, 90, 100, -5, -10, -90, -100, -120])
        if 5 / 10 == 0.5:
            assert_equal(x / 100, [0.05, 0.1, 0.9, 1,
                                   -0.05, -0.1, -0.9, -1, -1.2])
        else:
            assert_equal(x / 100, [0, 0, 0, 1, -1, -1, -1, -1, -2])
        assert_equal(x // 100, [0, 0, 0, 1, -1, -1, -1, -1, -2])
        assert_equal(x % 100, [5, 10, 90, 0, 95, 90, 10, 0, 80])

    def test_division_complex(self):
        # check that implementation is correct
        msg = "Complex division implementation check"
        x = np.array([1. + 1.*1j, 1. + .5*1j, 1. + 2.*1j], dtype=np.complex128)
        assert_almost_equal(x**2/x, x, err_msg=msg)
        # check overflow, underflow
        msg = "Complex division overflow/underflow check"
        x = np.array([1.e+110, 1.e-110], dtype=np.complex128)
        y = x**2/x
        assert_almost_equal(y/x, [1, 1], err_msg=msg)

    def test_floor_division_complex(self):
        # check that implementation is correct
        msg = "Complex floor division implementation check"
        x = np.array([.9 + 1j, -.1 + 1j, .9 + .5*1j, .9 + 2.*1j], dtype=np.complex128)
        y = np.array([0., -1., 0., 0.], dtype=np.complex128)
        assert_equal(np.floor_divide(x**2,x), y, err_msg=msg)
        # check overflow, underflow
        msg = "Complex floor division overflow/underflow check"
        x = np.array([1.e+110, 1.e-110], dtype=np.complex128)
        y = np.floor_divide(x**2, x)
        assert_equal(y, [1.e+110, 0], err_msg=msg)


class TestPower(TestCase):
    def test_power_float(self):
        x = np.array([1., 2., 3.])
        assert_equal(x**0, [1., 1., 1.])
        assert_equal(x**1, x)
        assert_equal(x**2, [1., 4., 9.])
        y = x.copy()
        y **= 2
        assert_equal(y, [1., 4., 9.])
        assert_almost_equal(x**(-1), [1., 0.5, 1./3])
        assert_almost_equal(x**(0.5), [1., ncu.sqrt(2), ncu.sqrt(3)])

    def test_power_complex(self):
        x = np.array([1+2j, 2+3j, 3+4j])
        assert_equal(x**0, [1., 1., 1.])
        assert_equal(x**1, x)
        assert_almost_equal(x**2, [-3+4j, -5+12j, -7+24j])
        assert_almost_equal(x**3, [(1+2j)**3, (2+3j)**3, (3+4j)**3])
        assert_almost_equal(x**4, [(1+2j)**4, (2+3j)**4, (3+4j)**4])
        assert_almost_equal(x**(-1), [1/(1+2j), 1/(2+3j), 1/(3+4j)])
        assert_almost_equal(x**(-2), [1/(1+2j)**2, 1/(2+3j)**2, 1/(3+4j)**2])
        assert_almost_equal(x**(-3), [(-11+2j)/125, (-46-9j)/2197,
                                      (-117-44j)/15625])
        assert_almost_equal(x**(0.5), [ncu.sqrt(1+2j), ncu.sqrt(2+3j),
                                       ncu.sqrt(3+4j)])
        norm = 1./((x**14)[0])
        assert_almost_equal(x**14 * norm,
                [i * norm for i in [-76443+16124j, 23161315+58317492j,
                                    5583548873 +  2465133864j]])

        # Ticket #836
        def assert_complex_equal(x, y):
            assert_array_equal(x.real, y.real)
            assert_array_equal(x.imag, y.imag)

        for z in [complex(0, np.inf), complex(1, np.inf)]:
            err = np.seterr(invalid="ignore")
            z = np.array([z], dtype=np.complex_)
            try:
                assert_complex_equal(z**1, z)
                assert_complex_equal(z**2, z*z)
                assert_complex_equal(z**3, z*z*z)
            finally:
                np.seterr(**err)

    def test_power_zero(self):
        # ticket #1271
        zero = np.array([0j])
        one = np.array([1+0j])
        cinf = np.array([complex(np.inf, 0)])
        cnan = np.array([complex(np.nan, np.nan)])

        def assert_complex_equal(x, y):
            x, y = np.asarray(x), np.asarray(y)
            assert_array_equal(x.real, y.real)
            assert_array_equal(x.imag, y.imag)

        # positive powers
        for p in [0.33, 0.5, 1, 1.5, 2, 3, 4, 5, 6.6]:
            assert_complex_equal(np.power(zero, p), zero)

        # zero power
        assert_complex_equal(np.power(zero, 0), one)
        assert_complex_equal(np.power(zero, 0+1j), cnan)

        # negative power
        for p in [0.33, 0.5, 1, 1.5, 2, 3, 4, 5, 6.6]:
            assert_complex_equal(np.power(zero, -p), cnan)
        assert_complex_equal(np.power(zero, -1+0.2j), cnan)


class TestLog2(TestCase):
    def test_log2_values(self) :
        x = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for dt in ['f','d','g'] :
            xf = np.array(x, dtype=dt)
            yf = np.array(y, dtype=dt)
            assert_almost_equal(np.log2(xf), yf)


class TestExp2(TestCase):
    def test_exp2_values(self) :
        x = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for dt in ['f','d','g'] :
            xf = np.array(x, dtype=dt)
            yf = np.array(y, dtype=dt)
            assert_almost_equal(np.exp2(yf), xf)


class TestLogAddExp2(object):
    # Need test for intermediate precisions
    def test_logaddexp2_values(self) :
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]
        z = [6, 6, 6, 6, 6]
        for dt, dec in zip(['f','d','g'],[6, 15, 15]) :
            xf = np.log2(np.array(x, dtype=dt))
            yf = np.log2(np.array(y, dtype=dt))
            zf = np.log2(np.array(z, dtype=dt))
            assert_almost_equal(np.logaddexp2(xf, yf), zf, decimal=dec)

    def test_logaddexp2_range(self) :
        x = [1000000, -1000000, 1000200, -1000200]
        y = [1000200, -1000200, 1000000, -1000000]
        z = [1000200, -1000000, 1000200, -1000000]
        for dt in ['f','d','g'] :
            logxf = np.array(x, dtype=dt)
            logyf = np.array(y, dtype=dt)
            logzf = np.array(z, dtype=dt)
            assert_almost_equal(np.logaddexp2(logxf, logyf), logzf)

    def test_inf(self) :
        err = np.seterr(invalid='ignore')
        inf = np.inf
        x = [inf, -inf,  inf, -inf, inf, 1,  -inf,  1]
        y = [inf,  inf, -inf, -inf, 1,   inf, 1,   -inf]
        z = [inf,  inf,  inf, -inf, inf, inf, 1,    1]
        try:
            for dt in ['f','d','g'] :
                logxf = np.array(x, dtype=dt)
                logyf = np.array(y, dtype=dt)
                logzf = np.array(z, dtype=dt)
                assert_equal(np.logaddexp2(logxf, logyf), logzf)
        finally:
            np.seterr(**err)

    def test_nan(self):
        err = np.seterr(invalid="ignore")
        try:
            assert np.isnan(np.logaddexp2(np.nan, np.inf))
            assert np.isnan(np.logaddexp2(np.inf, np.nan))
            assert np.isnan(np.logaddexp2(np.nan, 0))
            assert np.isnan(np.logaddexp2(0, np.nan))
            assert np.isnan(np.logaddexp2(np.nan, np.nan))
        finally:
            np.seterr(**err)


class TestLog(TestCase):
    def test_log_values(self) :
        x = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for dt in ['f','d','g'] :
            log2_ = 0.69314718055994530943
            xf = np.array(x, dtype=dt)
            yf = np.array(y, dtype=dt)*log2_
            assert_almost_equal(np.log(xf), yf)


class TestExp(TestCase):
    def test_exp_values(self) :
        x = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for dt in ['f','d','g'] :
            log2_ = 0.69314718055994530943
            xf = np.array(x, dtype=dt)
            yf = np.array(y, dtype=dt)*log2_
            assert_almost_equal(np.exp(yf), xf)


class TestLogAddExp(object):
    def test_logaddexp_values(self) :
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]
        z = [6, 6, 6, 6, 6]
        for dt, dec in zip(['f','d','g'],[6, 15, 15]) :
            xf = np.log(np.array(x, dtype=dt))
            yf = np.log(np.array(y, dtype=dt))
            zf = np.log(np.array(z, dtype=dt))
            assert_almost_equal(np.logaddexp(xf, yf), zf, decimal=dec)

    def test_logaddexp_range(self) :
        x = [1000000, -1000000, 1000200, -1000200]
        y = [1000200, -1000200, 1000000, -1000000]
        z = [1000200, -1000000, 1000200, -1000000]
        for dt in ['f','d','g'] :
            logxf = np.array(x, dtype=dt)
            logyf = np.array(y, dtype=dt)
            logzf = np.array(z, dtype=dt)
            assert_almost_equal(np.logaddexp(logxf, logyf), logzf)

    def test_inf(self) :
        err = np.seterr(invalid='ignore')
        inf = np.inf
        x = [inf, -inf,  inf, -inf, inf, 1,  -inf,  1]
        y = [inf,  inf, -inf, -inf, 1,   inf, 1,   -inf]
        z = [inf,  inf,  inf, -inf, inf, inf, 1,    1]
        try:
            for dt in ['f','d','g'] :
                logxf = np.array(x, dtype=dt)
                logyf = np.array(y, dtype=dt)
                logzf = np.array(z, dtype=dt)
                assert_equal(np.logaddexp(logxf, logyf), logzf)
        finally:
            np.seterr(**err)

    def test_nan(self):
        err = np.seterr(invalid="ignore")
        try:
            assert np.isnan(np.logaddexp(np.nan, np.inf))
            assert np.isnan(np.logaddexp(np.inf, np.nan))
            assert np.isnan(np.logaddexp(np.nan, 0))
            assert np.isnan(np.logaddexp(0, np.nan))
            assert np.isnan(np.logaddexp(np.nan, np.nan))
        finally:
            np.seterr(**err)


class TestLog1p(TestCase):
    def test_log1p(self):
        assert_almost_equal(ncu.log1p(0.2), ncu.log(1.2))
        assert_almost_equal(ncu.log1p(1e-6), ncu.log(1+1e-6))


class TestExpm1(TestCase):
    def test_expm1(self):
        assert_almost_equal(ncu.expm1(0.2), ncu.exp(0.2)-1)
        assert_almost_equal(ncu.expm1(1e-6), ncu.exp(1e-6)-1)


class TestHypot(TestCase, object):
    def test_simple(self):
        assert_almost_equal(ncu.hypot(1, 1), ncu.sqrt(2))
        assert_almost_equal(ncu.hypot(0, 0), 0)


def assert_hypot_isnan(x, y):
    err = np.seterr(invalid='ignore')
    try:
        assert np.isnan(ncu.hypot(x, y)), "hypot(%s, %s) is %s, not nan" % (x, y, ncu.hypot(x, y))
    finally:
        np.seterr(**err)


def assert_hypot_isinf(x, y):
    err = np.seterr(invalid='ignore')
    try:
        assert np.isinf(ncu.hypot(x, y)), "hypot(%s, %s) is %s, not inf" % (x, y, ncu.hypot(x, y))
    finally:
        np.seterr(**err)


class TestHypotSpecialValues(TestCase):
    def test_nan_outputs(self):
        assert_hypot_isnan(np.nan, np.nan)
        assert_hypot_isnan(np.nan, 1)

    def test_nan_outputs(self):
        assert_hypot_isinf(np.nan, np.inf)
        assert_hypot_isinf(np.inf, np.nan)
        assert_hypot_isinf(np.inf, 0)
        assert_hypot_isinf(0, np.inf)


def assert_arctan2_isnan(x, y):
    assert np.isnan(ncu.arctan2(x, y)), "arctan(%s, %s) is %s, not nan" % (x, y, ncu.arctan2(x, y))


def assert_arctan2_ispinf(x, y):
    assert (np.isinf(ncu.arctan2(x, y)) and ncu.arctan2(x, y) > 0), "arctan(%s, %s) is %s, not +inf" % (x, y, ncu.arctan2(x, y))


def assert_arctan2_isninf(x, y):
    assert (np.isinf(ncu.arctan2(x, y)) and ncu.arctan2(x, y) < 0), "arctan(%s, %s) is %s, not -inf" % (x, y, ncu.arctan2(x, y))


def assert_arctan2_ispzero(x, y):
    assert (ncu.arctan2(x, y) == 0 and not np.signbit(ncu.arctan2(x, y))), "arctan(%s, %s) is %s, not +0" % (x, y, ncu.arctan2(x, y))


def assert_arctan2_isnzero(x, y):
    assert (ncu.arctan2(x, y) == 0 and np.signbit(ncu.arctan2(x, y))), "arctan(%s, %s) is %s, not -0" % (x, y, ncu.arctan2(x, y))


class TestArctan2SpecialValues(TestCase):
    def test_one_one(self):
        # atan2(1, 1) returns pi/4.
        assert_almost_equal(ncu.arctan2(1, 1), 0.25 * np.pi)
        assert_almost_equal(ncu.arctan2(-1, 1), -0.25 * np.pi)
        assert_almost_equal(ncu.arctan2(1, -1), 0.75 * np.pi)

    def test_zero_nzero(self):
        # atan2(+-0, -0) returns +-pi.
        assert_almost_equal(ncu.arctan2(np.PZERO, np.NZERO), np.pi)
        assert_almost_equal(ncu.arctan2(np.NZERO, np.NZERO), -np.pi)

    def test_zero_pzero(self):
        # atan2(+-0, +0) returns +-0.
        assert_arctan2_ispzero(np.PZERO, np.PZERO)
        assert_arctan2_isnzero(np.NZERO, np.PZERO)

    def test_zero_negative(self):
        # atan2(+-0, x) returns +-pi for x < 0.
        assert_almost_equal(ncu.arctan2(np.PZERO, -1), np.pi)
        assert_almost_equal(ncu.arctan2(np.NZERO, -1), -np.pi)

    def test_zero_positive(self):
        # atan2(+-0, x) returns +-0 for x > 0.
        assert_arctan2_ispzero(np.PZERO, 1)
        assert_arctan2_isnzero(np.NZERO, 1)

    def test_positive_zero(self):
        # atan2(y, +-0) returns +pi/2 for y > 0.
        assert_almost_equal(ncu.arctan2(1, np.PZERO), 0.5 * np.pi)
        assert_almost_equal(ncu.arctan2(1, np.NZERO), 0.5 * np.pi)

    def test_negative_zero(self):
        # atan2(y, +-0) returns -pi/2 for y < 0.
        assert_almost_equal(ncu.arctan2(-1, np.PZERO), -0.5 * np.pi)
        assert_almost_equal(ncu.arctan2(-1, np.NZERO), -0.5 * np.pi)

    def test_any_ninf(self):
        # atan2(+-y, -infinity) returns +-pi for finite y > 0.
        assert_almost_equal(ncu.arctan2(1, np.NINF),  np.pi)
        assert_almost_equal(ncu.arctan2(-1, np.NINF), -np.pi)

    def test_any_pinf(self):
        # atan2(+-y, +infinity) returns +-0 for finite y > 0.
        assert_arctan2_ispzero(1, np.inf)
        assert_arctan2_isnzero(-1, np.inf)

    def test_inf_any(self):
        # atan2(+-infinity, x) returns +-pi/2 for finite x.
        assert_almost_equal(ncu.arctan2( np.inf, 1),  0.5 * np.pi)
        assert_almost_equal(ncu.arctan2(-np.inf, 1), -0.5 * np.pi)

    def test_inf_ninf(self):
        # atan2(+-infinity, -infinity) returns +-3*pi/4.
        assert_almost_equal(ncu.arctan2( np.inf, -np.inf),  0.75 * np.pi)
        assert_almost_equal(ncu.arctan2(-np.inf, -np.inf), -0.75 * np.pi)

    def test_inf_pinf(self):
        # atan2(+-infinity, +infinity) returns +-pi/4.
        assert_almost_equal(ncu.arctan2( np.inf, np.inf),  0.25 * np.pi)
        assert_almost_equal(ncu.arctan2(-np.inf, np.inf), -0.25 * np.pi)

    def test_nan_any(self):
        # atan2(nan, x) returns nan for any x, including inf
        assert_arctan2_isnan(np.nan, np.inf)
        assert_arctan2_isnan(np.inf, np.nan)
        assert_arctan2_isnan(np.nan, np.nan)


class TestLdexp(TestCase):
    def test_ldexp(self):
        assert_almost_equal(ncu.ldexp(2., 3),  16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.float32), np.array(3, np.int16)), 16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.float32), np.array(3, np.int32)), 16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.float64), np.array(3, np.int16)), 16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.float64), np.array(3, np.int32)), 16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.longdouble), np.array(3, np.int16)), 16.)
        assert_almost_equal(ncu.ldexp(np.array(2., np.longdouble), np.array(3, np.int32)), 16.)


class TestMaximum(TestCase):
    def test_reduce_complex(self):
        assert_equal(np.maximum.reduce([1,2j]),1)
        assert_equal(np.maximum.reduce([1+3j,2j]),1+3j)

    def test_float_nans(self):
        nan = np.nan
        arg1 = np.array([0,   nan, nan])
        arg2 = np.array([nan, 0,   nan])
        out  = np.array([nan, nan, nan])
        err = np.seterr(invalid="ignore")
        try:
            assert_equal(np.maximum(arg1, arg2), out)
        finally:
            np.seterr(**err)

    def test_complex_nans(self):
        nan = np.nan
        err = np.seterr(invalid="ignore")
        try:
            for cnan in [complex(nan, 0), complex(0, nan), complex(nan, nan)] :
                arg1 = np.array([0, cnan, cnan], dtype=np.complex)
                arg2 = np.array([cnan, 0, cnan], dtype=np.complex)
                out  = np.array([nan, nan, nan], dtype=np.complex)
                assert_equal(np.maximum(arg1, arg2), out)
        finally:
            np.seterr(**err)


class TestMinimum(TestCase):
    def test_reduce_complex(self):
        assert_equal(np.minimum.reduce([1,2j]),2j)
        assert_equal(np.minimum.reduce([1+3j,2j]),2j)

    def test_float_nans(self):
        nan = np.nan
        arg1 = np.array([0,   nan, nan])
        arg2 = np.array([nan, 0,   nan])
        out  = np.array([nan, nan, nan])
        err = np.seterr(invalid="ignore")
        try:
            assert_equal(np.minimum(arg1, arg2), out)
        finally:
            np.seterr(**err)

    def test_complex_nans(self):
        nan = np.nan
        err = np.seterr(invalid="ignore")
        try:
            for cnan in [complex(nan, 0), complex(0, nan), complex(nan, nan)] :
                arg1 = np.array([0, cnan, cnan], dtype=np.complex)
                arg2 = np.array([cnan, 0, cnan], dtype=np.complex)
                out  = np.array([nan, nan, nan], dtype=np.complex)
                assert_equal(np.minimum(arg1, arg2), out)
        finally:
            np.seterr(**err)


class TestFmax(TestCase):
    def test_reduce_complex(self):
        assert_equal(np.fmax.reduce([1,2j]),1)
        assert_equal(np.fmax.reduce([1+3j,2j]),1+3j)

    def test_float_nans(self):
        nan = np.nan
        arg1 = np.array([0,   nan, nan])
        arg2 = np.array([nan, 0,   nan])
        out  = np.array([0,   0,   nan])
        err = np.seterr(invalid="ignore")
        try:
            assert_equal(np.fmax(arg1, arg2), out)
        finally:
            np.seterr(**err)

    def test_complex_nans(self):
        nan = np.nan
        err = np.seterr(invalid="ignore")
        try:
            for cnan in [complex(nan, 0), complex(0, nan), complex(nan, nan)]:
                arg1 = np.array([0, cnan, cnan], dtype=np.complex)
                arg2 = np.array([cnan, 0, cnan], dtype=np.complex)
                out  = np.array([0,    0, nan], dtype=np.complex)
                assert_equal(np.fmax(arg1, arg2), out)
        finally:
            np.seterr(**err)


class TestFmin(TestCase):
    def test_reduce_complex(self):
        assert_equal(np.fmin.reduce([1,2j]),2j)
        assert_equal(np.fmin.reduce([1+3j,2j]),2j)

    def test_float_nans(self):
        nan = np.nan
        arg1 = np.array([0,   nan, nan])
        arg2 = np.array([nan, 0,   nan])
        out  = np.array([0,   0,   nan])
        err = np.seterr(invalid="ignore")
        try:
            assert_equal(np.fmin(arg1, arg2), out)
        finally:
            np.seterr(**err)

    def test_complex_nans(self):
        nan = np.nan
        err = np.seterr(invalid="ignore")
        try:
            for cnan in [complex(nan, 0), complex(0, nan), complex(nan, nan)]:
                arg1 = np.array([0, cnan, cnan], dtype=np.complex)
                arg2 = np.array([cnan, 0, cnan], dtype=np.complex)
                out  = np.array([0,    0, nan], dtype=np.complex)
                assert_equal(np.fmin(arg1, arg2), out)
        finally:
            np.seterr(**err)


class TestFloatingPoint(TestCase):
    def test_floating_point(self):
        assert_equal(ncu.FLOATING_POINT_SUPPORT, 1)


class TestDegrees(TestCase):
    def test_degrees(self):
        assert_almost_equal(ncu.degrees(np.pi), 180.0)
        assert_almost_equal(ncu.degrees(-0.5*np.pi), -90.0)


class TestRadians(TestCase):
    def test_radians(self):
        assert_almost_equal(ncu.radians(180.0), np.pi)
        assert_almost_equal(ncu.radians(-90.0), -0.5*np.pi)


class TestSign(TestCase):
    def test_sign(self):
        a = np.array([np.inf, -np.inf, np.nan, 0.0, 3.0, -3.0])
        out = np.zeros(a.shape)
        tgt = np.array([1., -1., np.nan, 0.0, 1.0, -1.0])

        olderr = np.seterr(invalid='ignore')
        try:
            res = ncu.sign(a)
            assert_equal(res, tgt)
            res = ncu.sign(a, out)
            assert_equal(res, tgt)
            assert_equal(out, tgt)
        finally:
            np.seterr(**olderr)


class TestSpecialMethods(TestCase):
    def test_wrap(self):
        class with_wrap(object):
            def __array__(self):
                return np.zeros(1)
            def __array_wrap__(self, arr, context):
                r = with_wrap()
                r.arr = arr
                r.context = context
                return r
        a = with_wrap()
        x = ncu.minimum(a, a)
        assert_equal(x.arr, np.zeros(1))
        func, args, i = x.context
        self.assertTrue(func is ncu.minimum)
        self.assertEqual(len(args), 2)
        assert_equal(args[0], a)
        assert_equal(args[1], a)
        self.assertEqual(i, 0)

    def test_wrap_with_iterable(self):
        # test fix for bug #1026:
        class with_wrap(np.ndarray):
            __array_priority__ = 10
            def __new__(cls):
                return np.asarray(1).view(cls).copy()
            def __array_wrap__(self, arr, context):
                return arr.view(type(self))
        a = with_wrap()
        x = ncu.multiply(a, (1, 2, 3))
        self.assertTrue(isinstance(x, with_wrap))
        assert_array_equal(x, np.array((1, 2, 3)))

    def test_priority_with_scalar(self):
        # test fix for bug #826:
        class A(np.ndarray):
            __array_priority__ = 10
            def __new__(cls):
                return np.asarray(1.0, 'float64').view(cls).copy()
        a = A()
        x = np.float64(1)*a
        self.assertTrue(isinstance(x, A))
        assert_array_equal(x, np.array(1))

    def test_old_wrap(self):
        class with_wrap(object):
            def __array__(self):
                return np.zeros(1)
            def __array_wrap__(self, arr):
                r = with_wrap()
                r.arr = arr
                return r
        a = with_wrap()
        x = ncu.minimum(a, a)
        assert_equal(x.arr, np.zeros(1))

    def test_priority(self):
        class A(object):
            def __array__(self):
                return np.zeros(1)
            def __array_wrap__(self, arr, context):
                r = type(self)()
                r.arr = arr
                r.context = context
                return r
        class B(A):
            __array_priority__ = 20.
        class C(A):
            __array_priority__ = 40.
        x = np.zeros(1)
        a = A()
        b = B()
        c = C()
        f = ncu.minimum
        self.assertTrue(type(f(x,x)) is np.ndarray)
        self.assertTrue(type(f(x,a)) is A)
        self.assertTrue(type(f(x,b)) is B)
        self.assertTrue(type(f(x,c)) is C)
        self.assertTrue(type(f(a,x)) is A)
        self.assertTrue(type(f(b,x)) is B)
        self.assertTrue(type(f(c,x)) is C)

        self.assertTrue(type(f(a,a)) is A)
        self.assertTrue(type(f(a,b)) is B)
        self.assertTrue(type(f(b,a)) is B)
        self.assertTrue(type(f(b,b)) is B)
        self.assertTrue(type(f(b,c)) is C)
        self.assertTrue(type(f(c,b)) is C)
        self.assertTrue(type(f(c,c)) is C)

        self.assertTrue(type(ncu.exp(a) is A))
        self.assertTrue(type(ncu.exp(b) is B))
        self.assertTrue(type(ncu.exp(c) is C))

    def test_failing_wrap(self):
        class A(object):
            def __array__(self):
                return np.zeros(1)
            def __array_wrap__(self, arr, context):
                raise RuntimeError
        a = A()
        self.assertRaises(RuntimeError, ncu.maximum, a, a)

    def test_default_prepare(self):
        class with_wrap(object):
            __array_priority__ = 10
            def __array__(self):
                return np.zeros(1)
            def __array_wrap__(self, arr, context):
                return arr
        a = with_wrap()
        x = ncu.minimum(a, a)
        assert_equal(x, np.zeros(1))
        assert_equal(type(x), np.ndarray)

    def test_prepare(self):
        class with_prepare(np.ndarray):
            __array_priority__ = 10
            def __array_prepare__(self, arr, context):
                # make sure we can return a new 
                return np.array(arr).view(type=with_prepare)
        a = np.array(1).view(type=with_prepare)
        x = np.add(a, a)
        assert_equal(x, np.array(2))
        assert_equal(type(x), with_prepare)

    def test_failing_prepare(self):
        class A(object):
            def __array__(self):
                return np.zeros(1)
            def __array_prepare__(self, arr, context=None):
                raise RuntimeError
        a = A()
        self.assertRaises(RuntimeError, ncu.maximum, a, a)

    def test_array_with_context(self):
        class A(object):
            def __array__(self, dtype=None, context=None):
                func, args, i = context
                self.func = func
                self.args = args
                self.i = i
                return np.zeros(1)
        class B(object):
            def __array__(self, dtype=None):
                return np.zeros(1, dtype)
        class C(object):
            def __array__(self):
                return np.zeros(1)
        a = A()
        ncu.maximum(np.zeros(1), a)
        self.assertTrue(a.func is ncu.maximum)
        assert_equal(a.args[0], 0)
        self.assertTrue(a.args[1] is a)
        self.assertTrue(a.i == 1)
        assert_equal(ncu.maximum(a, B()), 0)
        assert_equal(ncu.maximum(a, C()), 0)


class TestChoose(TestCase):
    def test_mixed(self):
        c = np.array([True,True])
        a = np.array([True,True])
        assert_equal(np.choose(c, (a, 1)), np.array([1,1]))


def is_longdouble_finfo_bogus():
    info = np.finfo(np.longcomplex)
    return not np.isfinite(np.log10(info.tiny/info.eps))


class TestComplexFunctions(object):
    funcs = [np.arcsin,  np.arccos,  np.arctan, np.arcsinh, np.arccosh,
             np.arctanh, np.sin,     np.cos,    np.tan,     np.exp,
             np.exp2,    np.log,     np.sqrt,   np.log10,   np.log2,
             np.log1p]

    def test_it(self):
        for f in self.funcs:
            if f is np.arccosh :
                x = 1.5
            else :
                x = .5
            fr = f(x)
            fz = f(np.complex(x))
            assert_almost_equal(fz.real, fr, err_msg='real part %s'%f)
            assert_almost_equal(fz.imag, 0., err_msg='imag part %s'%f)

    def test_precisions_consistent(self) :
        z = 1 + 1j
        for f in self.funcs :
            fcf = f(np.csingle(z))
            fcd  = f(np.cdouble(z))
            fcl = f(np.clongdouble(z))
            assert_almost_equal(fcf, fcd, decimal=6, err_msg='fch-fcd %s'%f)
            assert_almost_equal(fcl, fcd, decimal=15, err_msg='fch-fcl %s'%f)

    def test_branch_cuts(self):
        # check branch cuts and continuity on them
        yield _check_branch_cut, np.log,   -0.5, 1j, 1, -1
        yield _check_branch_cut, np.log2,  -0.5, 1j, 1, -1
        yield _check_branch_cut, np.log10, -0.5, 1j, 1, -1
        yield _check_branch_cut, np.log1p, -1.5, 1j, 1, -1
        yield _check_branch_cut, np.sqrt,  -0.5, 1j, 1, -1

        yield _check_branch_cut, np.arcsin, [ -2, 2],   [1j, -1j], 1, -1
        yield _check_branch_cut, np.arccos, [ -2, 2],   [1j, -1j], 1, -1
        yield _check_branch_cut, np.arctan, [-2j, 2j],  [1,  -1 ], -1, 1

        yield _check_branch_cut, np.arcsinh, [-2j,  2j], [-1,   1], -1, 1
        yield _check_branch_cut, np.arccosh, [ -1, 0.5], [1j,  1j], 1, -1
        yield _check_branch_cut, np.arctanh, [ -2,   2], [1j, -1j], 1, -1

        # check against bogus branch cuts: assert continuity between quadrants
        yield _check_branch_cut, np.arcsin, [-2j, 2j], [ 1,  1], 1, 1
        yield _check_branch_cut, np.arccos, [-2j, 2j], [ 1,  1], 1, 1
        yield _check_branch_cut, np.arctan, [ -2,  2], [1j, 1j], 1, 1

        yield _check_branch_cut, np.arcsinh, [ -2,  2, 0], [1j, 1j, 1 ], 1, 1
        yield _check_branch_cut, np.arccosh, [-2j, 2j, 2], [1,  1,  1j], 1, 1
        yield _check_branch_cut, np.arctanh, [-2j, 2j, 0], [1,  1,  1j], 1, 1

    @dec.knownfailureif(True, "These branch cuts are known to fail")
    def test_branch_cuts_failing(self):
        # XXX: signed zero not OK with ICC on 64-bit platform for log, see
        # http://permalink.gmane.org/gmane.comp.python.numeric.general/25335
        yield _check_branch_cut, np.log,   -0.5, 1j, 1, -1, True
        yield _check_branch_cut, np.log2,  -0.5, 1j, 1, -1, True
        yield _check_branch_cut, np.log10, -0.5, 1j, 1, -1, True
        yield _check_branch_cut, np.log1p, -1.5, 1j, 1, -1, True
        # XXX: signed zeros are not OK for sqrt or for the arc* functions
        yield _check_branch_cut, np.sqrt,  -0.5, 1j, 1, -1, True
        yield _check_branch_cut, np.arcsin, [ -2, 2],   [1j, -1j], 1, -1, True
        yield _check_branch_cut, np.arccos, [ -2, 2],   [1j, -1j], 1, -1, True
        yield _check_branch_cut, np.arctan, [-2j, 2j],  [1,  -1 ], -1, 1, True
        yield _check_branch_cut, np.arcsinh, [-2j,  2j], [-1,   1], -1, 1, True
        yield _check_branch_cut, np.arccosh, [ -1, 0.5], [1j,  1j], 1, -1, True
        yield _check_branch_cut, np.arctanh, [ -2,   2], [1j, -1j], 1, -1, True

    def test_against_cmath(self):
        import cmath, sys

        # cmath.asinh is broken in some versions of Python, see
        # http://bugs.python.org/issue1381
        broken_cmath_asinh = False
        if sys.version_info < (2,6):
            broken_cmath_asinh = True

        points = [-1-1j, -1+1j, +1-1j, +1+1j]
        name_map = {'arcsin': 'asin', 'arccos': 'acos', 'arctan': 'atan',
                    'arcsinh': 'asinh', 'arccosh': 'acosh', 'arctanh': 'atanh'}
        atol = 4*np.finfo(np.complex).eps
        for func in self.funcs:
            fname = func.__name__.split('.')[-1]
            cname = name_map.get(fname, fname)
            try:
                cfunc = getattr(cmath, cname)
            except AttributeError:
                continue
            for p in points:
                a = complex(func(np.complex_(p)))
                b = cfunc(p)

                if cname == 'asinh' and broken_cmath_asinh:
                    continue

                assert abs(a - b) < atol, "%s %s: %s; cmath: %s"%(fname,p,a,b)

    def check_loss_of_precision(self, dtype):
        """Check loss of precision in complex arc* functions"""

        # Check against known-good functions

        info = np.finfo(dtype)
        real_dtype = dtype(0.).real.dtype
        eps = info.eps

        def check(x, rtol):
            x = x.astype(real_dtype)

            z = x.astype(dtype)
            d = np.absolute(np.arcsinh(x)/np.arcsinh(z).real - 1)
            assert np.all(d < rtol), (np.argmax(d), x[np.argmax(d)], d.max(),
                                      'arcsinh')

            z = (1j*x).astype(dtype)
            d = np.absolute(np.arcsinh(x)/np.arcsin(z).imag - 1)
            assert np.all(d < rtol), (np.argmax(d), x[np.argmax(d)], d.max(),
                                      'arcsin')

            z = x.astype(dtype)
            d = np.absolute(np.arctanh(x)/np.arctanh(z).real - 1)
            assert np.all(d < rtol), (np.argmax(d), x[np.argmax(d)], d.max(),
                                      'arctanh')

            z = (1j*x).astype(dtype)
            d = np.absolute(np.arctanh(x)/np.arctan(z).imag - 1)
            assert np.all(d < rtol), (np.argmax(d), x[np.argmax(d)], d.max(),
                                      'arctan')

        # The switchover was chosen as 1e-3; hence there can be up to
        # ~eps/1e-3 of relative cancellation error before it

        x_series = np.logspace(-20, -3.001, 200)
        x_basic = np.logspace(-2.999, 0, 10, endpoint=False)

        if dtype is np.longcomplex:
            # It's not guaranteed that the system-provided arc functions
            # are accurate down to a few epsilons. (Eg. on Linux 64-bit)
            # So, give more leeway for long complex tests here:
            check(x_series, 50*eps)
        else:
            check(x_series, 2*eps)
        check(x_basic, 2*eps/1e-3)

        # Check a few points

        z = np.array([1e-5*(1+1j)], dtype=dtype)
        p = 9.999999999333333333e-6 + 1.000000000066666666e-5j
        d = np.absolute(1-np.arctanh(z)/p)
        assert np.all(d < 1e-15)

        p = 1.0000000000333333333e-5 + 9.999999999666666667e-6j
        d = np.absolute(1-np.arcsinh(z)/p)
        assert np.all(d < 1e-15)

        p = 9.999999999333333333e-6j + 1.000000000066666666e-5
        d = np.absolute(1-np.arctan(z)/p)
        assert np.all(d < 1e-15)

        p = 1.0000000000333333333e-5j + 9.999999999666666667e-6
        d = np.absolute(1-np.arcsin(z)/p)
        assert np.all(d < 1e-15)

        # Check continuity across switchover points

        def check(func, z0, d=1):
            z0 = np.asarray(z0, dtype=dtype)
            zp = z0 + abs(z0) * d * eps * 2
            zm = z0 - abs(z0) * d * eps * 2
            assert np.all(zp != zm), (zp, zm)

            # NB: the cancellation error at the switchover is at least eps
            good = (abs(func(zp) - func(zm)) < 2*eps)
            assert np.all(good), (func, z0[~good])

        for func in (np.arcsinh,np.arcsinh,np.arcsin,np.arctanh,np.arctan):
            pts = [rp+1j*ip for rp in (-1e-3,0,1e-3) for ip in(-1e-3,0,1e-3)
                   if rp != 0 or ip != 0]
            check(func, pts, 1)
            check(func, pts, 1j)
            check(func, pts, 1+1j)

    def test_loss_of_precision(self):
        for dtype in [np.complex64, np.complex_]:
            yield self.check_loss_of_precision, dtype

    @dec.knownfailureif(is_longdouble_finfo_bogus(), "Bogus long double finfo")
    def test_loss_of_precision_longcomplex(self):
        self.check_loss_of_precision(np.longcomplex)


class TestAttributes(TestCase):
    def test_attributes(self):
        add = ncu.add
        assert_equal(add.__name__, 'add')
        assert add.__doc__.startswith('add(x1, x2[, out])\n\n')
        self.assertTrue(add.ntypes >= 18) # don't fail if types added
        self.assertTrue('ii->i' in add.types)
        assert_equal(add.nin, 2)
        assert_equal(add.nout, 1)
        assert_equal(add.identity, 0)


class TestSubclass(TestCase):
    def test_subclass_op(self):
        class simple(np.ndarray):
            def __new__(subtype, shape):
                self = np.ndarray.__new__(subtype, shape, dtype=object)
                self.fill(0)
                return self
        a = simple((3,4))
        assert_equal(a+a, a)

def _check_branch_cut(f, x0, dx, re_sign=1, im_sign=-1, sig_zero_ok=False,
                      dtype=np.complex):
    """
    Check for a branch cut in a function.

    Assert that `x0` lies on a branch cut of function `f` and `f` is
    continuous from the direction `dx`.

    Parameters
    ----------
    f : func
        Function to check
    x0 : array-like
        Point on branch cut
    dx : array-like
        Direction to check continuity in
    re_sign, im_sign : {1, -1}
        Change of sign of the real or imaginary part expected
    sig_zero_ok : bool
        Whether to check if the branch cut respects signed zero (if applicable)
    dtype : dtype
        Dtype to check (should be complex)

    """
    x0 = np.atleast_1d(x0).astype(dtype)
    dx = np.atleast_1d(dx).astype(dtype)

    scale = np.finfo(dtype).eps * 1e3
    atol  = 1e-4

    y0 = f(x0)
    yp = f(x0 + dx*scale*np.absolute(x0)/np.absolute(dx))
    ym = f(x0 - dx*scale*np.absolute(x0)/np.absolute(dx))

    assert np.all(np.absolute(y0.real - yp.real) < atol), (y0, yp)
    assert np.all(np.absolute(y0.imag - yp.imag) < atol), (y0, yp)
    assert np.all(np.absolute(y0.real - ym.real*re_sign) < atol), (y0, ym)
    assert np.all(np.absolute(y0.imag - ym.imag*im_sign) < atol), (y0, ym)

    if sig_zero_ok:
        # check that signed zeros also work as a displacement
        jr = (x0.real == 0) & (dx.real != 0)
        ji = (x0.imag == 0) & (dx.imag != 0)

        x = -x0
        x.real[jr] = 0.*dx.real
        x.imag[ji] = 0.*dx.imag
        x = -x
        ym = f(x)
        ym = ym[jr | ji]
        y0 = y0[jr | ji]
        assert np.all(np.absolute(y0.real - ym.real*re_sign) < atol), (y0, ym)
        assert np.all(np.absolute(y0.imag - ym.imag*im_sign) < atol), (y0, ym)

def test_copysign():
    assert np.copysign(1, -1) == -1
    old_err = np.seterr(divide="ignore")
    try:
        assert 1 / np.copysign(0, -1) < 0
        assert 1 / np.copysign(0, 1) > 0
    finally:
        np.seterr(**old_err)
    assert np.signbit(np.copysign(np.nan, -1))
    assert not np.signbit(np.copysign(np.nan, 1))

def _test_nextafter(t):
    one = t(1)
    two = t(2)
    zero = t(0)
    eps = np.finfo(t).eps
    assert np.nextafter(one, two) - one == eps
    assert np.nextafter(one, zero) - one < 0
    assert np.isnan(np.nextafter(np.nan, one))
    assert np.isnan(np.nextafter(one, np.nan))
    assert np.nextafter(one, one) == one

def test_nextafter():
    return _test_nextafter(np.float64)

def test_nextafterf():
    return _test_nextafter(np.float32)

@dec.knownfailureif(sys.platform == 'win32', "Long double support buggy on win32")
def test_nextafterl():
    return _test_nextafter(np.longdouble)

def _test_spacing(t):
    err = np.seterr(invalid='ignore')
    one = t(1)
    eps = np.finfo(t).eps
    nan = t(np.nan)
    inf = t(np.inf)
    try:
        assert np.spacing(one) == eps
        assert np.isnan(np.spacing(nan))
        assert np.isnan(np.spacing(inf))
        assert np.isnan(np.spacing(-inf))
        assert np.spacing(t(1e30)) != 0
    finally:
        np.seterr(**err)

def test_spacing():
    return _test_spacing(np.float64)

def test_spacingf():
    return _test_spacing(np.float32)

@dec.knownfailureif(sys.platform == 'win32', "Long double support buggy on win32")
def test_spacingl():
    return _test_spacing(np.longdouble)

def test_spacing_gfortran():
    # Reference from this fortran file, built with gfortran 4.3.3 on linux
    # 32bits:
    #       PROGRAM test_spacing
    #        INTEGER, PARAMETER :: SGL = SELECTED_REAL_KIND(p=6, r=37)
    #        INTEGER, PARAMETER :: DBL = SELECTED_REAL_KIND(p=13, r=200)
    #
    #        WRITE(*,*) spacing(0.00001_DBL)
    #        WRITE(*,*) spacing(1.0_DBL)
    #        WRITE(*,*) spacing(1000._DBL)
    #        WRITE(*,*) spacing(10500._DBL)
    #
    #        WRITE(*,*) spacing(0.00001_SGL)
    #        WRITE(*,*) spacing(1.0_SGL)
    #        WRITE(*,*) spacing(1000._SGL)
    #        WRITE(*,*) spacing(10500._SGL)
    #       END PROGRAM
    ref = {}
    ref[np.float64] = [1.69406589450860068E-021,
           2.22044604925031308E-016,
           1.13686837721616030E-013,
           1.81898940354585648E-012]
    ref[np.float32] = [
            9.09494702E-13,
            1.19209290E-07,
            6.10351563E-05,
            9.76562500E-04]

    for dt, dec in zip([np.float32, np.float64], (10, 20)):
        x = np.array([1e-5, 1, 1000, 10500], dtype=dt)
        assert_array_almost_equal(np.spacing(x), ref[dt], decimal=dec)

def test_nextafter_vs_spacing():
    # XXX: spacing does not handle long double yet
    for t in [np.float32, np.float64]:
        for _f in [1, 1e-5, 1000]:
            f = t(_f)
            f1 = t(_f + 1)
            assert np.nextafter(f, f1) - f == np.spacing(f)

def test_pos_nan():
    """Check np.nan is a positive nan."""
    assert np.signbit(np.nan) == 0

def test_reduceat():
    """Test bug in reduceat when structured arrays are not copied."""
    db = np.dtype([('name', 'S11'),('time', np.int64), ('value', np.float32)])
    a = np.empty([100], dtype=db)
    a['name'] = 'Simple'
    a['time'] = 10
    a['value'] = 100
    indx = [0,7,15,25]

    h2 = []
    val1 = indx[0]
    for val2 in indx[1:]:
        h2.append(np.add.reduce(a['value'][val1:val2]))
        val1 = val2
    h2.append(np.add.reduce(a['value'][val1:]))
    h2 = np.array(h2)

    # test buffered -- this should work
    h1 = np.add.reduceat(a['value'], indx)    
    assert_array_almost_equal(h1, h2)

    # This is when the error occurs.
    # test no buffer
    res = np.setbufsize(32)
    h1 = np.add.reduceat(a['value'], indx)
    np.setbufsize(np.UFUNC_BUFSIZE_DEFAULT)    
    assert_array_almost_equal(h1, h2)
        

def test_complex_nan_comparisons():
    nans = [complex(np.nan, 0), complex(0, np.nan), complex(np.nan, np.nan)]
    fins = [complex(1, 0), complex(-1, 0), complex(0, 1), complex(0, -1),
            complex(1, 1), complex(-1, -1), complex(0, 0)]

    err = np.seterr(invalid="ignore")
    try:
        for x in nans + fins:
            x = np.array([x])
            for y in nans + fins:
                y = np.array([y])
    
                if np.isfinite(x) and np.isfinite(y):
                    continue
    
                assert_equal(x < y, False, err_msg="%r < %r" % (x, y))
                assert_equal(x > y, False, err_msg="%r > %r" % (x, y))
                assert_equal(x <= y, False, err_msg="%r <= %r" % (x, y))
                assert_equal(x >= y, False, err_msg="%r >= %r" % (x, y))
                assert_equal(x == y, False, err_msg="%r == %r" % (x, y))
    finally:
        np.seterr(**err)

if __name__ == "__main__":
    run_module_suite()
