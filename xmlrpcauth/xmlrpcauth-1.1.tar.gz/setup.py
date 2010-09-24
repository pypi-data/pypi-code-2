from setuptools import setup, find_packages

setup(
    name='xmlrpcauth',
    version='1.1',
    author='Christian Theune',
    author_email='ct@gocept.com',
    url='https://pypi.python.org/pypi/xmlrpcauth',
    description="""\
HTTP Basic-Auth transport for xmlrpclib.Server
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
)
