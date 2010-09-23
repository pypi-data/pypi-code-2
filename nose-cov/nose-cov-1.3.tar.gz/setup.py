import setuptools

setuptools.setup(name='nose-cov',
                 version='1.3',
                 description='nose plugin for coverage reporting, including subprocesses',
                 long_description=open('README.txt').read().strip(),
                 author='Meme Dough',
                 author_email='memedough@gmail.com',
                 url='http://bitbucket.org/memedough/nose-cov/overview',
                 py_modules=['nose_cov'],
                 install_requires=['nose>=0.11.4',
                                   'cov-core>=1.2'],
                 entry_points={'nose.plugins': ['cov = nose_cov:Cov']},
                 license='MIT License',
                 zip_safe=False,
                 keywords='nose nosetest cover coverage',
                 classifiers=['Development Status :: 4 - Beta',
                              'Intended Audience :: Developers',
                              'License :: OSI Approved :: MIT License',
                              'Operating System :: OS Independent',
                              'Programming Language :: Python',
                              'Programming Language :: Python :: 2.4',
                              'Programming Language :: Python :: 2.5',
                              'Programming Language :: Python :: 2.6',
                              'Programming Language :: Python :: 2.7',
                              'Programming Language :: Python :: 3.0',
                              'Programming Language :: Python :: 3.1',
                              'Topic :: Software Development :: Testing'])
