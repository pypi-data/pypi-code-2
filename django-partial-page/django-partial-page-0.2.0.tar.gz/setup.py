from setuptools import setup


setup(
    name='django-partial-page',
    version='0.2.0',
    url='https://bitbucket.org/siberiano/django-partial-page/',
    license='Public Domain',
    author='Dmitri Lebedev',
    author_email='detail@ngs.ru',
    description="""Middleware that extracts {% block-s %} from pages and sends them as JSON. This allows the clients update parts of the pages, which is useful for Ajax apps and sites using History.PushState.
    
    If /mypage/ has {% block main_content %} in the template, make a request /mypage/?partial=main_content, and you'll receive a JSON: {"main_content": "..."}.
    """,
    include_package_data=True,
    zip_safe=False,
    package_dir={'': '.'},
    packages=['django_partial_page']
)
