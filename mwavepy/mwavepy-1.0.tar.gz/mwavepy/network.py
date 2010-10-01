'''
#       network.py
#       
#       
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       Copyright 2010 lihan chen 
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later versionpy.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
'''

from copy import copy
import os

import numpy as npy
import pylab as plb 

import  mathFunctions as mf
import touchstone
from frequency import Frequency
from plotting import smith


class Network(object):
	'''
	Represents a n-port microwave network.

	the most fundemental properties are:
		s: scattering matrix. a kxnxn complex matrix where 'n' is number
			of ports of network.
		z0: characteristic impedance
		f: frequency vector in Hz. see also frequency, which is a
			Frequency object (see help on this class for more info)
		
	
	The following operators are defined as follows:
		'+' : element-wise addition of the s-matrix
		'-' : element-wise subtraction of the s-matrix
		'*' : element-wise multiplication of the s-matrix
		'/' : element-wise division of the s-matrix
		'**': cascading of two networks
		'//': de-embdeding of one network from the other.

	various other network properties are accesable as well as plotting
	routines are also defined for convenience, 
	
	most properties are derived from the specifications given for
	touchstone files. 
	'''

## CONSTRUCTOR
	def __init__(self, touchstone_file = None, name = None ):
		'''
		constructor.
		
		takes:
			file: if given will load information from touchstone file
			name: name of this network. 
		'''
		# although meaningless untill set with real values, this
		# needs this to exist for dependent properties
		self.frequency = Frequency(0,0,0)
		
		if touchstone_file is not None:
			self.read_touchstone(touchstone_file)
		else:
			self.name = name
			#self.s = None
			self.z0 = 50 
			
	

## OPERATORS
	def __pow__(self,other):
		'''
		 implements cascading this network with another network
		'''
		if self.number_of_ports == 2  and other.number_of_ports == 2:
			result = copy(self)
			result.s = cascade(self.s,other.s)
			return result
		elif self.number_of_ports == 2 and other.number_of_ports == 1:
			result = copy(other)
			result.s = cascade(self.s, other.s)
			return result
		elif self.number_of_ports == 1 and other.number_of_ports == 2:
			result = copy(other)
			# this flip is to make the termination what the syntax
			# looks like  
			result.s = cascade(flip(other.s),self.s)
			return result
		else:
			raise IndexError('Incorrect number of ports.')


	def __floordiv__(self,other):
		'''
		 implements de-embeding another network[s], from this network

		see de_embed
		'''
		try: 	
			# if they passed 1 ntwks and a tuple of ntwks, 
			# then deEmbed like A.inv*C*B.inv
			b = other[1]
			c = other[0]
			result =  copy (self)
			result.s =  flip(de_embed( flip(de_embed(c.s,self.s)),b.s))
			return result
		except TypeError:
			pass
				
		if self.number_of_ports == 2  and other.number_of_ports == 2:
			result = copy(self)
			result.s = de_embed(self.s,other.s)
			return result
		elif self.number_of_ports == 1 and other.number_of_ports == 2:
			result = copy(other)
			result.s = de_embed(self.s,other.s)
			return result
		else:
			raise IndexError('Incorrect number of ports.')


	def __mul__(self,a):
		'''
		element-wise complex multiplication  of s-matrix
		'''
		result = copy(self)
		result.s = result.s * a.s
		return result


	def __add__(self,other):
		'''
		element-wise addition of s-matrix
		'''
		result = copy(self)
		result.s = result.s + other.s
		return result
		

	def __sub__(self,other):
		'''
		element-wise subtraction of s-matrix
		'''
		result = copy(self)
		result.s = result.s - other.s
		return result


	def __div__(self,other):
		'''
		element-wise complex division  of s-matrix
		'''
		if other.number_of_ports != self.number_of_ports:
			raise IndexError('Networks must have same number of ports.')
		else:
			result = copy(self)
			try:
				result.name = self.name+'/'+other.name
			except TypeError:
				pass
			result.s =(self.s/ other.s)
			
			return result


