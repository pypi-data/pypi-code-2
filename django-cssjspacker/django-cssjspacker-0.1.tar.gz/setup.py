from setuptools import setup, find_packages
setup(
    name = "django-cssjspacker",
    version = "0.1",
    packages = find_packages(),
    author = "n0s",
    author_email = "me@n0s.name",
    description = "django application for js and css compression",
    license = "BSD",
    keywords = "django",
    url = "http://bitbucket.org/n0s/django-cssjspacker/wiki/",
    include_package_data = True,
    zip_safe = False
)