from setuptools import setup, find_packages
setup(
    name='cmsplugin-comments',
    version= '0.1',
    description='A very simple plugin for django-cms 2 to implement comments',
    long_description=open('README.txt').read(),
    #author='',
    #author_email='X',
    maintainer='gmh04',
    maintainer_email='gmh04@netscape.net',
    url='http://bitbucket.org/gmh04/cmsplugin_comments',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    requires= ['captcha']
)
