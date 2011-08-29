from distutils.core import setup

setup(name='scrapy-redis',
      version='0.1',
      description='Redis-based components for Scrapy',
      author='Rolando Espinoza La fuente',
      author_email='darkrho@gmail.com',
      url='http://github.com/darkrho/scrapy-redis',
      packages=['scrapy_redis'],
      license='BSD',
      #install_requires=['Scrapy>=0.13'],
      classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
      ]
     )
