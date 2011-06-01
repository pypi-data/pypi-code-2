# coding: utf-8
from scipy import real, sqrt, rand, randn

def cvar(x):
    m  = x.mean(-1)
    xo = (x.transpose() - m.transpose()).transpose()
    v  = real(xo * xo.conj()).mean(-1)
    return v, m

def norm_mv(x):
    v , m  = cvar(x)
    xn = ((x.transpose() - m.transpose()) / sqrt(v.transpose())).transpose()
    return xn, m, v

def crand(*arg):
    '''
    complex uniform random n-d array
    '''
    n = 1
    for i in arg:
        n = n * i
    if n < 100:
        o = 200
    else:
        o = 2 * n
    r = 2 * rand(o) - 1
    i = 2 * rand(o) - 1
    b = sqrt(r * r + i * i) < 1
    c = r[b.nonzero()][:n] + 1j * i[b.nonzero()][:n]
    return c.reshape(*arg)

def crandn(*arg):
    return norm_mv(randn(*arg) + 1j * randn(*arg))[0]
