from setuptools import setup, find_packages

version = '0.3'

setup(name='any2fixed',
      version=version,
      description="A tool to generate fixed length files from a list of python instances",
      long_description="""\
""",
      classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Text Processing :: General",
          ],
      keywords='fixed length python',
      author='Florent Aide',
      author_email='florent.aide@gmail.com',
      url='',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "pyjon.utils"
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
