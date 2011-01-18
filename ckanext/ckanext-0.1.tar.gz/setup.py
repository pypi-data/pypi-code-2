from setuptools import setup, find_packages

setup(
    name='ckanext',
    version='0.1',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    license='AGPL',
    url='http://ckan.org/',
    description='CKAN common library for extensions',
    keywords='data packaging component tool server',
    install_requires=[
        "Amara",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'ckan': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [ckan.forms]
    geo = ckanext.geo.geo_form:get_fieldset

    [console_scripts]
    amqp_listener = ckanext.amqp:listener
    link_checker = ckanext.link_checker:checker

    [ckan.plugins]
    form_api_tester = ckanext.plugins.form_api_tester:FormApiTester
    """,
    test_suite = 'nose.collector',
)
