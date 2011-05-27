from distutils.core import setup

setup(
    name='PyHole',
    version='1.0',
    author = "Krzysztof Dorosz",
    author_email = "cypreess@gmail.com",
    description = ("Simple, lazy REST api connector."),
    license = "BSD",
    keywords = "REST api connect connector pyhole",
    packages=['pyhole', ],
    long_description=open('README.txt').read(),
    url = "http://packages.python.org/pyhole",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    requires=['pyyaml', ],

)
