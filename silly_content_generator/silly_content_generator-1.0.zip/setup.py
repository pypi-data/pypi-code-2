
from setuptools import setup

setup(
    version='1.0',
    name='silly_content_generator',
    description='A tool to generate sample website content',
    long_description=open('README.txt','rb').read(),
    author='Alex Clark',
    author_email='aclark@aclark.net',
    url='https://github.com/aclark4life/silly_content_generator',
    py_modules=['silly_content_generator'],
    install_requires=['lorem-ipsum-generator'],
    entry_points = {
        'console_scripts': [
            'silly_content_generator = silly_content_generator:main',
        ],
    }
)
