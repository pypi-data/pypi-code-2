from setuptools import setup, find_packages

version = '2.0'

setup(name='collective.arboreal',
      version=version,
      description="Arboreal is a tool which lets you manage multiple trees.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],
      keywords='archetypes trees field widget index',
      author='Pareto',
      author_email='info@pareto.nl',
      url='http://pypi.python.org/pypi/collective.arboreal',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.i18n'
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
