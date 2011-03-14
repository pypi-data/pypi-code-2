import os
from setuptools import setup, find_packages

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.txt')
doc = read_file(os.path.join('src', 'cykooz', 'title', 'title.txt'))
changes = read_file('CHANGES.txt')

setup(
	name='cykooz.title',
	version='1.0.0',
	author='Cykooz',
	author_email='saikuz@mail.ru',
	description='Adapters for adapting any object to ITitle interface.',
	long_description='\n\n'.join([readme, doc, changes]),
	license='ZPL',
	keywords='zope3',
	url='https://bitbucket.org/cykooz/cykooz.title',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Framework :: Zope3',
		'License :: OSI Approved :: Zope Public License',
		'Programming Language :: Python',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Topic :: Internet :: WWW/HTTP'
		],
	packages=find_packages('src'),
	include_package_data=True,
	package_dir={'':'src'},
	namespace_packages=['cykooz'],
	extras_require=dict(
		test=[
			'zope.app.testing',
			],
		),
	install_requires=[
		'distribute',
		'zope.component',
		'zope.container',
		'zope.interface',
		'zope.dublincore',
        'zope.i18n',
		'zope.i18nmessageid',
		],
	zip_safe=False,
)
