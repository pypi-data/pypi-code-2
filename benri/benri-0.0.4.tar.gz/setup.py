try:
    from setuptools import setup, find_packages
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
finally:
    from setuptools import setup, find_packages

setup(name='benri',
    version='0.0.4', 
    author='Mikael Hoegqvist',
    author_email='hoegqvist@zib.de',
    url='',
    download_url='',
    description='A REST-service creation framework.',
    license='',
    long_description="""Convenience framework for REST service creation. Uses
                        Paste for many basic tasks.""",
    include_package_data = True,
    packages = find_packages(),
    install_requires = [
    'benri.client >= 0.0.2',
    'Paste>=1.7.5.1',
    'PasteScript>=1.7.2',
    'selector>=0.8.11',
    ],    
#    benri_erlang=benri.templates:ErlangTemplate
    entry_points = """
    [paste.paster_create_template]
    benri=benri.templates:BenriTemplate
    """,
     classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
    )

