#import ez_setup
#ez_setup.use_setuptools()

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
	name='tabola',
	version='0.0.5',
	author='L. C. Rees',
	author_email='lcrees@gmail.com',
	url='http://pypi.python.com/tabola/',
	packages=['tabola', 'tabola.formats'],
	install_requires=['xlwt', 'simplejson', 'PyYAML'],
	license='MIT',
	classifiers=(
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
        'Programming Language :: Python',
	),
    zip_safe = True,
)