## PRIMARY PROPERTIES
	# s-parameter matrix
	@property
	def s(self):
		'''
		The scattering parameter matrix.
		
		s-matrix has shape fxmxn, 
		where; 
			f is frequency axis and,
			m and n are port indicies
		'''
		return self._s
	
	@s.setter
	def s(self, s):
		'''
		the input s-matrix should be of shape fxmxn, 
		where f is frequency axis and m and n are port indicies
		'''
		if len(s.shape) == 1:
			# reshape to kxmxn, this simplifies indexing in function
			s = s.reshape(-1,1,1)
		self._s = s
		#s.squeeze()
	@property
	def y(self):
		if self.number_of_ports == 1:
			return (1-self.s)/(1+self.s)
		else:
			raise(NotImplementedError)
	
	# t-parameters
	@property
	def t(self):
		'''
		returns the t-parameters, which are also known as wave cascading
		matrix. 
		'''
		return s2t(self.s)
		
	# frequency information
	@property
	def frequency(self):
		'''
		returns a Frequency object, see  frequency.py
		'''
		return self._frequency

	@frequency.setter
	def frequency(self, new_frequency):
		'''
		takes a Frequency object, see  frequency.py
		'''
		self._frequency= copy(new_frequency)

	
	@property
	def f(self):
		''' the frequency vector for the network, in Hz. '''
		return self._frequency.f
		
	@f.setter
	def f(self,f):
		tmpUnit = self.frequency.unit
		self._frequency  = Frequency(f[0],f[-1],len(f),'hz')
		self._frequency.unit = tmpUnit
	

	
	# characteristic impedance
	@property
	def z0(self):
		''' the characteristic impedance of the network.'''
		return self._z0
	
	@z0.setter
	def z0(self, z0):
		self._z0 = z0
	
## SECONDARY PROPERTIES

	# s-parameters convinience properties	
	@property
	def s_mag(self):
		'''
		returns the magnitude of the s-parameters.
		'''
		return mf.complex_2_magnitude(self.s)
	
	@property
	def s_db(self):
		'''
		returns the magnitude of the s-parameters, in dB
		
		note:
			dB is calculated by 
				20*log10(|s|)
		'''
		return mf.complex_2_db(self.s)
		
	@property
	def s_deg(self):
		'''
		returns the phase of the s-parameters, in radians
		'''
		return mf.complex_2_degree(self.s)
		
	@property
	def s_rad(self):
		'''
		returns the phase of the s-parameters, in radians.
		'''
		return mf.complex_2_radian(self.s)
	
	@property
	def s_deg_unwrap(self):
		'''
		returns the unwrapped phase of the s-paramerts, in degrees
		'''
		return mf.radian_2_degree(self.s_rad_unwrap)
	
	@property
	def s_rad_unwrap(self):
		'''
		returns the unwrapped phase of the s-parameters, in radians.
		'''
		return npy.unwrap(mf.complex_2_radian(self.s),axis=0)

	@property
	def number_of_ports(self):
		'''
		the number of ports the network has.
		'''
		return self.s.shape[1]
	# frequency formating related properties
	
	
