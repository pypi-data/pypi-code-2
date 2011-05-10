from numpy import *
from time import time

# drawn from http://www.it.lut.fi/ip/evo/functions/node1.html

# 1
class sphere(object):
   name='sphere'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      return -(x ** 2).sum()

# 2
class ellipsoid(object):
   name='ellipsoid'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      return -((x ** 2) * array([(i + 1) for i in xrange(len(x))])).sum()

# 3
class rotatedEllipsoid(object):
   name='rotatedEllipsoid'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      return -array([(x[:i].sum()) ** 2 for i in xrange(len(x))]).sum()

# 4
class rosenbrock(object):
   name='rosenbrock'
   optima = (0, 1)
   center = 0
   scale = 5.12
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      return -(100 * (((x[:-1]**2) - x[1:])**2) + ((1 - x[:-1]) ** 2)).sum()

# 5
class rastrigin(object):
   name='rastrigin'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      return -(10 * len(x) + ((x ** 2) - 10 * cos(2 * pi * x)).sum())

# 5.1
class rotatedRastrigin(object):
   name='rotatedRastrigin'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   def __init__(self, rotation):
      self.rotation = rotation
      
   def __call__(self, x):
      y = dot(self.rotation, x)
      return -(10 * len(y) + ((y ** 2) - 10 * cos(2 * pi * y)).sum())

# 5.2
class miscaledRastrigin(object):
   name='miscaledRastrigin'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   def __init__(self):
      pass
      
   def __call__(self, x):
      exponent = array([ i / (len(x) - 1) for i in xrange(len(x))])
      y = x * (10 ** exponent)
      return -(10 * len(y) + ((y ** 2) - 10 * cos(2 * pi * y)).sum())

# 5.3
class rotatedMiscaledRastrigin(object):
   name='rotatedMiscaledRastrigin'
   optima = (0, 0)
   center = 0
   scale = 5.12
   
   def __init__(self, rotation):
      self.rotation = rotation
      
   def __call__(self, x):
      z = dot(self.rotation, x)
      exponent = array([ i / (len(z) - 1) for i in xrange(len(z))])
      y = z * (10 ** exponent)
      return -(10 * len(y) + ((y ** 2) - 10 * cos(2 * pi * y)).sum())


# 6
class schwefel(object):
   name='schwefel'
   optima = (-418.982887272433799807913601398, 420.968746)
   constraints = (-512, 512)
   center = 0
   scale = 512
   
   
   def __init__(self):
      pass

   def __call__(self, x):
      return -(-x * sin(sqrt(abs(x)))).sum() / len(x)


# 6.1
class rotatedSchwefel(object):
   name = 'rotatedSchwefel'
   center = 0
   scale = 512
   
   
   @property
   def optima(self):
      return  (-418.982887272433799807913601398, dot(self.rotation, 420.968746))
   
   constraints = (-512, 512)
   
   def __init__(self, rotation):
      self.rotation = rotation

   def __call__(self, x):
      y = dot(self.rotation, x)
      return -(-y * sin(sqrt(y))).sum() / len(y)

# 7 
class salomon(object):
   name = 'salomon'
   optima = (0, 0)
   center = 0
   scale = 30

   def __init__(self):
      pass
      
   def __call__(self, x):
      dist = sqrt((x ** 2).sum())
      return -(-cos(2*pi*dist) + .1 * dist + 1)

# 8
class whitley(object):
   name = 'whitley'
   optima = (0, 1)
   bounds = (-1.0,2.0)
   center = 0
   scale = 5.12

   def __init__(self):
      pass
      
   def __call__(self, x):
      i = outer(x, ones(len(x)))
      j = outer(ones(len(x)), x)
      z = 100 * (((i ** 2) - j) ** 2) + ((1 - j) ** 2)
      return -((z ** 2)/4000 - cos(z) + 1).sum()

# 9
class ackley(object):
   name = 'ackley'
   bounds = (-30,30)
   center = 0
   scale = 30
 
   optima = {
      2: (-4.59010163415866756508876278531, [array([1.5096201, -0.7548651]), array([-1.5096201, -0.7548651])]),
      5: (-13.37957500565419, [array([1.5157285, -1.1151432, -1.1096511, -1.1038473, -0.7471183]), array([-1.5157285, -1.1151432, -1.1096511, -1.1038473, -0.7471183])])
   }

   def __init__(self):
      pass
      
   def __call__(self, x):
      return -(exp(-.2) * sqrt((x[:-1]**2) + (x[1:]**2)) \
              + 3 * (cos(2*x[:-1]) + sin(2*x[1:]))).sum()


