from setuptools import setup, find_packages

setup(
    name='django-groupcache',
    version=__import__('groupcache').__version__,
    license='BSD',

    description='Reusable Django App for Generational Caching of Views',
    long_description=open('README.rst').read(),

    author='Sylvain Fourmanoit',
    author_email='fourmanoit@gmail.com',

    url='http://syfou.bitbucket.org/django-groupcache',
    
    include_package_data = True,
    
    packages = ['groupcache'],
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django'
        ]
)
