from setuptools import setup, find_packages
import os

version = '1.2.0'

setup(name='five.grok',
      version=version,
      description="Grok-like layer for Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        ],
      keywords='zope2 grok',
      author='Lennart Regebro, Godefroid Chapelle',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/five.grok/',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'martian',
        'Zope2>=2.12.3',
        'five.formlib',
        'five.localsitemanager > 2.0dev',
        'grokcore.component',
        'grokcore.formlib >= 1.4',
        'grokcore.view >= 1.12.1',
        'grokcore.viewlet >= 1.3',
        'grokcore.security',
        'grokcore.site',
        'grokcore.annotation',
        ],
      )
