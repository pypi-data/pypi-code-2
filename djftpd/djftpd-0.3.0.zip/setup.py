from setuptools import setup, find_packages

setup(
    name = 'djftpd',
    version = '0.3.0',
    url = 'http://bitbucket.org/weholt/djftpd',
    author = 'Thomas Weholt',
    author_email = 'thomas@weholt.org',
    description = 'FTP-server authenticating against django user database.',
    license = 'GPL v3.0',
    packages = find_packages(),
    install_requires = ('pyftpdlib','django'),
    zip_safe = False,
)
