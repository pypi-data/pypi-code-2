from distutils.core import setup
from os import walk

def getPackages():
	l = []
	for a, b, c in walk('mibian'):
		l.append(a.replace('/','.'))
	return l	

setup(
	name='mibian',	
	version='0.0.1',
	description='Options Pricing Library',
	author='Yassine Maaroufi',
	author_email='yassinemaaroufi@gmail.com',
	url='http://code.mibian.net/',
	license='GPL',
	packages=getPackages(),
	requires=['scipy']
	)
