import os

from setuptools import setup, find_packages

version = '1.1.2'

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__),
                             name)).read()

readme = read_file('README.txt')
changes = read_file('CHANGES.txt')

setup(name='cykooz.djangorecipe',
      version=version,
      description="Buildout recipe for Django",
      long_description='\n\n'.join([readme, changes]),
      classifiers=[
        'Framework :: Buildout',
        'Framework :: Buildout :: Recipe',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        ],
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages = ['cykooz'],
      keywords='',
      author='Cykooz',
      author_email='saikuz@mail.ru',
      url='https://bitbucket.org/cykooz/cykooz.djangorecipe',
      license='BSD',
      zip_safe=False,
      extras_require = dict(
        test = [
            'mock',
            ],
        ),
      install_requires=[
        'distribute',
        'zc.buildout',
        'zc.recipe.egg',
        'Django'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = cykooz.djangorecipe.recipe:Recipe
      """,
      )
