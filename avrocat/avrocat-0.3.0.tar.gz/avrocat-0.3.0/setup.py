from setuptools import setup

setup(name="avrocat",
      version="0.3.0",
      description="`cat` (and write) for Avro files",
      author="Miki Tebeka",
      author_email="miki.tebeka@gmail.com",
      license="MIT",
      url="https://bitbucket.org/tebeka/avrocat/src",
      requires=["avro"],
      scripts=["src/avrocat", "src/avrowrite"],
)
