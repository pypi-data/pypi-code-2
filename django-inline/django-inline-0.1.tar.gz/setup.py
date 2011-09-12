from setuptools import setup, find_packages

setup(
    name='django-inline',
    version='0.1',
    license='GNU Lesser GPL',
    url='https://bitbucket.org/siberiano/django-inline/',
    author='Dmitri Lebedev',
    author_email='detail@ngs.ru',
    description="""
    The Django backend for jeditable (http://www.appelsiini.net/projects/jeditable)
    """,
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'example'},
    packages=find_packages('example', exclude=('*.pyc', '*~'))
)
