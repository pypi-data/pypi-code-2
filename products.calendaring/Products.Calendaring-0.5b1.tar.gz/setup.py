from setuptools import setup, find_packages


version = '0.5b1'

setup(
    name="Products.Calendaring",
    version=version,
    long_description=open(("README")).read(),
    description="An iCalendar marshaller for Marshall",
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    author="Sidnei da Silva",
    author_email="sidnei@enfoldsystems.com",
    url="http://dist.enfoldsystems.com/catalog/calendaring",
    packages=find_packages(),
    namespace_packages=["Products"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "icalendar",
        "python-dateutil",
        ],
    )
