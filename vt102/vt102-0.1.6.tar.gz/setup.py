from distutils.core import setup
import sys

setup(name="vt102",
      version="0.1.6",
      author="Sam Gibson",
      author_email="sam@ifdown.net",
      url="https://github.com/samfoo/vt102",
      description="Simple vt102 emulator, useful for screen scraping.",
      packages=["vt102"],
      provides=["vt102"],
      keywords="vt102 terminal emulator screen scraper",
      license="Lesser General Public License v3.0",
)
