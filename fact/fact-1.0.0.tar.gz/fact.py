'''Calculates factorial of an integer n
        Only works for positive integers'''
def fact(n):
	if n==1:
		return n
	else:
		return n*fact(n-1)

	
