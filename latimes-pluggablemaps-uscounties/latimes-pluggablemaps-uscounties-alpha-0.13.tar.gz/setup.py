from setuptools import setup, find_packages

setup(name='latimes-pluggablemaps-uscounties',
      version='alpha-0.13',
      description='L.A. Times Pluggable Maps: U.S. Counties',
      author='Ben Welsh',
      author_email='ben.welsh@gmail.com',
      url='http://github.com/datadesk/latimes-pluggablemaps-uscounties',
      download_url='http://github.com/datadesk/latimes-pluggablemaps-uscounties.git',
      packages=find_packages(),
      data_files=[
        ('us_counties', [
            'us_counties/data/fips.csv',
            'us_counties/templates/base.html', 
            'us_counties/templates/county_list.json',
            'us_counties/templates/openlayers.html',
            'us_counties/templates/openlayers.js',
            'us_counties/templates/polymaps.html',
            'us_counties/templates/polymaps.js',
        ]),
      ],
      license='MIT',
      keywords='gis geographical maps earth usa counties boundaries',
      classifiers=[
       "Development Status :: 3 - Alpha",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       "Programming Language :: Python",
       "Topic :: Scientific/Engineering :: GIS",
       "Topic :: Software Development :: Libraries :: Python Modules"
       ],
     )
