from numpy import *
from scipy.special import gammaln

class KullbackLeiblerDivergence(object):
   def __init__(self, k):
      self.k = k
   
   def numStepsToDiff(self, k, x, xs, dim):
      diffs = abs(x - xs).sum(axis=1)
      cnt = 0
      for d in diffs: 
         if d < k: cnt += 1
      return cnt
      """
      cnt = 0
      for y in xs:
         d = x.distance(y, dim)
         if d < k:
            cnt += 1
      return cnt
      """
   
   def distance(self, x, y):
      return sqrt(((x - y) ** 2).sum())
   
   def nearestNeighbor(self, k, x, xs):
      d = sqrt(((xs - x)**2).sum(axis=1))
      j = k - 1
      ks = []
      for i, y in enumerate(xs):
         if len(ks) == 0:
            ks.append((y, d[i]))
         elif j >= len(ks) or d[i] < ks[j][1]:
            m = 0
            while m < len(ks) and ks[m][1] < d[i]:
               m += 1
            if m >= len(ks):
               ks.append((y, d[i]))
            else:
               ks.insert(m, (y,d[i]))
            ks = ks[:k]
      
      return ks[j]

         
   
   def compute(self, p, q, xs):
      return array([p(x) * log(p(x) / q(x)) for x in xs]).sum()
    
   def approximateOneBits(self, xs, q, dim):
      """ 
         Estimate for KL div. in binary space
         
         
         xs is a sample from p (Ternary strings
         q is density
         
         return approximation to p || q
      """
      k = int(dim * .1) or 1
      total = 0.0
      stored = {}
      rank = 2 ** array([i+1 for i in xrange(dim)])
      for i,x in enumerate(xs):
         key = str(float((x * rank).sum()))
         if not stored.has_key(key):
            neighbors = self.numStepsToDiff(k, x, xs, dim)
            stored[key] = neighbors
         else:
            neighbors = stored[key]
         print "one ", i, total / (i+1.), neighbors, log(neighbors), log(q(x))
         total += log(neighbors) - log(q(x))
      total /= len(xs)
      div = sum([s for key, s in stored.iteritems()]) + 0.
      print "divisor: ", div, log(div), total
      
      return total - log(div) 
    
   def approximateOne(self, xs, q, cutoff=.1):
      """ 
         Based on F Perez Cruz 2008 
         "Kullback-Leibler Divergence Estimation for Continuous Distributions" 
         
         
         xs is a sample from p
         q is density
         
         return approximation to p || q
      """
      k = len(xs) / 500
      d = len(xs[0])
      c = gammaln(d *.5 + 1) - (d * .5) * log(pi) + log(k / (len(xs) - 1.))
      c /= len(xs)
      total = 0.0
      for i,x in enumerate(xs):
         print "one ", i, c, total / (i+1.)
         y, dist = self.nearestNeighbor(k+1, x, xs)
         total += d * log(dist) - log(q(x))
         if (i+0.) / len(xs) > cutoff:
            total /= cutoff
            break
      total /= len(xs)
      return c + total

   def approximate(self, ps, qs, cutoff = .1):
      """ 
         Based on F Perez Cruz 2008 
         "Kullback-Leibler Divergence Estimation for Continuous Distributions" 
         
         
         ps is a sample from p
         qs is a sample from q
         
         return approximation to p || q
      """
      k = self.k
      d = len(ps[0])
      c = log(len(qs) / (len(ps) - 1.))
      total = 0.0
      for i, x in enumerate(ps):
         print "two ", i
         y, dist = self.nearestNeighbor(k+1, x, ps)
         z, dist2 = self.nearestNeighbor(k, x, qs)
         total += log(dist / dist2)
         if (i+0.) / len(xs) > cutoff:
            total /= cutoff
            break
      total *= ((d + 0.) / len(ps))
      return c + total