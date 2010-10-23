from setuptools import setup, find_packages

def main():
    setup(
        name='pywhois',
        version='0.1',
        author='Michael Carter',
        author_email='CarterMichael@gmail.com',
        license='MIT',
        description="A whois program with truncated output",
        long_description='',
        packages= find_packages(),
        zip_safe = False,
        install_requires = [],
        entry_points = '''    
            [console_scripts]
            pywhois = pywhois.bin:main
        ''',
        
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],        
    )


if __name__ == '__main__':
    main()
