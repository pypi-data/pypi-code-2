from distutils.core import setup

setup(
    name='ihttp',
    packages=['ihttp'],
    version='0.2',
    description='Easy python http fetch module',
    author='Alan Castro',
    author_email='alanclic@gmail.com',
    url='http://alancastro.org',
    keywords = ["http", "fetch", "get", "post"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP"
        ],
    long_description = open('README.markdown').read()
)
