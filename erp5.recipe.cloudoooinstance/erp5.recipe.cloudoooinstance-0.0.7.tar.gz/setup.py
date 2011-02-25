from setuptools import setup, find_packages

name = "erp5.recipe.cloudoooinstance"
version = '0.0.7'

setup(
    name = name,
    version = version,
    author = "Gabriel M. Monnerat",
    author_email = "gabriel@tiolive.com",
    description = "ZC Buildout recipe for installing a cloudooo instance",
    long_description="""\n""",
    license = "ZPL 2.1",
    keywords = "cloud buildout",
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    install_requires=["z3c.recipe.template",],
    namespace_packages = ['erp5', 'erp5.recipe'],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
