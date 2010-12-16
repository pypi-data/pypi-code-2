from setuptools import setup, find_packages
import os

version = '0.1b4'

setup(name='slc.calendarfetcher',
      version=version,
      description="slc.calendarfetcher will fetch and import calendars from the ICS URLs you give it.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "CHANGES.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='calendar import ical',
      author='JC Brand (Syslab.com GmbH)',
      author_email='brand@syslab.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.form==1.9.0',
          'plone.z3cform<=0.6',
          'dateable.chronos',
          'p4a.subtyper',
          'p4a.calendar==1.1',
          'p4a.plonecalendar',
          'Products.Calendaring',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
