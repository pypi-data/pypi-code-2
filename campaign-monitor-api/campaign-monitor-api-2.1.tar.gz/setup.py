from setuptools import setup

setup(
    name = "campaign-monitor-api",
    version = "2.1",
    author = "Grant Young",
    author_email = "grant@zum.io",
    maintainer="Whads/Accent SL",
    maintainer_email="whads@whads.com",
    description = ("A Python class that is an implementation of common "
                   "Campaign Monitor API methods."),
    license = "LGPL",
    keywords = "campaign monitor api",
    packages=['campaign_monitor_api'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Communications :: Email"
    ],
)
