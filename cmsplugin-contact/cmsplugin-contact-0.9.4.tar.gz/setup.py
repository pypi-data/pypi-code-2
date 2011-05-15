from setuptools import setup, find_packages

setup(
    name='cmsplugin-contact',
    version='0.9.4',
    description='Contact form plugin for Django CMS with spam protection and i18n',
    author='Maccesch',
    author_email='maccesch@gmail.com',
    url='http://github.com/maccesch/cmsplugin-contact',
    packages=find_packages(),
    keywords='contact form django cms django-cms spam protection email',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