class ackley2(ackley):
   name = 'ackley2'
   optima = (0,0)
   
   def __call__(self, x):
      return -(-20 * exp(-.02 * sqrt((x ** 2).sum() / len(x)) ) \
       - exp(cos(2 * pi * x).sum() / len(x)) + 20 + e)

# 10
class langerman(object):
   name = 'langerman'
   center = 5
   scale = 10
   A = array(
      [
         [9.681, 0.667, 4.783, 9.095, 3.517, 9.325, 6.544, 0.211, 5.122, 2.020],
         [9.400, 2.041, 3.788, 7.931, 2.882, 2.672, 3.568, 1.284, 7.033, 7.374],
         [8.025, 9.152, 5.114, 7.621, 4.564, 4.711, 2.996, 6.126, 0.734, 4.982],
         [2.196, 0.415, 5.649, 6.979, 9.510, 9.166, 6.304, 6.054, 9.377, 1.426],
         [8.074, 8.777, 3.467, 1.863, 6.708, 6.349, 4.534, 0.276, 7.633, 1.567]
      ]
   )
   
   c = array([
      0.806, 0.517, 0.100, 0.908, 0.965
   ])
   
   optima = {
      2: (-1.08093846723926811925764468469, array([9.6810707, 0.6666515])),
      5: (-0.964999919793332, array([8.07400, 8.777001, 3.467004, 1.863013, 6.707995]))
   }
   
   def __init__(self):
      pass

   def __call__(self, x):
      y = ((outer(ones(5), x) - self.A[:5,:len(x)]) ** 2).sum(axis=1)
      return (self.c * exp(-y / pi) * cos(pi * y)).sum()
      

# 11
class shekelsFoxholes(object):
   name = 'shekelsFoxholes'
   bounds = (-15,15)
   center = 5
   scale = 10
   A = array(
      [
         [9.681, 0.667, 4.783, 9.095, 3.517, 9.325, 6.544, 0.211, 5.122, 2.020],
         [9.400, 2.041, 3.788, 7.931, 2.882, 2.672, 3.568, 1.284, 7.033, 7.374],
         [8.025, 9.152, 5.114, 7.621, 4.564, 4.711, 2.996, 6.126, 0.734, 4.982],
         [2.196, 0.415, 5.649, 6.979, 9.510, 9.166, 6.304, 6.054, 9.377, 1.426],
         [8.074, 8.777, 3.467, 1.863, 6.708, 6.349, 4.534, 0.276, 7.633, 1.567],
         [7.650, 5.658, 0.720, 2.764, 3.278, 5.283, 7.474, 6.274, 1.409, 8.208],
         [1.256, 3.605, 8.623, 6.905, 4.584, 8.133, 6.071, 6.888, 4.187, 5.448],
         [8.314, 2.261, 4.224, 1.781, 4.124, 0.932, 8.129, 8.658, 1.208, 5.762],
         [0.226, 8.858, 1.420, 0.945, 1.622, 4.698, 6.228, 9.096, 0.972, 7.637],
         [7.305, 2.228, 1.242, 5.928, 9.133, 1.826, 4.060, 5.204, 8.713, 8.247],
         [0.652, 7.027, 0.508, 4.876, 8.807, 4.632, 5.808, 6.937, 3.291, 7.016],
         [2.699, 3.516, 5.874, 4.119, 4.461, 7.496, 8.817, 0.690, 6.593, 9.789],
         [8.327, 3.897, 2.017, 9.570, 9.825, 1.150, 1.395, 3.885, 6.354, 0.109],
         [2.132, 7.006, 7.136, 2.641, 1.882, 5.943, 7.273, 7.691, 2.880, 0.564],
         [4.707, 5.579, 4.080, 0.581, 9.698, 8.542, 8.077, 8.515, 9.231, 4.670],
         [8.304, 7.559, 8.567, 0.322, 7.128, 8.392, 1.472, 8.524, 2.277, 7.826],
         [8.632, 4.409, 4.832, 5.768, 7.050, 6.715, 1.711, 4.323, 4.405, 4.591],
         [4.887, 9.112, 0.170, 8.967, 9.693, 9.867, 7.508, 7.770, 8.382, 6.740],
         [2.440, 6.686, 4.299, 1.007, 7.008, 1.427, 9.398, 8.480, 9.950, 1.675],
         [6.306, 8.583, 6.084, 1.138, 4.350, 3.134, 7.853, 6.061, 7.457, 2.258],
         [0.652, 2.343, 1.370, 0.821, 1.310, 1.063, 0.689, 8.819, 8.833, 9.070],
         [5.558, 1.272, 5.756, 9.857, 2.279, 2.764, 1.284, 1.677, 1.244, 1.234],
         [3.352, 7.549, 9.817, 9.437, 8.687, 4.167, 2.570, 6.540, 0.228, 0.027],
         [8.798, 0.880, 2.370, 0.168, 1.701, 3.680, 1.231, 2.390, 2.499, 0.064],
         [1.460, 8.057, 1.336, 7.217, 7.914, 3.615, 9.981, 9.198, 5.292, 1.224],
         [0.432, 8.645, 8.774, 0.249, 8.081, 7.461, 4.416, 0.652, 4.002, 4.644],
         [0.679, 2.800, 5.523, 3.049, 2.968, 7.225, 6.730, 4.199, 9.614, 9.229],
         [4.263, 1.074, 7.286, 5.599, 8.291, 5.200, 9.214, 8.272, 4.398, 4.506],
         [9.496, 4.830, 3.150, 8.270, 5.079, 1.231, 5.731, 9.494, 1.883, 9.732],
         [4.138, 2.562, 2.532, 9.661, 5.611, 5.500, 6.886, 2.341, 9.699, 6.500]
      ]
   )
   
   c = array([
      0.806, 0.517, 0.100, 0.908, 0.965, 0.669, 0.524, 0.902, 0.531, 0.876, 0.462,
      0.491, 0.463, 0.714, 0.352, 0.869, 0.813, 0.811, 0.828, 0.964, 0.789, 0.360,
      0.369, 0.992, 0.332, 0.817, 0.632, 0.883, 0.608, 0.326
   ])
   
   optima = {
      2: (-12.1190083797535965715042038937, array([8.0240653, 9.1465340])),
      5: (-10.40561723899245, array([8.02491489, 9.15172576, 5.11392781, 7.62086096, 4.56408839])),
      10: (-10.2088, array((8.025, 9.152, 5.114, 7.621, 4.564, 4.771, 2.996, 6.126, 0.734, 4.982)))
   }
   
   def __init__(self):
      pass
   
   def __call__(self, x):
      dim = len(x)
      s = ((outer(ones(30), x) - self.A[:30,:dim]) ** 2).sum(axis=1)
      s = s + self.c
      return (1. / s).sum()

