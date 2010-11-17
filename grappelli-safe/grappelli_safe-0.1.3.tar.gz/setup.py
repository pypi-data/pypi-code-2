from setuptools import setup, find_packages

setup(
    name='grappelli_safe',
    version='0.1.3',
    description='The grappelli_2 branch of django-grappelli packaged correctly',
    author='Patrick Kranzlmueller, Axel Swoboda (vonautomatisch)',
    author_email='werkstaetten@vonautomatisch.at',
    maintainer='Stephen McDonald',
    maintainer_email='stephen.mc@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

