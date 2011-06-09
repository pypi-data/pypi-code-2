import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "zbxsend",
    version = "0.1.1",
    author = "Sergey Kirillov",
    author_email = "sergey.kirillov@gmail.com",
    description = ("Module used to send metrics to Zabbix."),
    url='https://github.com/pistolero/zbxsend',
    license = "BSD",
    packages=['zbxsend'],
    long_description=read('README.txt'),
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ],
)