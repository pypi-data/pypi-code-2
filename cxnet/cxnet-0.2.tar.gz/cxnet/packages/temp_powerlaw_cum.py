from pylab import *

# Define function for calculating a power law
powerlaw = lambda x, amp, index: amp * (x**index)

##########
# Generate data points with noise
##########
num_points = 20

# Note: all positive, non-zero data
xdata = linspace(1.1, 10.1, num_points)
ydata = powerlaw(xdata, 10.0, -2.0)     # simulated perfect data
yerr = 0.2 * ydata                      # simulated errors (10%)

ydata += randn(num_points) * yerr       # simulated noisy data

if True:
	y_cum = []
	sum_ = 0
	ydata.reverse()
	for y_ in ydata:
	    sum_ += y_
	    y_cum.append(sum_)
	ydata=y_cum
	ydata.reverse()



##########
# Plotting data
##########

clf()
loglog(xdata, ydata, ".")     # Fit
title('Best Fit Power Law')
xlabel('X')
ylabel('Y')
xlim(1, 11)


#savefig('power_law_fit.png')
