import scipy as sp
import openTMM as tmm
import os

basePath = tmm.__path__[0]
curPath = os.path.abspath(os.curdir)

inFile = os.path.join(basePath, "tests", "cpcInput.txt")
outFileSVN = os.path.join(basePath, "tests", "cpcOutputSVN.txt")
outFile = os.path.join(curPath, "cpcOutput.txt")

# input data
inData = sp.loadtxt(inFile, delimiter=',', skiprows=1)

# Make Layer obj from inData
mm = 1.0 * 10**-3
GHz = 1.0 * 10**9
fo = inData[0,3] * GHz
phi = inData[0,4]
xSample = int(inData[0,5])
stackDict = {}
stackDict['epsilonRelative'] = inData[:,0]
stackDict['muRelative'] = inData[:,1]
stackDict['height'] = inData[:,2] * mm
stack = tmm.Layer(stackDict)

out = open(outFile, 'w')

# perp polarization
x, u_e, u_m = stack.energy(fo, phi, xSample, pol='perp')
out.write('Perpendicular polarization:\n')
out.write('u_e(x) = \n')
for i in range(u_e.size):
    s = "%*.*E  " % (1, 6, float(u_e[i]))
    out.write(s)

out.write('\n')
out.write('u_m(x) = \n')

for i in range(u_m.size):
    s = "%*.*E  " % (1, 6, float(u_m[i]))
    out.write(s)

# parallel polarization
x, u_e, u_m = stack.energy(fo, phi, xSample, pol='parallel')
out.write('\n\n')
out.write('Parallel polarization:\n')
out.write('u_e(x) = \n')

for i in range(u_e.size):
    s = "%*.*E  " % (1, 6, float(u_e[i]))
    out.write(s)

out.write('\n')
out.write('u_m(x) = \n')

for i in range(u_m.size):
    s = "%*.*E  " % (1, 6, float(u_m[i]))
    out.write(s)


out.close()
print '\n'
print 'Dear CPC Program Librarian,\n'
print 'INPUT DATA: ' + inFile
print '\nOUTPUT DATA (this run): ' + outFile
print '\nOUTPUT DATA (from SVN): ' + outFileSVN
print '\nPlease compare OUTPUT DATA (this run) with OUTPUT DATA (from SVN).'
print '\n\nThanks you, \n    Alex J. Yuffa <ayuffa@gmail.com>'


