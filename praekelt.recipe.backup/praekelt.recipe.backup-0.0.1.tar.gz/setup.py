from setuptools import setup, find_packages

setup(
    name='praekelt.recipe.backup',
    version='0.0.1',
    description='Filesystem and database backup Buildout recipe.',
    long_description = open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/praekelt.recipe.backup',
    packages = find_packages(),
    install_requires = [
        'zc.recipe.egg',
    ],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = praekelt.recipe.backup:Backup']},
)