class shekel2(shekelsFoxholes):
   name = 'shekel2'
   bounds = (-5,15)
   center = 5
   scale = 10
      
# 12
class rana(object):
   name = 'rana'
   optima = (-512.753162426239100568636786193, -514.041683)
   center = 0
   scale = 520

   def __init__(self):
      pass
      
   def __call__(self, x):
      z = append(x[1:], x[:1], axis=0)
      ym = sqrt(abs(z + 1 - x))
      yp = sqrt(abs(z + 1 + x))
      return -(x * sin(ym) * cos(yp) + (z + 1) * cos(ym) * sin(yp)).sum() / len(x)


class griewank(object):
   name = "griewank"
   optima = (0, 0)
   bounds = (-600, 600)
   center = 0
   scale = 600
   
   
   def __init__(self):
      pass

   def __call__(self, x):
      y = x
      i = array([i+1 for i in xrange(len(x))])
      return -(1. + (y**2).sum()/4000. - (cos(y / sqrt(i))).prod())

class weierstrass(object):
   name = "weierstrass"
   optima = (0,0)
   center = 0
   scale = 0.5

   def __call__(self, x):
      xk = outer(ones(20), x)
      k = array([i for i in xrange(20)])
      ak = .5 ** k
      bk = 3 ** k
      c = outer(ak, ones(len(x))) * cos(2 * pi * outer(bk, ones(len(x))) * (xk + .5))
      d = ak * cos(pi * bk)
      return (c.sum() + len(x) * d.sum())


