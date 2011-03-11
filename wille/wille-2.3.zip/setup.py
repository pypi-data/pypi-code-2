from setuptools import setup

def readme():
    return open('README.txt','rt').read()

setup(
    name = "wille",
    version = "2.3",
    author = "TUT / Hypermedia Laboratory",
    author_email = "jaakko.salonen@tut.fi",
    description = ("Wille Visualisation Framework"),
    license = "BSD",
    keywords = "visualisation framework",
    url = "http://packages.python.org/wille",
    packages=['wille', 'wille.utils', 'tests'],
    long_description=readme(),
    scripts=['scripts/wille-server.py', 'scripts/wille-admin.py'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires = [
        'httplib2>=0.6.0',
        'pyjavaproperties>=0.5',
        'feedparser>=5.0',
        'argparse>=1.1'
    ],
)
