from setuptools import setup, find_packages
import queued_storage

setup(
    name='django-queued-storage-fork',
    version=queued_storage.__version__,
    description='Allows for files to be uploaded locally and then transferred to a remote location. This is a fork because the original is not online.',
    long_description = open('README.rst').read(),
    author='Alen Mujezinovic',
    author_email='alen@caffeinehit.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    include_package_data=True,
    install_requires=['django-celery>=2.3.3'],
    zip_safe=False,
)
