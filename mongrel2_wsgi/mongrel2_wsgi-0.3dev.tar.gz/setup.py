from setuptools import setup, find_packages

version = '0.3'

setup(name='mongrel2_wsgi',
      version=version,
      description="Mongrel2 handler to WSGI.",
      long_description="""\
A Mongrel2 handler for WSGI applications. Based on the CherryPy WSGI
server, eventlet, and ZeroMQ. Supports streaming and chunked responses.
""",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
          ],
      keywords='wsgi mongrel2 eventlet',
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/mongrel2_wsgi',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "pyzmq",
          "eventlet",
          "PasteScript",
          "PasteDeploy",
      ],
      entry_points="""
      [paste.server_runner]
      main = mongrel2_wsgi.runner:server_runner
      """,
      )
