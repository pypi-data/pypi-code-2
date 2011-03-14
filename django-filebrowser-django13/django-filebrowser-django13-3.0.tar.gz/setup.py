from setuptools import setup, find_packages

setup(
    name='django-filebrowser-django13',
    version='3.0',
    description='Media-Management with the Django Admin-Interface. Package for using without django-grapelli in Django 1.3',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    url='http://github.com/msaelices/django-filebrowser-no-grappelli-for-django13',
    packages=find_packages(),
    include_package_data=True,
    package_data = {'filebrowser': ['templates/filebrowser/*.html',
                                    'templates/filebrowser/include/*',
                                    'locale/*/LC_MESSAGES/*',
                                    'media/filebrowser/*/*'],
                    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
