import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'linseed',
    version = '0.3',
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Austin Bingham',
    author_email = 'austin.bingham@gmail.com',
    description = 'Gather and print linux system information.',
    license = 'MIT',
    keywords = 'system info resources',
    url = 'http://code.google.com/p/linseed/',

    entry_points = {
        'console_scripts': [
            'linseed = linseed.app:main',
            ],

        'linseed.info_source': [
            'linseed.batteries = linseed.battery:Batteries',
            'linseed.cpus = linseed.cpu:CPUs',
            'linseed.memory = linseed.memory:Memory',
            'linseed.swap = linseed.memory:Swap',
            'linseed.wicd = linseed.wicd:WICD',
            'linseed.current_time = linseed.current_time:CurrentTime',
            ],
        },

    install_requires=[
        # 'dbus',
        'baker',
        ],
    )
