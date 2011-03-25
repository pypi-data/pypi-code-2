from distutils.core import setup
import os

readme_file = os.path.join(os.path.dirname(__file__),
                           'README')
long_description = open(readme_file).read()    
setup(name='django-emailform',
      version='0.1.6',
      description='django-email forms is an application for generating multi input forms, customized using the django admin, with emailing of entries to a supplied list of email addresses.',
      long_description=long_description,
      author='Glenn Mohre',
      author_email='glenn.mohre@gmail.com',
      url='http://www.bitbucket.org/glennmohre/django-emailform',
      packages=['emailform'],
      license='MIT',
     )
