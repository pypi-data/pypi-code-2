from distutils.core import setup

setup(
    name='XeroAPI',
    version='0.0.1',
    author='Beesdom',
    author_email='team@beesdom.com',
    packages=['xeroapi', 'xeroapi.tests'],
    url='http://pypi.python.org/pypi/XeroAPI/',
    license='LICENSE.txt',
    description='Python client API for private XERO applications.',
    long_description=open('README.txt').read(),
    install_requires=[
        "M2Crypto",
        "oauth2",
    ],
)
