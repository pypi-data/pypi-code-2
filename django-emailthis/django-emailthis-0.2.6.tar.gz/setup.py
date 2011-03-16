from distutils.core import setup

description = """
a simple email-to-a-friend application that generates an email
form, handles its submission, persists the submission data to a
database, and sends a templated email.  Both anonymous and registered
users can send email.
"""

long_description = description + """

This app started out as a quasi-fork of Jeff Croft's "mailfriend" app
(http://code.google.com/p/django-mailfriend/), but the latter only
supported registered users; this supports users of both
the registered and unregistered varieties.

Form submission is here done solely via ajax; form loading is intended
to be handled similarly.

"""

version = "0.2.6"

setup(author="Jacob Smullyan",
      author_email='jsmullyan@gmail.com',
      description=description,
      long_description=long_description,
      license="BSD",
      platforms='OS Independent',
      name="django-emailthis",
      url="http://code.google.com/p/django-emailthis/",
      classifiers=[
    "Development Status :: 3 - Alpha",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      version=version,
      keywords="django email",
      packages=("emailthis",),
      package_dir={'': '.'},
      )
