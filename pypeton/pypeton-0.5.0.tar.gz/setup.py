from distutils.core import setup

setup(
    name         = 'pypeton',
    packages     = ['pypeton',],
    scripts      = ['pypeton/pypeton',],
    version      = '0.5.0',
    author       = 'RED Interactive Agency',
    author_email = 'geeks@ff0000.com',

    package_data = {
        'pypeton': [
            'files/django/*.*',
            'files/django/deploy/*.*',
            'files/django/deploy/cron/*.*',
            'files/django/deploy/requirements/*.*',
            'files/django/deploy/scripts/*.*',
            'files/django/env/*.*',
            'files/django/logs/*.*',
            'files/django/migrations/*.*',
            'files/django/project/*.*',
            'files/django/project/apps/*.*',
            'files/django/project/apps/initial_data/*.*',
            'files/django/project/apps/initial_data/fixtures/*.*',
            'files/django/project/apps/initial_data/management/*.*',
            'files/django/project/apps/initial_data/management/commands/*.*',
            'files/django/project/apps/initial_data/middleware/*.*',
            'files/django/project/settings/*.*',
            'files/django/project/static/*.*',
            'files/django/project/templates/*.*',
            'files/django/uploads/*.*',
        ]
    },

    url          = 'http://www.github.com/ff0000/pypeton/',
    download_url = 'http://www.github.com/ff0000/pypeton/',

    license      = 'MIT license',
    description  = """ Tool to start Django and Bongo projects """,

    long_description = open('README.markdown').read(),
    install_requires = ['pycolors2',],

    classifiers  = (
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ),
)