## CLASS METHODS
	# touchstone file IO
	def read_touchstone(self, filename):
		'''
		loads  values from a touchstone file. 
		
		takes:
			filename - touchstone file name, string. 
		
		note: 
			ONLY 'S' FORMAT SUPORTED AT THE MOMENT 
			all work is tone in the touchstone class. 
		'''
		touchstoneFile = touchstone.touchstone(filename)
		
		if touchstoneFile.get_format().split()[1] != 's':
			raise NotImplementedError('only s-parameters supported for now.')
		
		self.z0 = float(touchstoneFile.resistance)
		self.f, self.s = touchstoneFile.get_sparameter_arrays() # note: freq in Hz
		self.frequency.unit = touchstoneFile.frequency_unit # for formatting plots
		self.name = touchstoneFile.filename.split('/')[-1].split('.')[-2]

	def write_touchstone(self, filename=None,dir ='./'):
		'''
		write a touchstone file representing this network.  the only 
		format supported at the moment is :
			HZ S RI 
		
		takes: 
			filename - filename (not including extension)
			
		
		note:
			in the future could make possible use of the touchtone 
			class, but at the moment this would not provide any benefit 
			as it has not set_ functions. 
		'''

		
		if filename is None and self.name is not None:
			filename= self.name

		filename= dir+filename + '.s'+str(self.number_of_ports)+'p'
		outputFile = open(filename,"w")
		
		# write header file. 
		# the '#'  line is NOT a comment it is essential and it must be 
		#exactly this format, to work
		# [HZ/KHZ/MHZ/GHZ] [S/Y/Z/G/H] [MA/DB/RI] [R n]
		outputFile.write('# ' + self.frequency.unit + ' S RI R ' + str(self.z0) +" \n")
		
		#write comment line for users (optional)
		outputFile.write ("!freq\t")
		for n in range(self.number_of_ports):
			for m in range(self.number_of_ports):
				outputFile.write("Re" +'S'+`m+1`+ `n+1`+  "\tIm"+\
				'S'+`m+1`+ `n+1`+'\t')
		outputFile.write('\n')		
		
		# write out data, note: this could be done with matrix 
		#manipulations, but its more readable to me this way
		for f in range(len(self.f)):
			outputFile.write(str(self.frequency.f_scaled[f])+'\t')
			
			for n in range(self.number_of_ports):
				for m in range(self.number_of_ports):
					outputFile.write( str(npy.real(self.s[f,m,n])) + '\t'\
					 + str(npy.imag(self.s[f,m,n])) +'\t')
			
			outputFile.write('\n')
		
		outputFile.close()


	# self-modifications
	def interpolate(self):
		raise NotImplementedError


	def flip(self):
		'''
		swaps the ports of a two port 
		'''
		if self.number_of_ports == 2:
			self.s = flip(self.s)
		else:
			raise ValueError('you can only flip two-port Networks')


	# ploting

	def plot_vs_frequency_generic(self,attribute,y_label=None,\
		m=0,n=0, ax=None,show_legend=True,**kwargs):
		'''
		generic plotting function for plotting a Network's attribute
		vs frequency.
		

		takes:

		
		'''

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca()
			
		# set the legend label for this trace to the networks name if it
		# exists, and they didnt pass a name key in the kwargs
		if 'label'  not in kwargs.keys(): 
			if self.name is None:
				if plb.rcParams['text.usetex']:
					label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
				else:
					label_string = 'S'+repr(m+1) + repr(n+1)
			else:
				if plb.rcParams['text.usetex']:
					label_string = self.name+', $S_{'+repr(m+1) + \
						repr(n+1)+'}$'
				else:
					label_string = self.name+', S'+repr(m+1) + repr(n+1)

			kwargs['label'] = label_string
			
		# plot the desired attribute vs frequency 
		ax.plot(self.frequency.f_scaled, getattr(self, attribute)[:,m,n],\
			 **kwargs)

		# label axis
		plb.xlabel('Frequency ['+ self.frequency.unit +']')
		plb.ylabel(y_label)
		plb.axis('tight')
		#draw legend
		if show_legend:
			plb.legend()
		
	def plot_polar_generic (self,attribute_r, attribute_theta,	m=0,n=0,\
		ax=None,show_legend=True,**kwargs):
		'''
		generic plotting function for plotting a Network's attribute
		in polar form
		

		takes:
			
		
		'''

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca(polar=True)
			
		# set the legend label for this trace to the networks name if it
		# exists, and they didnt pass a name key in the kwargs
		if 'label'  not in kwargs.keys(): 
			if self.name is None:
				if plb.rcParams['text.usetex']:
					label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
				else:
					label_string = 'S'+repr(m+1) + repr(n+1)
			else:
				if plb.rcParams['text.usetex']:
					label_string = self.name+', $S_{'+repr(m+1) + \
						repr(n+1)+'}$'
				else:
					label_string = self.name+', S'+repr(m+1) + repr(n+1)

			kwargs['label'] = label_string
			
		#TODO: fix this to call from ax, if possible
		plb.polar(getattr(self, attribute_r)[:,m,n],\
			getattr(self, attribute_theta)[:,m,n],**kwargs)

		#draw legend
		if show_legend:
			plb.legend()	
		
	def plot_s_db(self,m=0, n=0, ax = None, show_legend=True,**kwargs):
		'''
		plots the magnitude of the scattering parameter of indecies m, n
		in log magnitude
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_db',\
			y_label='Magnitude [dB]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)

	def plot_s_mag(self,m=0, n=0, ax = None, show_legend=True,**kwargs):
		'''
		plots the magnitude of a scattering parameter of indecies m, n
		not in  magnitude
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_mag',\
			y_label='Magnitude [not dB]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)

	def plot_s_deg(self,m=0, n=0, ax = None, show_legend=True,**kwargs):
		'''
		plots the phase of a scattering parameter of indecies m, n in
		degrees
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_deg',\
			y_label='Phase [deg]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)
		
				
	def plot_s_deg_unwrapped(self,m=0, n=0, ax = None, show_legend=True,\
		**kwargs):
		'''
		plots the phase of a scattering parameter of indecies m, n in
		unwrapped degrees
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_deg_unwrap',\
			y_label='Phase [deg]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)
	def plot_s_rad(self,m=0, n=0, ax = None, show_legend=True,**kwargs):
		'''
		plots the phase of a scattering parameter of indecies m, n in
		radians
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_rad',\
			y_label='Phase [rad]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)
		
				
	def plot_s_rad_unwrapped(self,m=0, n=0, ax = None, show_legend=True,\
		**kwargs):
		'''
		plots the phase of a scattering parameter of indecies m, n in
		unwrapped radians
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_vs_frequency_generic(attribute= 's_rad_unwrap',\
			y_label='Phase [rad]', m=m,n=n, ax=ax,\
			show_legend = show_legend,**kwargs)	

	def plot_s_polar(self,m=0, n=0, ax = None, show_legend=True,\
		**kwargs):
		'''
		plots the scattering parameter of indecies m, n in polar form
		
		takes:
			m - first index, int
			n - second indext, int
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to the matplotlib.plot command
		'''
		self.plot_polar_generic(attribute_r= 's_mag',attribute_theta='s_rad',\
			m=m,n=n, ax=ax,	show_legend = show_legend,**kwargs)	

	def plot_s_smith(self,m=0, n=0,r=1,ax = None, show_legend=True,**kwargs):
		'''
		plots the scattering parameter of indecies m, n on smith chart
		
		takes:
			m - first index, int
			n - second indext, int
			r -  radius of smith chart
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			**kwargs - passed to thematplotlib.plot command	
		'''
		# TODO: prevent this from re-drawing smith chart if one alread
		# exists on current set of axes

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca()
			
		# set the legend label for this trace to the networks name if it
		# exists, and they didnt pass a name key in the kwargs
		if 'label'  not in kwargs.keys(): 
			if self.name is None:
				if plb.rcParams['text.usetex']:
					label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
				else:
					label_string = 'S'+repr(m+1) + repr(n+1)
			else:
				if plb.rcParams['text.usetex']:
					label_string = self.name+', $S_{'+repr(m+1) + \
						repr(n+1)+'}$'
				else:
					label_string = self.name+', S'+repr(m+1) + repr(n+1)

			kwargs['label'] = label_string
			
		# plot the desired attribute vs frequency 
		smith(ax=ax, smithR = r)
		ax.plot(self.s[:,m,n].real,  self.s[:,m,n].imag, **kwargs)
		
		#draw legend
		if show_legend:
			plb.legend()
		ax.axis(npy.array([-1,1,-1,1])*r)