class randomrbm(object):
   center = 0.5
   scale = 0.5
   dim = 50
   
   def __init__(self):
      dim = self.dim
      self.w = random.standard_cauchy((dim, dim)) / dim / dim
      self.bv = random.standard_cauchy(dim) / dim / dim
      self.bh = random.standard_cauchy(dim) / dim / dim
   
   def energy(self, x, useAlternate=False):
      return -self(x)   
            
   def __call__(self, x):
      v = x[:self.dim].toArray(self.dim)
      h = x[self.dim:(2 * self.dim)].toArray(self.dim)
      ret = (dot(v, dot(self.w, h)) + dot(v, self.bv) + dot(h, self.bh))
      return ret
   
   def partition(self):
      from pyec.distribution.basic import BernoulliTernary
      uniform = BernoulliTernary(self)
      sample = uniform.batch(100000)
      base = array([exp(-self.energy(x)) for x in sample]) 
      return (base / 100000.).sum() * (2.0 ** (self.dim * 2))
      
      """
      from pyec.util.TernaryString import TernaryString
      total = 0
      all = (1L << self.dim) - 1L
      for i in xrange(1 << (2 * self.dim)):
         total += exp(self.__call__(TernaryString(long(i), all)))
      return total
      """
      
   def scoreSample(self, sample, Z=1.0):
      return [(x, exp(-self.__call_(x))/Z) for x in sample]
   
   def simulatedTempering(self, size):
      from pyec.distribution.boltzmann.sample import RBMSimulatedTempering
      sampler = RBMSimulatedTempering(1000)
      return sampler(self, size)
   
   def swendsenwang(self, size):
      from pyec.util.TernaryString import TernaryString
      sample = []
      vsize = self.dim
      hsize = self.dim
      
      w = self.w
      bv = self.bv
      bh = self.bh
      
      for n in xrange(1):
         start = time()
         x = random.random_sample(vsize + hsize).round()
         last = copy(x)
         repeats = 0
         for l in xrange(1000 + size):
            startInner = time()
            clusters = {}
            for i in xrange(vsize):
               for j in xrange(hsize):
                  i2 = j + vsize
                  if (w[i,j] < 0.0 and x[i] != x[i2] and random.random_sample() < 1. - exp(2 * w[i,j])) or \
                   (w[i,j] > 0.0 and x[i] == x[i2] and random.random_sample() < 1. - exp(-2 * w[i,j])):
                  #if d[i,j] > 0.0:
                     si = [i]
                     sj = [i2]
                     if clusters.has_key(i):
                        si = clusters[i]
                     if clusters.has_key(i2):
                        sj = clusters[i2]
                     s = list(set(si + sj))
                     for k in s:
                        clusters[k] = s
            
            computed = zeros(x.size)
            for k, s in clusters.iteritems():
               if computed[k] > 0.0:
                  continue
               bias = 0.0
               for m in s:
                  if m >= vsize:
                     bias += bh[m - vsize]
                  else:
                     bias += bv[m]
               state = float(random.binomial(1, 1. / (1. + exp(-bias)), 1))
               for m in s:
                  x[m] = state
                  computed[m] = 1.0
                  
            for i in xrange(x.size):
               if computed[i] < 1.0:
                  i2 = i
                  b = bv
                  if i2 >= vsize:
                     i2 -= vsize
                     b = bh
                  x[i] = float(random.binomial(1, 1. / (1. + exp(-b[i2])), 1))
            if l >= 1000:
               sample.append(TernaryString.fromArray(x))
         #print "SW sample ", n, ": ", time() - start   
         
      return sample   
   
            
   def gibbs(self, size):
      from pyec.util.TernaryString import TernaryString
      sample = []
      for i in xrange(size):
         x = random.random_sample(2 * self.dim).round()
         for j in xrange(100):
            v = dot(self.w, x[self.dim:]) + self.bv
            x[:self.dim] = random.binomial(1, 1. / (1. + exp(-v/(100 - j))), self.dim)
            h = dot(x[self.dim:], self.w) + self.bh
            x[self.dim:] = random.binomial(1, 1. / (1. + exp(-h/(100 - j))), self.dim)
         sample.append(TernaryString.fromArray(x))
      return sample
      
   def bucket(self, sample, Z=1.0):
      d = {}
      size = len(sample)
      incr = 1.0 / size
      for x in sample:
         y = str(x)
         if d.has_key(y):
            d[y][0] += incr
         else:
            d[y] = [incr, exp(-self.__call__(x))/Z]
      return d
      
      
class data_extender(object):
   def __init__(self, data, vsize, hsize):
      self.data = data
      self.vsize = vsize
      self.hsize = hsize
      

   def batch(self, size):
      sample = []
      while len(sample) < size:
        sample.extend([append(d, random.random_sample(self.hsize).round(), axis=0) for d in self.data])
      return sample[:size]
                  
class randomrbmdata(object):
   center = 0
   scale = 0
   vsize = 50
   hsize = 200
   numdata = 1000

   def __init__(self):
      from pyec.distribution.boltzmann.rbm import rbm
      self.base = randomrbm()
      self.model = rbm(self.vsize,self.hsize)
      self.model.data = [x.toArray(self.vsize + self.hsize)[:self.vsize] for x in self.base.gibbs(self.numdata)]# random.random_sample((self.numdata, self.vsize)).round()
      
   def __call__(self, x):
      return -self.model.energy(x)
   
   def train(self, sampler):
      self.model.sampler = self.algorithm
      return self.model.train()  
      
   def gibbs(self, size):
      self.model.gibbs(size)
   
   @property
   def initial(self):
      return data_extender(self.model.data, self.vsize, self.hsize)

allBenchmarks = [sphere(), ellipsoid(), rotatedEllipsoid(), rosenbrock(), rastrigin(), miscaledRastrigin(), schwefel(), salomon(), whitley(), ackley(), langerman(), shekelsFoxholes(), rana(), shekel2(), ackley2(), griewank(), weierstrass()]      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
