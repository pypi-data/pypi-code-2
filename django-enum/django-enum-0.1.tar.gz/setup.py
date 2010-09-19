from distutils.core import setup

VERSION='0.1'

DESCRIPTION="A utility for writing Django choice enumerations."

setup(name="django-enum",
      url="http://bitbucket.org/smulloni/django-enum/",
      version=VERSION,
      description=DESCRIPTION,
      author="Jacob Smullyan",
      author_email="smulloni@smullyan.org",
      license='BSD',
      classifiers=['Framework :: Django',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Utilities'],
      packages=['djenum'])
      
