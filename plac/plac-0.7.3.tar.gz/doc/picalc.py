from random import random
import plac

def calc_pi(npoints):
    counts = 0
    for j in xrange(npoints):
        n, r = divmod(j, 1000000)
        if r == 0:
            yield '%dM iterations' % n
        x, y = random(), random()
        if x*x + y*y < 1:
            counts += 1
    yield (4.0 * counts)/npoints

if __name__ == '__main__':
    N = 1000000
    total = 0
    for task in plac.runp([calc_pi(N), calc_pi(N)]):
        total += task.result
    print total/2
