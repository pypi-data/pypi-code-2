try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='python-premailer',
    version='0.5.7',
    description='Prepare HTML for email; embedd CSS to inline.',
    long_description=open('README.md').read(),
    author='Ralph Bean',
    author_email='ralph.bean@gmail.com',
    url='http://github.com/ralphbean/python-premailer',
    install_requires=[
        "cssutils",
        "BeautifulSoup",
    ],
    packages=['pypremailer'],
)
