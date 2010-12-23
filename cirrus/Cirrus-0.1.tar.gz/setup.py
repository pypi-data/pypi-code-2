import os
from setuptools import find_packages, setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Cirrus",
    version = "0.1",
    author = "Tim Kuhlman",
    author_email = "tim@backgroundprocess.com",
    description = ("Define and setup a cloud infrastructure, leveraging libcloud and yaml."),
    license = "BSD",
    keywords = "cloud libcloud yaml ec2 route53",
    include_package_data = True,
    url = "http://packages.python.org/cirrus",
    packages=find_packages(),
    scripts=['bin/dns_setup.py', 'bin/ec2_setup.py'],
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires = ['boto', 'PyYAML>=3.09', 'paramiko>=1.7.6', 'dnspython'],
)

