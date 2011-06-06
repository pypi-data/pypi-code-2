from setuptools import setup, find_packages

version = '0.1'
description = "Tekh is a template which utilizes ZODB + ZEO for the database and other pyramid modules."
description_extra = "The other modules it uses are: coverage, nose, pyramid, pyramid_beaker, pyramid_mailer, pyramid_jinja2, and repoze.folder."

setup(name='tekh',
      version=version,
      description=description,
      long_description=description + description_extra,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ZODB ZEO coverage nose pyramid pyramid_beaker pyramid_mailer pyramid_jinja2 beaker mailer jinja2',
      author='Nathan McBride',
      author_email='nmcbride@ndmwebdesign.com',
      url='http://www.ndmwebdesign.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      exclude_package_data={'':['*.pyc']},
      zip_safe=False,
      install_requires=[
          "PasteScript>=1.3",
          "pyramid"
      ],
      entry_points="""
      [paste.paster_create_template]
      tekh = tekh:TekhProjectTemplate
      """,
     )
