try:
    from distribute import setup
except ImportError:
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

setup(version='0.2',
      name='reform',
      packages=['reform'],
      author=u'Henry Pr\u00EAcheur',
      author_email='henry@precheur.org',
      description='Validate and convert forms',
      license='ISCL',
      keyword='form html http web',
      install_requires=['MarkupSafe>=0.11'],
      test_suite='tests',
      classifiers=[
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ISC License (ISCL)',
          'Programming Language :: Python :: 2.6',
      ])
