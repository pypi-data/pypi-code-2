from setuptools import setup, find_packages

fd = open("README")
long_description = fd.read()
fd.close()

setup(
    name='titere',
    version='0.1',
    description='Automated toold that manage configurations',
    author='Jorge Eduardo Cardona',
    author_email='jorgeecardona@gmail.com',
    license="BSD",
    url="http://pypi.python.org/pypi/titere/",
    long_description=long_description,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'titere = titere.main:main',
            ],
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        ],
    )
