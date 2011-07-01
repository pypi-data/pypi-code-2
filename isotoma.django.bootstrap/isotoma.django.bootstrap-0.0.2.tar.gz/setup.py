from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name = 'isotoma.django.bootstrap',
    version = version,
    description = "Bootstrap a django project to isotoma code standards",
    url = "http://github.com/isotoma/isotoma.django.bootstrap",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    classifiers = [
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
        ],
    keywords = "django project bootstrap",
    author = "Tom Wardill",
    author_email = "tom.wardill@isotoma.com",
    license = "Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    package_data = { 
        '': ['README.rst', 'CHANGES.txt'],
        'isotoma.django.bootstrap': ['templates/*.tmpl']
    },
    namespace_packages = ['isotoma', 'isotoma.django'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'Django',
        'Jinja2',
        'setuptools',
        ],
    entry_points = {
        'console_scripts':
        ['djangoboot = isotoma.django.bootstrap:main'],
        }
    )