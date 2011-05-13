import Num
import types

class multivariate_normal:
	__doc__ = """multivariate_normal(mean, cov) or multivariate_normal(mean, cov, [m, n, ...])
          returns an array containing multivariate normally distributed random numbers
          with specified mean and covariance.

          mean must be a 1 dimensional array. cov must be a square two dimensional
          array with the same number of rows and columns as mean has elements.

          The first form returns a single 1-D array containing a multivariate
          normal.

          The second form returns an array of shape (m, n, ..., cov.shape[0]).
          In this case, output[i,j,...,:] is a 1-D array containing a multivariate
          normal."""

	def __init__(self, mean, cov):
		cov = Num.asarray(cov)
       		mean = Num.array(mean, copy=True)
       		# Check preconditions on arguments
       		if len(mean.shape) != 1:
              		raise TypeError, "mean must be 1 dimensional."
       		if (len(cov.shape) != 2) or (cov.shape[0] != cov.shape[1]):
              		raise TypeError, "cov must be 2 dimensional and square."
       		if mean.shape[0] != cov.shape[0]:
              		raise TypeError, "mean and cov must have same length."
       		u, s, self.v = Num.LA.singular_value_decomposition(cov)
		self.ss = Num.sqrt(s)
		self.mean = Num.array(mean, copy=True)	# Copy, so no one changes it
						# underneath you.


	def sample(self, shape=[]):
       		# Compute shape of output
       		if isinstance(shape, types.IntType):
			final_shape = [shape]
		else:
       			final_shape = list(shape[:])
       		final_shape.append(self.mean.shape[0])
       		# Create a matrix of independent standard normally distributed random
       		# numbers. The matrix has rows with the same length as mean and as
       		# many rows are necessary to form a matrix of shape final_shape.
       		x = Num.RA.standard_normal(Num.multiply.reduce(final_shape))
       		x.shape = (Num.multiply.reduce(final_shape[0:-1]), final_shape[-1])
       		# Transform matrix of standard normals into matrix where each row
       		# contains multivariate normals with the desired covariance.
       		# Compute A such that matrixmultiply(transpose(A),A) == cov.
       		# Then the matrix products of the rows of x and A has the desired
       		# covariance. Note that sqrt(s)*v where (u,s,v) is the singular value
       		# decomposition of cov is such an A.
       		x = Num.matrixmultiply(x*self.ss, self.v)
       		# The rows of x now have the correct covariance but mean 0. Add
       		# mean to each row. Then each row will have mean mean.
       		Num.add(self.mean, x, x)
       		x.shape = final_shape
       		return x

def test():
	import sys
	N = 30000
	cov = Num.array([[1, 0.1, -0.2], [0.1, 1.1, 0.2], [-0.2, 0.2, 2.0]])
	x = multivariate_normal(Num.zeros((3,), Num.Float),
				cov)
	s = Num.zeros((3,3), Num.Float)
	for i in range(N):
		z = x.sample()
		if i%300 == 0:
			sys.stdout.writelines('.')
		s += Num.outerproduct(z, z)
	print
	print cov
	print s/N

if __name__ == '__main__':
	test()
