from pymorphous import *

f1 = Field({'a':1, 'b':2, 'c':None})
f2 = Field({'a':-1, 'b':-2, 'c':None})
f3 = Field({'a':0, 'b':0, 'c':0})
s1 = -1
s2 = 1
print f1+f2
print s1*f1
#print f1*s1
#print s1*(f1+s2)
#print f3+f2+s1*(f1+s2)