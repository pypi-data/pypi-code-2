from distutils.core import setup

VERSION='0.7'

DESCRIPTION="Utilities useful for writing django views."

setup(name="django-viewutil",
      url="http://bitbucket.org/smulloni/django-viewutil/",
      version=VERSION,
      description=DESCRIPTION,
      author="Jacob Smullyan",
      author_email="smulloni@smullyan.org",
      license='BSD',
      classifiers=['Framework :: Django',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Utilities'],
      packages=['djview'])
      
