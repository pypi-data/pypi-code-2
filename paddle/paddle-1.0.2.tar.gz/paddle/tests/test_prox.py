
import scipy as sp
import paddle

d = 10
K = 20
N = 30

def test_st():
    # prepare arguments
    X = sp.random.uniform(low=-1, high=1, size=(d, N))
    # for mu=0 should be the same
    Y = paddle.prox._st(X, 0)
    assert sp.allclose(Y, X)
    # for mu=inf should be all zero
    Y = paddle.prox._st(X, sp.inf)
    assert sp.allclose(Y, 0)
    # check for 0<mu<inf
    mu = sp.absolute(X).mean()
    Y = paddle.prox._st(X, mu)
    # check the sign
    assert sp.allclose(sp.sign(sp.where(Y == 0, 0, X)), sp.sign(Y))
    # check the extremes
    assert Y.max() == X.max() - mu
    assert Y.min() == X.min() + mu

