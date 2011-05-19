from setuptools import setup, find_packages
import os

version = '0.0.1'
name='slapos.recipe.java'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    author="Cedric de Saint Martin",
    author_email="cedric.dsm@tiolive.com",
    description="zc.buildout recipe that downloads and installs Java",
    long_description=(read('README.txt')),
    license='ZPL 2.1',
    keywords = "buildout java slapos",
    url='http://www.slapos.org/',

    packages=find_packages('src'),
    include_package_data=True,
    package_dir = {'': 'src'},
    namespace_packages=['slapos', 'slapos.recipe'],
    install_requires=['zc.buildout', 'setuptools'],
    entry_points={'zc.buildout': ['default = %s.recipe:Recipe' % name]},
    zip_safe=False,
    )
