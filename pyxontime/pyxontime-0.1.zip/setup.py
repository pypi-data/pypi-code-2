from setuptools import setup
setup(
      name="pyxontime",
      version="0.1",
      author="Arnaud Bos",
      author_email="arnaud.tlse@gmail.com",
      description="",
      long_description=open("README.rst").read(),
      packages=["pyxontime", "pyxontime.cli"],
      install_requires=["pyquery",],
      scripts=["run-pyxontime.py",])
