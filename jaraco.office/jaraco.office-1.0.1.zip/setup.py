from setuptools import find_packages

setup_params = dict(
	name='jaraco.office',
	use_hg_version=True,
	description="Utility library for working with MS Office documents",
	long_description=open('README').read(),
	keywords='excel office word'.split(),
	author='Jason R. Coombs',
	author_email='jaraco@jaraco.com',
	url='http://pypi.python.org/pypi/jaraco.office',
	license='MIT',
	packages=find_packages(),
	namespace_packages = ['jaraco'],
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: Microsoft :: Windows",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
	],
	zip_safe=True,
	entry_points = dict(
		console_scripts = [
			'doc-to-pdf = jaraco.office.word:doc_to_pdf_cmd',
			'doc-to-pdf-server = jaraco.office.convert:ConvertServer.start_server',
		],
	),
	install_requires = [
		'jaraco.util>=3.8.1',
	],
	setup_requires = [
		'hgtools',
	],
	use_2to3=True,
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
