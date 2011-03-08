from setuptools import setup, find_packages
setup(
      name='pylaf',
      version='0.3.1',
      package_dir={'pylaf' : 'src/pylaf', 'pylaf.utils' : 'src/pylaf/utils', 'pylaf.utils.core' : 'src/pylaf/utils/core', 'pylaf.utils.gui' : 'src/pylaf/utils/gui', 'pylaf.utils.mpl' : 'src/pylaf/utils/mpl'},
      packages=['pylaf','pylaf.utils','pylaf.utils.core','pylaf.utils.gui','pylaf.utils.mpl'],
      classifiers=[
                   'Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                   ],
      description='Python Laboratory Application Framework',
      long_description='''\
      Python Laboratory Application Framework is a package for development applications.
      
      Requirements
      ------------
      * Python 2.4 or later (not support 3.x)
      
      Features
      --------
      * Renewal all codes
      '''
      ,
      keywords=['framework',],
      author='Hidehisa Shiomi',
      author_email='pylaf@users.sourceforge.jp',
      url='http://pylaf.sourceforge.jp',
      license='BSD',
      )
