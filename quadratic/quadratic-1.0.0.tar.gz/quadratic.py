# This program evaluates the values of a quadratic function.

print ("y = ax^2 + bx + c")

a = eval(input("What is a?: "))
b = eval(input("What is b?: "))
c = eval(input("What is c?: "))

def ans():
	print("y intercept => (0, %.2f)" % (c))
	x = -b / (2*a)
	y = a*x**2 + b*x + c
	print ("vertex => (%.2f, %.2f)" % (x,y))
	x1 = x + 2
	y1 = a*x1**2 + b*x1 + c
	x2 = x - 2
	y2 = a*x2**2 + b*x2 + c
	print ("extra points => (%.2f, %.2f); (%.2f, %.2f)" % (x1,y1,x2,y2))

d = b**2 - 4*a*c    # discriminant

if d < 0:
	print ("no solution!!")

elif d == 0:
	x = -b / (2*a)
	print ("x intercept => (%.2f, 0)" % (x))
	ans()
    
else: 
	from math import sqrt    
	x = [(-b + sqrt(b**2 - 4*a*c)) / (2*a), (-b - sqrt(b**2 - 4*a*c)) / (2*a)]
	print("x intercepts => (%.2f, 0); (%.2f, 0)" % (x[0],x[1]))
	ans()
