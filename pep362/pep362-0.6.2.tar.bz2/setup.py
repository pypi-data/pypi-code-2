from distutils.core import setup

setup(
        # Package metadata.
        name='pep362',
        version='0.6.2',
        description='Implementation of PEP 362 (Function Signature objects)',
        author='Brett Cannon',
        author_email='brett@python.org',
        url='http://svn.python.org/view/sandbox/trunk/pep362/',
        # Files.
        py_modules=['pep362', 'examples'],
        packages=['tests'],
        data_files=['README'],
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
        ]
    )
