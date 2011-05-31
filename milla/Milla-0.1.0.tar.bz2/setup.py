try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Milla',
    version='0.1.0',
    description='Lightweight WSGI framework for web applications',
    author='Dustin C. Hatch',
    author_email='admiralnemo@gmail.com',
    url='', #TODO: Bitbucket URL here
    install_requires=[
        'WebOb',
        'WebError'
    ],
    packages=find_packages('src', exclude=['distribute_setup']),
    package_dir={'': 'src'},
    entry_points={
        'milla.request_validator': [
            'default = milla.auth:RequestValidator'
        ]
    }
)
