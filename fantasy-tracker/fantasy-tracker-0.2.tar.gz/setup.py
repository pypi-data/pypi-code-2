from setuptools import setup, find_packages

requirements = ['ClientForm',
                'mechanize',
                'BeautifulSoup'
               ]

commands = ['scripts/fantasy_stats']

setup(
    name='fantasy-tracker',
    version='0.2',
    description='Library to fetch Fantasy Football statistics',
    author="Matthew W. Jones",
    author_email="mat@matburt.net",
    url="http://github.com/matburt/fantasy-tracker",
    license="BSD",
    packages=find_packages(),
    scripts=commands,
    install_requires=requirements,
    zip_safe=False
)
