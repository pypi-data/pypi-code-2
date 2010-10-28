from setuptools import find_packages, setup

setup(
    name='SCMAccessPlugin', version='2.1',
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
        scmaccess = scm_access.scm_access
    """,
)

