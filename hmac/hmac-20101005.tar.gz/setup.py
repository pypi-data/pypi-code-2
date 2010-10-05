from setuptools import setup

setup(
    name = 'hmac',
    version = '20101005',
    py_modules = [ 'hmac' ],
    include_package_data = True,
    zip_safe = True,
    maintainer = 'Laurence Rowe',
    maintainer_email = 'laurence@lrowe.co.uk',
    description = "HMAC (Keyed-Hashing for Message Authentication) Python module.",
    long_description = open("README.txt").read() + "\n\n" + open("CHANGES.txt").read(),
    license = 'PSF license',
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Security :: Cryptography",
        ],
    install_requires = [
        'setuptools',
        'hashlib',
        ],
    )
