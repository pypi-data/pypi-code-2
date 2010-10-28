from setuptools import find_packages, setup

setup(
    name='SCMAccessPlugin', version='2.0',
    description = "Trac plugin for SCM access control",
    author = "Stefan Richter",
    author_email = "stefan@02strich.de",
    url = "http://www.02strich.de",
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Framework :: Trac',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Python Software Foundation License',
            'Programming Language :: Python :: 2',],
	
    packages=find_packages(exclude=['*.tests*']),
    entry_points = """
        [trac.plugins]
        svnaccess = svn_access.svn_access
    """,
)

