from setuptools import setup, find_packages

setup(
    name='minibooks',
    version='0.2.0',
    author='Caktus Consulting Group',
    author_email='solutions@caktusgroup.com',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={
        '': ['*.sql', '*.pyc', 'example_project'],
    },
    url='http://bitbucket.org/caktus/minibooks',
    license='LICENSE.txt',
    description='minibooks is a simple CRM, bookkeeping and double entry accounting package for the Django web framework.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
)

