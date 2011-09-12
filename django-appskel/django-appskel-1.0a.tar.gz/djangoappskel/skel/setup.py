from setuptools import setup, find_packages
import os
import {{ module }}

CLASSIFIERS=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Framework :: Django'
]

setup(
    name='{{ egg }}',
    version={{ module }}.get_version(),
    description='{{ description }}',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.{{ readme_ext }}')).read(),
    author='{{ author }}',
    author_email='{{ email }}',
    url='{{ url }}',
    packages=find_packages(),
    classifiers = CLASSIFIERS,
    test_suite = "{{ module }}.test.run_tests.run_tests",
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
