from setuptools import setup, find_packages

setup(
    name='sortable',
    version='0.1',
    description='An app to add drag-and-drop to Grappelli admin to reorder instances of models.',
    author='Red Interactive Agency',
    author_email='geeks@ff0000.com',
    url='http://github.com/ff0000/sortable/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)

