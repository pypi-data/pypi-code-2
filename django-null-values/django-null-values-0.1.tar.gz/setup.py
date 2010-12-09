from distutils.core import setup

setup(
    name = "django-null-values",
    version = "0.1",
    description = "Automatically convert empty strings to NULL if null=True",
    url = "http://hg.schinckel.net/django-null-values/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "null_values",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
