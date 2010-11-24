from setuptools import setup
setup(
      name="pyxontime",
      version="0.3",
      author="Arnaud Bos",
      author_email="arnaud.tlse@gmail.com",
      description="Python software to get OXONTIME's bus schedules of Oxfordshire",
      long_description=open("README.rst").read(),
      packages=["pyxontime", "pyxontime.cli", "pyxontime.gui"],
      install_requires=["pyquery","pygobject","pygtk"],
      scripts=["pyxontime-cli.py","pyxontime-gui.py"])
