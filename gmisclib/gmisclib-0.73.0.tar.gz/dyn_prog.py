"""Viterbi search"""

import numpy




def path(nodecost, linkcost):
	# nodecost[t,j]  at time t, pitch=j
	# linkcosts[j1, j2]   cost to go from (t,j1) to (t+1,j2)
	#    where j=pitch

	T = nodecost.shape[0]
	N = nodecost.shape[1]



	cost = numpy.zeros((N,))

	bestpathto = []
	for j in range(N):
		bestpathto.append([j])
		cost[j] = nodecost[0,j]

	for t in range(1,T):
		nbp = []
		ncost = numpy.zeros((N,))
		for j in range(N):
			cc = cost + linkcost[:,j]
			assert len(cc.shape)==1
			o = numpy.argmin(cc)
			ncost[j] = cc[o] + nodecost[t,j]
			nbp.append(bestpathto[o] + [j])
		bestpathto = nbp
		cost = ncost

	assert len(cost.shape)==1
	jj = numpy.argmin(cost)

	return (cost[jj], bestpathto[jj])



def test1():
	T = 10
	N = 7
	noc = numpy.zeros((T,N)) + 5
	noc[:,3] = 1
	linkc = numpy.zeros((N,N)) + 2

	c, p = path(noc, linkc)
	assert abs(c - (10*1 + 9*2)) < 0.0001
	assert p == [3]*T

def test2():
	T = 10
	N = 7
	noc = numpy.zeros((T,N)) + 5
	for i in range(T):
		noc[i,i%N] = 1
	linkc = numpy.zeros((N,N)) + 2

	c, p = path(noc, linkc)
	assert abs(c - (10*1 + 9*2)) < 0.0001
	assert p == [0,1,2,3,4,5,6,0,1,2]


def test3():
	T = 10
	N = 7
	noc = numpy.zeros((T,N)) + 1
	noc[0,0] = 0
	linkc = numpy.zeros((N,N)) + 2
	for i in range(N):
		linkc[i,(i+1)%N] = 1

	c, p = path(noc, linkc)
	assert abs(c - (0+9*1 + 9*1)) < 0.0001
	assert p == [0,1,2,3,4,5,6,0,1,2]

if __name__ == '__main__':
	test1()
	test2()
	test3()
