from distutils.core import setup

setup(
	name='RapLeafApi',
	author='RapLeaf',
	author_email='developer@rapleaf.com',
	version='0.1.0',
	packages=['rapleafApi'],
	url='http://www.rapleaf.com',
	download_url='https://github.com/Rapleaf/Personalization-Dev-Kits',
	description='A library for interacting with RapLeaf\'s Personalization API',
	keywords='rapleaf api',
	install_requires=['urllib3'],
	long_description=open('README.txt').read(),
)
