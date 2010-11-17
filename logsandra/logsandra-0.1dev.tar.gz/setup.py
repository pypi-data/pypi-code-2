try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='logsandra',
    version='0.1',
    description='',
    maintainer='Tyler Hobbs',
    maintainer_email='tyler@riptano.com',
    url='http://github.com/thobbs/logsandra',
    requires=[
        "Pylons(>=1.0)",
        "Jinja2",
        "PyYAML",
        "pycassa(>=0.5.4)",
        "python_dateutil(>=1.0)",
        "CherryPy(>=3.1)",
        "thrift05",
        "ordereddict"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'logsandra': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'logsandra': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    scripts=['logsandra-httpd.py', 'logsandra-monitord.py'],
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = logsandra.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """
)
