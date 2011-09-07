from setuptools import setup, find_packages

setup(
    name='django-googleanalytics',
    version='1.0',
    description='Google Analytics templatetag for Django',
    author='Gonzalo Saavedra',
    author_email='gonzalosaavedra@gmail.com',
    url='http://code.google.com/p/django-googleanalytics/',
    license = 'BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
