from distutils.core import setup

setup(
    name='dopen',
    version='0.2.1dev',
    description='Extension-based Opener',
    author='Darragh van Tichelen',
    author_email='darragh.ssa@gmail.com',
    packages=['dopen',],
    package_data={'dopen': ['*.ded']},
    license='LGPL-3',
    long_description=open('README.txt').read(),
)
