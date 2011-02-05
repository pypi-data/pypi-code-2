from distutils.core import setup

setup(
    name='yamlconfig',
    version='0.3.1',
    description='YAML configuration file reader with basic variable interpolation.',
    author='Kelsey Hightower',
    author_email='kelsey.hightower@gmail.com',
    url='https://bitbucket.org/khightower/yamlconfig',
    py_modules=['yamlconfig'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    install_requires=['PyYAML >= 3.0']
    )
