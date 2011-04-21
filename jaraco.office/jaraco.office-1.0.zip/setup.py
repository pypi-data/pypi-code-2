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
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
	],
	zip_safe=True,
	entry_points = dict(
		console_scripts = [
			'doc-to-pdf = jaraco.office.word:doc_to_pdf_cmd',
			'doc-to-pdf-server = jaraco.office.convert:ConvertServer.start_server',
		],
	),
	setup_requires = [
		'hgtools',
	],
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
