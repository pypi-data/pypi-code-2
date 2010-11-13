from setuptools import setup


setup(
        name='decolib',
        version='0.0.1',
        packages=['decolib'],
        install_requires=[
        ],
        author='Pavel Zhukov',
        author_email='gelios@gmail.com',
        description='Various python decorators',
        long_description='''
        Various useful python decorators:
        - retry(tries, delay=3, backoff=2) \
        Retries a function or method until it complite without exeptions \
        delay sets the initial delay, and backoff sets how much the delay should \
        lengthen after each failure. backoff must be greater than 1, or else it \
        isn't really a backoff. tries must be at least 0, and delay greater than 0

        - memoized
        Classic memoization. Function cache results, then return objects from cache for same argumets
        ''',
        license='GPL',
        keywords='decorators',
        url='http://bitbucket.org/zeus/decolib'
        )

