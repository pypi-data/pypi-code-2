import os
from setuptools import setup



readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
        name     = 'django-latex',
        version  = '0.1',
        packages = ['latex'],

        requires = ['python (>= 2.4)', 'django (>= 1.1)',],

        description  = 'Django application to generate latex/pdf files.',
        long_description = readme,
        author       = 'Bearstech',
        author_email = 'jcharpentier@bearstech.com',
        url          = 'http://bitbucket.org/bearstech/django-latex',
        download_url = '',
        license      = 'GPL v3',
        keywords     = 'django models pdf latex pdflatex',
        classifiers  = [
                    'Development Status :: 4 - Beta',
                    'Environment :: Web Environment',
                    'Framework :: Django',
                    'Intended Audience :: Developers',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                ],
)

