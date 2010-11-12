from setuptools import setup, find_packages

setup(name='transbot',
      version='1.0.2',
      description='Inter-channel IRC automatic translation bot using Google Translate API',
      author='Taylor Rose & Mark Thill',
      author_email='tjr1351@rit.edu & mrt8449@rit.edu',
      url='http://fedorahosted.org/transbot',
      license=['gpl-3.0'],
      packages=find_packages(),
      include_package_data=True,
      scripts = ["transbot"]
      )
