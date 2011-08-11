from setuptools import setup, find_packages

setup(
    name='django-partial-page',
    version='0.4.1',
    url='https://bitbucket.org/siberiano/django-partial-page/',
    license='Public Domain',
    author='Dmitri Lebedev',
    author_email='detail@ngs.ru',
    description="""Middleware that extracts {% block-s %} from pages and sends them as JSON. This allows the clients update parts of the pages, which is useful for Ajax apps and sites using History.PushState.
    
    If /mypage/ has {% block main_content %} in the template, make a request /mypage/?partial=main_content, and you'll receive a JSON: {"main_content": "..."}.
    
    The example Django project in the BitBucket contains a working JavaScript module that handles these requests and does something more.
    """,
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'example'},
    packages=find_packages('example', exclude=('*.pyc', '*~'))
)