## FUNCTIONS
# functions operating on Network[s]
def average(list_of_networks):
	'''
	complex average of the s-parameters list of Networks
	'''
	out_ntwk = copy(list_of_networks[0])
	
	for a_ntwk in list_of_networks[1:]:
		out_ntwk += a_ntwk

	out_ntwk.s/(len(list_of_networks))

	return out_ntwk

def psd2_2_time_domain():
	raise NotImplementedError

# functions not operating on  Network type. 
#mostly working on  s-matricies

# network format conversions
def s2t(s):
	'''
	converts a scattering parameters to 'wave cascading parameters'
	
	input matrix shape should be should be 2x2, or kx2x2
	
	BUG: if s -matrix has ones for reflection, thsi will produce inf's
	you cant cascade a matrix like this anyway, but we should handle it 
	better
	'''
	t = npy.copy(s)
	if len (s.shape) > 2 :
		for f in range(s.shape[0]):
			t[f,:,:] = s2t(s[f,:,:])
	elif s.shape == (2,2):
		t = npy.array([[-1*npy.linalg.det(s),	s[0,0]],\
					[-s[1,1],1]]) / s[1,0]
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return t        
        

def t2s(t):
	'''
	converts a 'wave cascading parameters' to scattering parameters 
	
	input matrix shape should be should be 2x2, or kx2x2
	'''
	s = npy.copy(t)
	if len (t.shape) > 2 :
		for f in range(t.shape[0]):
			s[f,:,:] = t2s(s[f,:,:])
	
	elif t.shape== (2,2):
		s = npy.array([[t[0,1],npy.linalg.det(t)],\
			[1,-t[1,0]]])/t[1,1]
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return s



