
import numpy as NP
import paddle

d = 10
K = 20
N = 30

def test_cost_rec():
    # prepare arguments
    U = NP.random.uniform(size=(K, N))
    D = NP.random.uniform(size=(d, K))
    X = NP.dot(D, U)
    # test is zero when exact
    rec_err = paddle.common._cost_rec(D, X, U)
    assert abs(rec_err) < 1.e-12
    # test is positive when not exact
    X += NP.random.normal(size=(d, N))
    rec_err = paddle.common._cost_rec(D, X, U)
    assert abs(rec_err) > 0

def test_cost_cod():
    # prepare arguments
    X = NP.random.uniform(size=(d, N))
    C = NP.random.uniform(size=(K, d))
    U = NP.dot(C, X)
    pars = {'eta': 1.}
    # test is zero when exact
    cod_err = paddle.common._cost_cod(C, X, U, pars)
    assert abs(cod_err) < 1.e-12
    # test is positive when not exact
    X += NP.random.normal(size=(d, N))
    cod_err = paddle.common._cost_cod(C, X, U, pars)
    assert abs(cod_err) > 0
    # test is zero when eta is zero
    pars['eta'] = 0
    cod_err = paddle.common._cost_cod(C, X, U, pars)
    assert abs(cod_err) < 1.e-12

def test_replaceAtoms():
    # prepare arguments
    U = NP.random.uniform(size=(K, N))
    D = NP.random.uniform(size=(d, K))
    X = NP.dot(D, U) + 0.1*NP.random.normal(size=(d, N))
    # if the list is empty nothing should happen
    V = paddle.common._replaceAtoms(X, U, D, [])
    assert NP.allclose(U, V)
    # choose one atom and one example
    i = NP.random.randint(K)
    j = NP.random.randint(N)
    U[:,j] = 0
    V = paddle.common._replaceAtoms(X, U, D, [i,])
    v = NP.zeros((K,))
    v[i] = 1
    assert NP.allclose(V[:,j], v)

