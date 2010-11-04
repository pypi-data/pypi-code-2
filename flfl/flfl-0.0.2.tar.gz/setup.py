from distutils.core import setup
import flfl

try:
    import ply
except ImportError:
    print "flfl requires PLY"

setup(name='flfl',
      author=flfl.__author__,
      author_email='takada-at@klab.jp',
      version=flfl.__version__,
      description='A Compiler for FlashLite 1.0/1.1',
      long_description=flfl.__doc__,
      scripts=['scripts/flfl'],
      packages=['flfl'],
      package_data={'flfl': ['flfl.cfg']},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Compilers'
          ]
      )
