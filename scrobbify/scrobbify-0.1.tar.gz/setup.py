from setuptools import setup

setup(
    name='scrobbify',
    version='0.1',
    description="Real-time 'now playing notifications' for Spotify",
    author='Steve Winton',
    author_email='stevewinton@gmail.com',
    url='http://github.com/swinton/scrobbify',
    py_modules=['scrobbify'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Free For Home Use",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Topic :: Desktop Environment",
    ],
    keywords='spotify desktop',
    license='GPL',
    install_requires=[
        'setuptools',
        'pylibpcap >=0.6.2'
    ],
)