def cascade(a,b):
	'''
	cascade two s-matricies together.
	
	a's port 2 == b's port 1
	
	if you want a different port configuration use the flip() fuction
	takes:
		a: a 2x2 or kx2x2 s-matrix
		b: a 2x2, kx2x2, 1x1, or kx1x1 s-matrix 
	note:
		BE AWARE! this relies on s2t function which has a inf problem 
		if s11 or s22 is 1. 
	'''
	c = copy(b)
	
	if len (a.shape) > 2 :
		# assume this is a kxnxn matrix
		for f in range(a.shape[0]):
			c[f,:,:] = cascade(a[f,:,:],b[f,:,:])
	
	elif a.shape == (2,2) and b.shape == (2,2):
		c = t2s(npy.dot (s2t(a) ,s2t(b)))
	elif a.shape == (2,2) and b.shape == (1,1):
		# makes b into a two-port s-matrix so that s2t will work, but  
		# only s11 of the  resultant network is returned
		c = t2s(npy.dot (s2t(a) , \
			s2t(npy.array([[b.squeeze(),1.0],[1.0,0.0]]))))[0,0]
	else:
		raise IndexError('one of the s-matricies has incorrect shape')
	return c
	


def de_embed(a,b):	
	'''
	de-embed a 2x2 s-matrix from another 2x2 s-matrix
	
	c = b**-1 * a
	
	note:
		BE AWARE! this relies on s2t function which has a inf problem 
		if s11 or s22 is 1. 
	'''
	# TODO: re-write this and make more efficient/concise
	c = copy(a)
	
	if len (b.shape) > 2 :
		for f in range(b.shape[0]):
			if len(a.shape) == 1:
				# 'a' is a one-port netowrk
				c[f] = de_embed(a[f],b[f,:,:])
			else:
				c[f,:,:] = de_embed(a[f,:,:],b[f,:,:])
	
	elif b.shape == (2,2):
		if a.shape == (2,2):
			c = t2s(npy.dot ( npy.linalg.inv(s2t(b)), s2t(a)))
		else:
			c = t2s(npy.dot ( npy.linalg.inv(s2t(b)), \
				s2t(npy.array([[a.squeeze(),1.],[1.,0.]]))))[0,0]
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return c



def flip(a):
	'''
	invert the ports of a networks s-matrix, 'flipping' it over
	
	note:
			only works for 2-ports at the moment
	'''
	c = copy(a)
	
	if len (a.shape) > 2 :
		for f in range(a.shape[0]):
			c[f,:,:] = flip(a[f,:,:])
	elif a.shape == (2,2):
		c[0,0] = a[1,1]
		c[1,1] = a[0,0]
		c[0,1] = a[1,0]
		c[1,0] = a[0,1]
	else:
		raise IndexError('matricies should be 2x2, or kx2x2')
	return c
	





