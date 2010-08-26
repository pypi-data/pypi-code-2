'''
Created on 2010/8/26

@author: Victor-mortal
'''
from setuptools import setup

setup(name='apply_firewall',
    version='1.0',
    description="""A tool for applying iptables of linux safely, it rollbacks to
 original iptables if you don't type yes in specific time period. This is useful
 to void some situation which like blocked your self from accessing SSH remotely
    """,
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    py_modules=['apply_firewall'],
    entry_points={
        'console_scripts': 'apply_firewall = apply_firewall:main'
    }
)