from setuptools import find_packages, setup

setup(
    name="zc.signalhandler",
    description="Configurable signal handling for ZConfig",
    long_description=open("README.txt").read(),
    author='Zope Corporation',
    author_email='info@zope.com',
    license="ZPL 2.1",
    version="1.2.0",
    packages=find_packages("src"),
    namespace_packages=["zc"],
    package_dir={"": "src"},
    install_requires=["ZConfig >= 2.4a3"],
    extras_require={"test": ["zope.testing"]},
    include_package_data=True,
    zip_safe=False,
    )
