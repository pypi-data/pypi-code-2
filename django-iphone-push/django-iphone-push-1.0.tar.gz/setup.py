from distutils.core import setup

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Framework :: Django
Programming Language :: Python
"""

setup(
    name="django-iphone-push",
    version="1.0",
    description="Add iPhone Push notifications to a Django Project quickly and easily",
    author="Lee Packham",
    author_email="lpackham@leenux.org.uk",
    url="http://leepa.github.com/django-iphone-push/",
    packages=['iphonepush', 'iphonepush.migrations'],
    platforms=["any"],
    license="See LICENSE.txt",
    classifiers = filter(None, classifiers.split("\n")),
)