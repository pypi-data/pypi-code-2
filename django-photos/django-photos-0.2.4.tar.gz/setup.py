from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2.4'

install_requires = [
    'Django',
    'django-taggit',
    'django-templatetag-sugar',
    'easy_thumbnails',   
    'pil'
]


setup(name='django-photos',
    version=version,
    description="This is a simple photo-app for django.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
                 "Development Status :: 3 - Alpha",
                 "Environment :: Web Environment",
                 "Framework :: Django",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 
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
