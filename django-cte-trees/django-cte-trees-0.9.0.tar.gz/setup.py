from setuptools import setup, find_packages
import cte_tree
 
setup(
    name = 'django-cte-trees',
    version = cte_tree.__version__,
    packages = find_packages(),
    include_package_data=True,
    author = 'Alexis Petrounias',
    maintainer = 'Alexis Petrounias',
    keywords = 'django, postgresql, cte, trees, sql',
    license = 'BSD',
    description = 'Experimental implementation of Adjecency-List trees using PostgreSQL Common Table Expressions (CTE) for Django.',
    long_description=open('README.txt').read(),
    url='http://www.petrounias.org/software/django-cte-trees/',
    download_url = "https://bitbucket.org/petrounias/django-cte-trees/get/tip.tar.gz",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

