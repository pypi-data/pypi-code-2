"""
Flask-YAMLConfig
----------------

Usage:

    from flaskext.yamlconfig import install_yaml_config
    install_yaml_config(app)
    
    or 
    
    from flaskext.yamlconfig import install_yaml_config
    from flaskext.yamlconfig import AppYAMLConfigure
    
    class MyConfig(AppYAMLConfigure):
        def configure_mysection(self, content):
            for item in content:
                ....

"""

from setuptools import setup
import sys
requires = ['Flask>=0.6', 'PyYAML']
if sys.version_info < (2, 6):
    requires.append('simplejson')

setup(
    name='Flask-YAMLConfig',
    version='0.0.1',
    license='MIT',
    author='Eugene Sazonov aka zheromo',
    author_email='zheromo@gmail.com',
    description='YAML configurator for Flask app.',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
