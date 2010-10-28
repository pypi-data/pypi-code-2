import os

from setuptools import setup, find_packages

 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = ['zc.buildout', 'zc.recipe.egg']

setup(
    name='thechristmaspig',
    version="0.9.2",
    description="Buildout recipe for Django. Sets up controls scripts and wsgi file.",
    long_description=read("README.rst"),
    url='http://github.com/prestontimmons/thechristmaspig',
    license='BSD',
    author='Preston Timmons',
    author_email='prestontimmons@gmail.com',
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
    ],
    packages=find_packages(exclude=['example', 'parts', 'eggs']),
    keywords='',
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
    # -*- Entry points: -*-
    [zc.buildout]
    default = recipe:Recipe
    """,
)
