from setuptools import setup


setup(
        name = 'pbot',
        version = '1.4.0',
        packages = ['pbot'],
        install_requires = ['lxml'],
        author = 'Pavel Zhukov',
        author_email = 'gelios@gmail.com',
        description = 'An simple site crawler with proxy support',
        long_description = open('README').read(),
        license = 'GPL',
        keywords = 'crawling, bot',
        url = 'http://bitbucket.org/zeus/pbot'
     )

