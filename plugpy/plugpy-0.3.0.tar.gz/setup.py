from setuptools import setup

version_tuple = __import__('plugpy').VERSION

if version_tuple[2] is not None:
    version = "%d.%d.%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

setup(
    name = "plugpy",
    version = version,
    url = 'http://bitbucket.org/mopemope/plugpy/',
    author = 'yutaka.matsubara',
    author_email = 'yutaka.matsubara@gmail.com',
    maintainer = 'yutaka.matsubara',
    maintainer_email = 'yutaka.matsubara@gmail.com',
    license='MIT License',
    description = 'Simple Plugin System ',
    packages = ['plugpy', 'plugpy.ext'],
    classifiers = [
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"
        ]
)
