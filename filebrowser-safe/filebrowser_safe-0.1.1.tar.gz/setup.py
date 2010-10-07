from setuptools import setup, find_packages

setup(
    name='filebrowser_safe',
    version='0.1.1',
    description='The filebrowser_3 branch of django-filebrowser packaged correctly',
    author='Patrick Kranzlmueller, Axel Swoboda (vonautomatisch)',
    author_email='werkstaetten@vonautomatisch.at',
    maintainer='Stephen McDonald',
    maintainer_email='stephen.mc@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

