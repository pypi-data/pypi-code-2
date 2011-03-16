from setuptools import setup

setup(
    name = 'everjoke',
    version = '0.2.2',
    description = 'Write and Manage Jokes',
    author = 'Cody Hess',
    author_email = 'cody.hess@gmail.com',
    packages = ['everjokeCLI'],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X"],
    install_requires = ['sqlalchemy', 'argparse'],
    entry_points = {'console_scripts':
        ['everjoke = everjokeCLI.EverjokeCLI:main']})
