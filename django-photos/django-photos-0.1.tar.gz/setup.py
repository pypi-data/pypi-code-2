from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1'

install_requires = [
    'Django',
    'django-taggit',
    'django-templatetag-sugar',
    'easy_thumbnails',
    'django-pagination',    
    'pil'
]


setup(name='django-photos',
    version=version,
    description="This is a simple photo-app for django.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='django photo gallery',
    author='Julian Moritz',
    author_email='jumo@gmx.de',
    url='http://www.bitbucket.org/feuervogel/django-photos',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['django-photos=djangophotos:main']
    },
    test_suite='runtests.runtests'
)
