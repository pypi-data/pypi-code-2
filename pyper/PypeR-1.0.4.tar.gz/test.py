#!/usr/bin/env python

from pyper import *

if __name__ == '__main__':
	myR = R()
	a = range(5)

	# test simple command
	myR.run('a <- 3')
	myR('print(a)')

	# test parameter conversion
	myR('b <- %s' % Str4R(a))

	# set variable in R
	myR.assign('b', a)
	#    or 
	myR['b'] = a
	#	or
	myR.b = a

	# get value from R 
	# from R variables
	b = myR['b']
	bb = myR.get('bb', 'No this variable!')
	print(b, bb, myR['pi'], myR.pi)
	# or from an R expression
	print(myR['(2*pi + 3:9)/5'])
	del myR.a, myR['b']

	# test R list
	myR['alst'] = [1, (2, 3, 'any strings'), 4+5j]
	print(myR['alst'])

	# test plotting
	myR('png("abc.png"); plot(1:5); dev.off()')

	if has_numpy:
		arange, array, reshape = numpy.arange, numpy.array, numpy.reshape
		# numpy arrays
		# one-dimenstion numpy array will be converted to R vector
		myR['avec'] = arange(5)
		print(myR['avec'])
		# one-dimenstion numpy record array will be converted to R data.framme
		myR['adfm'] = array([(1, 'Joe', 35820.0), (2, 'Jane', 41235.0), (3, 'Kate', 37932.0)], \
				dtype=[('id', '<i4'), ('employee', '|S4'), ('salary', '<f4')])
		print(myR['adfm'])
		# two-dimenstion numpy array will be converted to R matrix
		myR['amat'] = reshape(arange(12), (3, 4)) # a 3-row, 4-column matrix
		print(myR['amat'])
		# numpy array of three or higher dimensions will be converted to R array
		myR['aary'] = reshape(arange(24), (2, 3, 4)) # a 3-row, 4-column, 2-layer array 
		print(myR['aary'])

	# test huge data sets and the function runR
	a = range(10000) #00)
	sa = 'a <- ' + Str4R(a)
	rlt = runR(sa)

	# to use an R on remote server, you need to provide correct parameter to initialize the R instance:
	# rsrv = R(RCMD='/usr/local/bin/R', host='My_server_name_or_IP', user='username')


