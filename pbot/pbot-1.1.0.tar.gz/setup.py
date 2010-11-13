from setuptools import setup


setup(
        name = 'pbot',
        version = '1.1.0',
        packages = ['pbot'],
        install_requires = [],
        author = 'Pavel Zhukov',
        author_email = 'gelios@gmail.com',
        description = 'An simple site crawler with proxy support',
        long_description = 'An simple site grawler, project target - save state (cookies, referrer) between requests. \
         Also support lxml.html.submit_form with bot.open_http method',
        license = 'GPL',
        keywords = 'crawling, bot',
        url = 'http://bitbucket.org/zeus/pbot'
     )

