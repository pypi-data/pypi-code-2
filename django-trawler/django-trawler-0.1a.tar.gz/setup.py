from setuptools import setup
from trawler import __version__
setup(
    name="django-trawler",
    version=__version__,
    url="https://bitbucket.org/onelson/django-trawler",
    author="Owen Nelson",
    author_email="onelson@gmail.com",
    license="MIT",
    description="Django App for running phishing campaigns (for staff "
    "security awareness training).",
    long_description=open('README').read(),
    keywords="phishing, security, django",
    packages=['trawler'],
    include_package_data=True,
    setup_requires=['setuptools'],
    install_requires=['setuptools', 'django>=1.3'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: "
                              "Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules"],

)

