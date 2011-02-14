import os
from setuptools import find_packages, setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Cirrus",
    version = "0.3",
    author = "Tim Kuhlman",
    author_email = "tim@backgroundprocess.com",
    description = ("Define and setup a cloud infrastructure, leveraging libcloud and yaml."),
    license = "BSD",
    keywords = "cloud libcloud yaml ec2 route53",
    include_package_data = True,
    url = "https://launchpad.net/cirrus",
    packages=find_packages(),
    scripts=['bin/dns_setup.py', 'bin/ec2_setup.py', 'bin/update_host.py'],
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires = ['boto>=2.0b4', 'PyYAML>=3.09', 'paramiko>=1.7.6', 'dnspython'],
)

