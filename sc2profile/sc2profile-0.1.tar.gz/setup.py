from distutils.core import setup
from email.utils import parseaddr

from sc2profile import __version__, __author__

name, email = parseaddr(__author__)

setup(version=__version__,
      name='sc2profile',
      py_modules=['sc2profile'],

      author=name,
      author_email=email,
      description='Fetch StarCraft II profiles on battle.net',
      license='ISCL',
      keyword='starcraft battle.net profile',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ISC License (ISCL)',
          'Programming Language :: Python :: 2.6',
      ])
