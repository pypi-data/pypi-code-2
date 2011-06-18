# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 12:07:21 2011

@author: Sat Kumar Tomer
@website: www.ambhas.com
@email: satkumartomer@gmail.com

This is a test script for the copulalib

"""


# import required library
import sys
import numpy as np
import matplotlib.pyplot as plt


# add the path to copulalib
sys.path.insert(0, '..')

# import copulalib
from copulalib.copulalib import Copula


# generate random (normal distributed) numbers
x = np.random.normal(size=100)
y = 2.5*x+ np.random.normal(size=100)

plt.subplot(221)
plt.scatter(x, y)
plt.grid(True)
plt.title('Data')

# make the instance of Copula class with x, y and clayton family
foo_clayton = Copula(x, y, family='clayton')
foo_frank = Copula(x, y, family='frank')
foo_gumbel = Copula(x, y, family='gumbel')

# print the Kendall's rank correlation
print foo_gumbel.tau 

# print spearmen's correlation
print foo_gumbel.sr

# print pearson's correlation
print foo_gumbel.pr

# print the parameter (theta) of copula
print foo_clayton.theta
print foo_frank.theta
print foo_gumbel.theta

# generate the 1000 samples (U,V) of copula
X1, Y1 = foo_clayton.generate_xy(1000)
X2, Y2 = foo_frank.generate_xy(1000)
X3, Y3 = foo_gumbel.generate_xy(1000)

plt.subplot(222)
plt.scatter(X1, Y1)
plt.grid(True)
plt.title('Clayton')

plt.subplot(223)
plt.scatter(X2, Y2)
plt.grid(True)
plt.title('Frank')

plt.subplot(224)
plt.scatter(X3, Y3)
plt.grid(True)
plt.title('Gumbel')

plt.show()





#count = 0
#u = UniversalDetector()
#for f in glob.glob(sys.argv[1]):
#    print(f.ljust(60), end=' ')
#    u.reset()
#    for line in open(f, 'rb'):
#        u.feed(line)
#        if u.done: break
#    u.close()
#    result = u.result
#    if result['encoding']:
#        print(result['encoding'], 'with confidence', result['confidence'])
#    else:
#        print('******** no result')
#    count += 1
#print(count, 'tests')