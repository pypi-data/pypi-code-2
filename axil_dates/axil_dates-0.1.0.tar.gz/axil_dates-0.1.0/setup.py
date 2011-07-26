from setuptools import setup, find_packages
 
version = '0.1.0'
 
LONG_DESCRIPTION = open('README').read()
 
setup(
    name='axil_dates',
    version=version,
    description="axil_dates",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='django,dates,times',
    author='CashStar Inc',
    author_email='kcochrane@cashstar.com',
    url='https://bitbucket.org/cashstar/axil_dates',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)