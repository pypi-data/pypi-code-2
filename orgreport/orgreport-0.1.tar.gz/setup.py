import os
from distutils.core import setup

version = '0.1'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read()

setup(name='orgreport',
      version=version,
      description=("Format output in the Emacs org-mode format"),
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Editors :: Emacs"
        ],
      keywords='emacs org-mode',
      author='Olivier Schwander',
      author_email='schwander@lix.polytechnique.fr',
      url='http://www.lix.polytechnique.fr/~schwander/orgreport',
      license='BSD',
      py_modules=['orgreport'],
      )

