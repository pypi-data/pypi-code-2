from setuptools import setup, find_packages

setup(
    name='Ygrep',
    url='https://github.com/marianobarrios/ygrep',
    version='0.1dev',
    packages=find_packages(),
    license='GPL',
    requires='PyYAML',
    long_description=open('README.txt').read(),
    author = "Mariano Barrios",
    author_email = "marianobarrios@gmail.com",
    entry_points = {  
        'console_scripts': ['ygrep = ygrep.ygrepmain']
    }
)
