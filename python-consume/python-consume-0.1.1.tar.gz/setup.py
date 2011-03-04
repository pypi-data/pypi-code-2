from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(
    name='python-consume',
    version=version,
    packages=['consume',],
    package_dir={'': 'src'},
    package_data={
        'consume': [
            'input_data/*.xml',
            'tests/test*.py',
            'examples/*',
        ],
    },
    install_requires=[
        'setuptools',
        'numpy',
    ],
    description="Python port of Consume, a software program developed by the USFS that calculates consumption and emissions from wildland fires",
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='kml',
    author='Michael Billmire',
    author_email='mgbillmi@mtu.edu',
    url='http://pypi.python.org/pypi/python-consume',
    license='BSD',
    long_description="""\
==============
Python-Consume
==============
Python-Consume is a Python package that is a port of Consume 3.0, a software 
program developed by the USFS that calculates consumption and emissions from 
wildland fires.

Consume 3.0 was developed and designed originally in Java by US Forest 
Service Fire and Environmental Research Applications (FERA) team.

This is a recoded version (2010) developed by Michigan Tech Research
Institute (MTRI) in consultation with FERA.  This version was developed
for use in MTRI's Wildfire Emissions Information System (WFEIS) 
(wfeis.mtri.org), but was also designed to include more user-friendly
shell-based analysis options.

During the recoding process, several errors were identified in the original
Consume 3.0 source code, but were fixed (via consultation with original
developers Roger Ottmar and Susan Prichard) for this version. For this reason,
results from this version will not always align with results from the official
Consume 3.0 GUI version of the software. Notable errors include:

1. incorrect calculation of 'duff' reduction (p. 182 in the Consume 3.0)
2. a bug that interchanges 'squirrel midden' density and radius when FCCS
   values are loaded
3. a typo that incorrectly calculates pm2.5 emissions from 'canopy'
   consumption (thus influencing total pm2.5 emissions values as well)

*For users familiar with the original Consume 3.0 GUI software, see the 
notes section below for functionality and operational differences between
this version and the original.*

References:

* CONSUME: http://www.fs.fed.us/pnw/fera/research/smoke/consume/index.shtml
* FCCS: http://www.fs.fed.us/pnw/fera/fccs/
* FERA: http://www.fs.fed.us/pnw/fera/F
* MTRI: http://www.mtri.org

Requirements:

* Python 2.4 or above (free from http://www.python.org)
* numpy package (free from http://np.scipy.org/)

For questions/comments, contact:

* Michael G. Billmire mgbillmi@mtu.edu
* Tyler A. Erickson taericks@mtu.edu

------------
Dependencies
------------
* Python 2.4 or above 
* python-numpy (free from http://np.scipy.org/)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Notes for users familiar with the original Consume 3.0 GUI software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* This version relies entirely on FCCS fuelbed data and does NOT use SAF/SRM
  cover type data except in the background for selecting the correct emissions
  factor groups to use from a link table provided by FERA.
* *Heat release* output is coupled with consumption outputs.
* Instead of selecting a specific ecoregion from Bailey's set, this version only
  requires the user to specify whether the fuelbed is located in *western*, 
  *boreal*, or *southern* regions. See the original Consume 3.0 User's Manual
  to view which Bailey's ecoregions fit into these broader categories. 

------------
Installation
------------
Python-Consume can be installed from the Python Package Index, using either 
easy_install or pip:

  $ sudo easy_install python-consume

or

  $ sudo pip install python-consume

The installation can be tested by running the following:

  $ nosetests -s --with-coverage

-------------------------------------------
Usage
-------------------------------------------

(See next section for a complete, uninterrupted example...)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Getting Started with the Fuel Consumption Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open a Python shell program (e.g. IDLE, ipython, etc.).
Import the module:

>>> from consume import consume

Declare a Consume FuelConsumption object:

>>> fc_obj = consume.FuelConsumption()


*Note: if the .xml fuel loading database is located somewhere other than
the default location, user can specify this using the 'fccs_file' argument,
e.g.:
fc_obj = consume.FuelConsumption(fccs_file="C:/Documents/FCCSLoadings.xml")*

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SETTING INPUT PARAMETERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a number of alternative options for setting input values:

1.  Start a program that will prompt the user for inputs:
    >>> fc_obj.prompt_for_inputs()

2.  Load inputs from a pre-formatted csv file (see example file:
    "consume_inputs_example.csv" for correct formatting):
    
    >>> fc_obj.load_scenario("myscenario.csv")
    
    OR to load, calculate outputs, and store outputs at once, use the
    batch_process method:
    
    >>> fc_obj.batch_process("myscenario.csv", "myoutputs.csv")

3.  Individually set/change input values manually:
    
    >>> fc_obj.burn_type = <'natural' or 'activity'>
    >>> fc_obj.fuelbed_fccs_ids = [FCCSID#1,FCCSID#2,...]
    >>> fc_obj.fuelbed_area_acres = [AREA#1,AREA#2,...]
    >>> fc_obj.fuelbed_ecoregion = [ECOREGION#1, ECOREGION#2,...]
    >>> fc_obj.fuel_moisture_1000hr_pct = [1000hrFM#1, 1000hrFM#2,...]
    >>> fc_obj.fuel_moisture_duff_pct = [DuffFM#1, DuffFM#2, ...]
    >>> fc_obj.canopy_consumption_pct = [PctCan#1, PctCan#2,...]
    >>> fc_obj.shrub_blackened_pct = [PercentShrub#1, PercentShrub#2,...]

    inputs specific to 'activity' burns:
    
    >>> fc_obj.fuel_moisture_10hr_pct = [10HourFM#1, 10HourFM#2, ...]
    >>> fc_obj.slope = [Slope#1, Slope#2, ...]
    >>> fc_obj.windspeed = [Windspeed#1, Windspeed#2, ...]
    >>> fc_obj.fm_type = <'MEAS-Th', 'ADJ-Th', or 'NFDRS-Th'>
    >>> fc_obj.days_since_rain = [Days#1, Days#2, ...]
    >>> fc_obj.lengthOfIgnition = [Length#1, Length#2, ...]


    *Note: When setting input values, the user can also select a SINGLE 
    value (instead of a list) for any environment variable that will 
    apply to the entire scenario.
    These environment variables include the following:
    ecoregion, fuel_moisture_1000hr_pct,  fuel_moisture_duff_pct, 
    canopy_consumption_pct, shrub_blackened_pct, slope, windpseed, 
    fm_type, days_since_rain, lengthOfIgnition*

Description of the input parameters:

burn_type
    Use this variable to select 'natural' burn equations or 
    'activity' (i.e. prescribed) burn equations. Note that
    'activity' burns require 6 additional input parameters:
    10hr fuel moisture, slope, windpseed, fuel moisture type,
    days since significant rainfall, and length of ignition.
    
fuelbed_fccs_ids
    a list of Fuel Characteristic Classification System (FCCS)
    (http://www.fs.fed.us/pnw/fera/fccs/index.shtml) fuelbed ID
    numbers (1-291).  Use the .FCCS.browse() method to load a list
    of all FCCS ID#'s and their associated site names. Use 
    .FCCS.info(id#) to get a site description of the
    specified FCCD ID number. To get a complete listing of fuel
    loadings for an FCCS fuelbed, use: 
    .FCCS.info(id#, detail=True)

fuelbed_area_acres
    a list (or single number to be used for all fuelbeds) of
    numbers in acres that represents area for the corresponding
    FCCS fuelbed ID listed in the 'fuelbeds_fccs_ids' variable.

fuelbed_ecoregion
    a list (or single region to be used for all fuelbeds) of
    ecoregions ('western', 'southern', or 'boreal') that
    represent the ecoregion for the corresponding FCCS fuelbed ID
    listed in the 'fuelbeds_fccs_ids' variable. Regions within the
    US that correspond to each broad regional description can be
    found in the official Consume 3.0 User's Guide, p. 60. Further
    info on Bailey's ecoregions can be found here:
    www.eoearth.org/article/Ecoregions_of_the_United_States_(Bailey)
    Default is 'western'

fuel_moisture_1000hr_pct
    1000-hr fuel moisture in the form of a number or list of
    numbers ranging from 0-100 representing a percentage.
    Default is 50%

fuel_moisture_10hr_pct
    <specific to 'activity' burns>
    10-hr fuel moisture in the form of a number or list of
    numbers ranging from 0-100 representing a percentage.
    Default is 50%

fuel_moisture_duff_pct
    Duff fuel moisture. A number or list of numbers ranging from
    0-100 representing a percentage.
    Default is 50%.

canopy_consumption_pct
    Percent canopy consumed. A number or list of numbers ranging
    from 0-100 representing a percentage. Set to '-1' to
    use an FCCS-fuelbed dependent precalculated canopy consumption
    percentage based on crown fire initiation potential, crown to
    crown transmissivity, and crown fire spreading potential.
    (note: auto-calc is not available for FCCS ID's 401-456)
    Default is -1

shrub_blackened_pct
    Percent of shrub that has been blackened. A number or list
    of numbers ranging from 0-100 representing a percentage.
    Default is 50%

slope
    <specific to 'activity' burns>
    Percent slope of a fuelbed unit. Used in predicting 100-hr
    (1-3" diameter) fuel consumption in 'activity' fuelbeds.
    Valid values: a number or list of numbers ranging from 0-100
    representing a percentage.
    Default is 5%

windspeed
    <specific to 'activity' burns>
    Mid-flame wind speed (mph) during the burn. Maximum is 35 mph.
    Used in predicting 100-hr (1-3" diameter) fuel consumption in 
    'activity' fuelbeds.
    Default is 5 mph

fm_type
    <specific to 'activity' burns>
    Source of 1000-hr fuel moisture data.
        
        * "Meas-Th" (default) : measured directly
        * "NFDRS-Th" : calculated from NFDRS
        * "ADJ-Th" : adjusted for PNW conifer types
    
    Note: 1000-hr fuel moisture is NOT calculated by Consume, 
    i.e. user must derive 1000-hr fuel moisture & simply select
    the method used.

days_since_rain
    <specific to 'activity' burns>
    Number of days since significant rainfall. According to the
    Consume 3.0 User's Guide, "Significant rainfall is one-quarter
    inch in a 48-hour period." Used to predict duff consumption
    in 'activity' fuelbeds.

lengthOfIgnition
    <specific to 'activity' burns>
    The amount of time (minutes) it will take to ignite the area
    to be burned. Used to determine if a fire will be of high 
    intensity, which affects diameter reduction of large woody
    fuels in 'activity' fuelbeds.

The user can also optionally set alternate output units. Use the
list_valid_units() method to view output unit options.
Default fuel consumption units are tons/acre ('tons_ac').

>>> consume.list_valid_units()

Output::

    ['lbs',
     'lbs_ac',
     'tons',
     'tons_ac',
     'kg',
     'kg_m^2',
     'kg_ha',
     'kg_km^2'
     'tonnes',
     'tonnes_ha',
     'tonnes_km^2']


>>> fc_obj.output_units = 'lbs'

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CUSTOMIZING FUEL LOADINGS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fuel loadings are automatically imported from the FCCS database based on the
FCCS fuelbed ID#s selected by the user. If desired, the user can also 
customize FCCS fuel loadings by setting the '.customized_fuel_loadings' variable
to a list of 3 value lists in this format:
[fuelbed index number {interger}, fuel stratum {string}, loading value {number}]

e.g.:

>>> fc_obj.customized_fuel_loadings = [[1, 'overstory', 4.5],[2, 'shrub_prim', 5]]

The above command will change the canopy 'overstory' loading in the first ('1')
fuelbed to 4.5 (tons/acre) and will change the 'shrub_prim' (primary shrub
loading) in the second ('2') fuelbed to 5 tons/acre. To view all valid stratum
names and units, use the fc_obj.FCCS.list_fuel_loading_names() method.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OUTPUTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consumption outputs can be accessed by calling the .results(), .report(), or
.batch_process() methods. Calling any of these methods will trigger the 
calculation of all fuel consumption equation and will return the results in 
a variety of different formats:


>>> fc_obj.results()

... generates & prints a python DICTIONARY of consumption
results by fuel category (major and minor categories)
See complete example below to see how individual
data categories can be accessed from this dictionary.

>>> fc_obj.report(csv="")

...prints a TABULAR REPORT of consumption results for
the major fuel categories (similar to the "Fuel
Consumption by Combustion Stage" report produced by the
official Consume 3.0 GUI program).  To export a version 
of this report as a CSV FILE, use the 'csv' argument to 
specify a file name, e.g.:
>>> fc_obj.report(csv = "consumption_report.csv")

>>> fc_obj.batch_process(csvin="", csvout="")

...similar to the .report() method, although requires an
input csv file and will export results to the specified
CSV output.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTHER USEFUL METHODS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> consume.list_valid_units()        

...displays a list of valid output unit options

>>> consume.list_valid_consumption_strata()

...displays a list of valid consumption strata group names

>>> fc_obj.list_variable_names()

...displays a list of the variable names used for each input parameter

>>> fc_obj.FCCS.browse()

...loads a list of all FCCS fuelbed ID numbers and their site names

>>> fc_obj.FCCS.info(#)

...provides site description of the FCCS fuelbed with the specified ID number. 
Set detail=True to print out detailed fuel loading information

>>> fc_obj.FCCS.get_canopy_pct(#)

...displays estimated canopy consumption percent as calculated by MTRI for the 
specified FCCS ID number. This is the  value that will be used if 
canopy_consumption_pct is set to -1.

>>> fc_obj.load_example()

...loads an example scenario with 2 Fuelbeds

>>> fc_obj.reset_inputs_and_outputs()

...clears input and output parameters

>>> fc_obj.display_inputs()

...displays a list of the input parameters.
Useful for checking that scenario parameters were set correctly


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Working with the EMISSIONS Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For emissions data, declare a Consume Emissions object by nesting in the
FuelConsumption object we were working on above as the only required argument.

>>> e_obj = consume.Emissions(fc_obj)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SETTING INPUT PARAMETERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input parameters for emissions calculations are much easier to set than those
for FuelConsumption, as they are ALL ultimately automatically derived from the
parameters set within the nested FuelConsumption object.
The input parameters required for the emissions calculations are as follows:

*  FUEL CONSUMPTION (tons/ac) & the scenario of corresponding FCCS ID#s,
   AREAS, and ECOREGIONS, all of which is derived from the FuelConsumption
   object specified in the Emissions object declaration we just did

*  EMISSIONS FACTOR GROUP ('efg'), which specifies the appropriate set of
   emissions factors (lbs/tons consumed for each of 7 emissions species) 
   to use for the scenario. This is automatically selected based on the 
   FCCS fuelbeds in the consumption scenario, but the user can override
   the auto-select process if desired as described below.

As with the FuelConsumption object, the user can also optionally set alternate 
output units for the Emissions object. Use the consume.list_valid_units() method
to view output unit options.
Default output units for emissions are lbs/ac.

>>> e_obj.output_units = 'kg_ha'

To change the FuelConsumption units, simply modify the units of the FC object
that is nested within the Emissions object:

>>> e_obj.FCobj.output_units = 'kg_ha'


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OUTPUTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with the FuelConsumption object, Emissions outputs can be accessed by 
calling the .results() or .report() methods. Calling either methods will trigger
the calculation of emissions and output results in a variety of different
formats:

>>> e_obj.results()

...generates a python DICTIONARY similar to the one created
by the FuelConsumption object, but with Emissions
results added (consumption data is also included).
See complete example below to see how specific
data categories can be accessed in this dictionary.

>>> e_obj.report()

...prints a TABULAR REPORT of emissions results for all
pollutants and combustion stages (similar to the
"Emissions by Combustion Stage" report produced in 
the official Consume 3.0 GUI program).  To export
a version of this report as a CSV FILE, use the
'csv' argument to specify a file name, e.g.:
>>> e_obj.report(csv = "emissions_report.csv")


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTHER USEFUL METHODS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> e_obj.display_inputs()

...displays a list of the input parameters.
Useful for checking that scenario
parameters were set correctly

>>> e_obj.efDB.browse()

...displays a list of all emissions factor
groups and their associated fuel types
and references

>>> e_obj.efDB.info(#)

...display detailed information about the
specified emissions factor group ID#
(use the .browse() method above to view
ID#s). Includes the actual emissions
factor values.

For further help on specific methods or properties,
type "help([CONSUME METHOD])" within a python shell, e.g.:

>>> help(fc_obj.FCCS.info)

Output::

  Help on method info in module consume_obj:
  
  info(self, fccs_id, detail=False) method of consume_obj.FCCSDB instance
      Display an FCCS fuelbed description.
      
      Prints fuel loading information on the fuelbed with the specified
      FCCS ID. Requires one argument: an integer refering to a specific FCCS
      ID. For a list of valid FCCS IDs, use the .browse() method."


-------------------------------------------
Complete Uninterrupted Example
-------------------------------------------

The following example sets up a 'natural' burn scenario in which 100 acres FCCS 
fuelbed ID #1 ("Black cottonwood - Douglas fir - Quaking aspen riparian forest")
and 200 acres of FCCS fuelbed ID #47 ("Redwood - Tanoak forest") are consumed.
1000-hr and duff fuel moisture is set at 50% for fuelbed ID #1 and 40% for
fuelbed ID #47. Canopy consumption and shrub percent black is set at 25% for
both fuelbeds.

>>> from consume import consume
>>> fc_obj = consume.FuelConsumption()
>>> fc_obj.fuelbed_fccs_ids = [1, 47]
>>> fc_obj.fuelbed_area_acres = [100, 200]
>>> fc_obj.fuelbed_ecoregion = 'western'
>>> fc_obj.fuel_moisture_1000hr_pct = [50, 40]
>>> fc_obj.fuel_moisture_duff_pct = [50, 40]
>>> fc_obj.canopy_consumption_pct = 25
>>> fc_obj.shrub_blackened_pct = 25
>>> fc_obj.output_units = 'kg_ha'
>>> fc_obj.display_inputs()

Output::

  Current scenario parameters:
  
  Parameter                   Value(s)
  --------------------------------------------------------------
  Burn type                   natural
  FCCS fuelbeds (ID#)         [1, 47]
  Fuelbed area (acres)        [100, 200]
  Fuelbed ecoregion           western
  Fuel moisture (1000-hr, %)  [50, 40]
  Fuel moisture (duff, %)     [50, 40]
  Canopy consumption (%)      25
  Shrub blackened (%)         25
  Output units                kg_ha


>>> fc_obj.report()

Output::

    FUEL CONSUMPTION
    Consumption units: kg/ha
    Heat release units: btu/ha
    Total area: 300 acres

    FCCS ID: 1
    Area:    100
    Ecoregion: western
    CATEGORY        Flaming     Smoldering  Residual    TOTAL
    canopy          1.25e+04    9.58e+02    1.51e+02    1.36e+04
    shrub           1.26e+03    6.97e+01    0.00e+00    1.33e+03
    nonwoody        3.95e+02    2.08e+01    0.00e+00    4.16e+02
    llm             2.32e+03    2.20e+02    0.00e+00    2.54e+03
    ground fuels    8.97e+02    1.51e+04    3.72e+04    5.32e+04
    woody fuels     9.71e+03    5.61e+03    8.81e+03    2.41e+04
    TOTAL:          2.70e+04    2.20e+04    4.61e+04    9.52e+04

    Heat release:   1.19e+08    9.70e+07    2.03e+08    4.20e+08


    FCCS ID: 47
    Area:    200
    Ecoregion: western
    CATEGORY        Flaming     Smoldering  Residual    TOTAL
    canopy          7.93e+03    2.48e+03    2.05e+03    1.25e+04
    shrub           3.87e+03    2.69e+02    0.00e+00    4.13e+03
    nonwoody        9.88e+02    5.20e+01    0.00e+00    1.04e+03
    llm             4.93e+03    5.41e+02    0.00e+00    5.47e+03
    ground fuels    3.59e+03    4.08e+04    6.98e+04    1.14e+05
    woody fuels     2.56e+04    2.06e+04    2.49e+04    7.11e+04
    TOTAL:          4.69e+04    6.47e+04    9.67e+04    2.08e+05

    Heat release:    2.07e+08    2.85e+08    4.27e+08    9.18e+08


    ALL FUELBEDS:

    Consumption:    4.03e+04    5.04e+04    7.99e+04    1.71e+05
    Heat release:   3.26e+08    3.82e+08    6.30e+08    1.34e+09



>>> fc_obj.results()['consumption']['ground fuels']

Output::

    {'basal accumulations': {'flaming': array([-0.,  0.]),
                             'residual': array([-0.,  0.]),
                             'smoldering': array([-0.,  0.]),
                             'total': array([-0.,  0.])},
     'duff, lower': {'flaming': array([ 0.,  0.]),
                     'residual': array([ 35377.20573062,  62608.52081126]),
                     'smoldering': array([  8844.30143266,  15652.13020281]),
                     'total': array([ 44221.50716328,  78260.65101407])},
     'duff, upper': {'flaming': array([  896.68092549,  3586.72370195]),
                     'residual': array([ 1793.36185097,  7173.4474039 ]),
                     'smoldering': array([  6276.76647841,  25107.06591365]),
                     'total': array([  8966.80925487,  35867.23701949])},
     'squirrel middens': {'flaming': array([ 0.,  0.]),
                          'residual': array([ 0.,  0.]),
                          'smoldering': array([ 0.,  0.]),
                          'total': array([ 0.,  0.])}}


>>> e_obj = consume.Emissions(fc_obj)
>>> e_obj.display_inputs()

Output::

    CONSUMPTION

    Current scenario parameters:

    Parameter                    Value(s)
    --------------------------------------------------------------
    Burn type                    ['natural']
    FCCS fuelbeds (ID#)          [1, 47]
    Fuelbed area (acres)         [ 100.  200.]
    Fuelbed ecoregion            ['western']
    Fuel moisture (1000-hr, %)   [ 50.  40.]
    Fuel moisture (duff, %)      [ 50.  40.]
    Canopy consumption (%)       [ 25.]
    Shrub blackened (%)          [ 25.]
    Output units                 ['kg_ha']

    EMISSIONS

    Current scenario parameters:

    Parameter            Value(s)
    --------------------------------------------------------------

>>> e_obj.report()

Output::

    EMISSIONS
    Units: lbs_ac

    FCCS ID: 1
    Area:    100 ac. (40.5 ha)
    Emissions factor group: 2
    SPECIES Flaming     Smoldering  Residual    TOTAL
    pm      2.77e+02    3.73e+02    7.82e+02    1.43e+03
    pm10    1.69e+02    2.54e+02    5.33e+02    9.56e+02
    pm2.5   1.47e+02    2.30e+02    4.82e+02    8.58e+02
    co      1.11e+03    3.59e+03    7.53e+03    1.22e+04
    co2     4.09e+04    2.80e+04    5.87e+04    1.28e+05
    ch4     5.31e+01    1.92e+02    4.03e+02    6.49e+02
    nmhc    6.27e+01    1.37e+02    2.88e+02    4.88e+02

    FCCS ID: 47
    Area:    200 ac. (80.9 ha)
    Emissions factor group: 4
    SPECIES Flaming     Smoldering  Residual    TOTAL
    pm      4.60e+02    9.69e+02    1.45e+03    2.88e+03
    pm10    2.45e+02    7.30e+02    1.09e+03    2.07e+03
    pm2.5   2.01e+02    6.81e+02    1.02e+03    1.90e+03
    co      1.11e+03    7.87e+03    1.18e+04    2.08e+04
    co2     7.24e+04    8.72e+04    1.30e+05    2.90e+05
    ch4     6.28e+01    5.08e+02    7.60e+02    1.33e+03
    nmhc    6.70e+01    3.81e+02    5.70e+02    1.02e+03

    ALL FUELBEDS:
    Units: lbs_ac
    Total area: 300 ac. (121.4 ha)
    pm      3.99e+02    7.70e+02    1.23e+03    2.40e+03
    pm10    9.45e+01    3.02e+01    2.14e+01    1.46e+02
    pm2.5   2.96e+01    3.08e+00    0.00e+00    3.27e+01
    co      7.81e+00    6.37e-01    0.00e+00    8.45e+00
    co2     4.02e+01    6.65e+00    0.00e+00    4.68e+01
    ch4     2.65e+01    4.93e+02    9.07e+02    1.43e+03
    nmhc    2.01e+02    2.37e+02    2.99e+02    7.36e+02


>>> e_obj.results()['emissions']['co2']

Output::

    {'flaming': array([ 40877.14600611,  72354.16061005]),
     'residual': array([  58664.90328723,  130457.66209735]),
     'smoldering': array([ 27980.07467362,  87193.41115534]),
     'total': array([ 127522.12396695,  290005.23386274])}



-------------------------------------------
Navigating the .results() dictionaries
-------------------------------------------

The table below depicts all categories included in the .results() dictionaries
that are produced from the FuelConsumption and Emissions objects. Note that the
FuelConsumption .results() dictionary does NOT include emissions data while the
Emissions .results() dictionary includes BOTH consumption and emissions data.

The FINAL index in the dictionary will be always be an integer that indicates
the fuelbed unit in the scenario. In the example above, a [0] would access 
data for the first fuelbed (FCCS ID #1) and a [1] would access data for the 
second fuelbed (FCCS ID #47). Use Python's built-in 'sum()' function to
calculate total consumption/emissions across ALL fuelbeds.


~~~~~~~~~~~~~
Examples
~~~~~~~~~~~~~

To access TOTAL consumption for the given scenario for each fuelbed unit:

>>> fc_obj.results()['consumption']['summary']['total']['total']

To access TOTAL consumption for only the first fuelbed unit in the scenario:

>>> fc_obj.results()['consumption']['summary']['total']['total'][0]

To access TOTAL consumption for the given scenario across ALL fuelbeds*:

>>> sum(fc_obj.results()['consumption']['summary']['total']['total'])

To access consumption data for all canopy strata:

>>> fc_obj.results()['consumption']['canopy']

To access TOTAL canopy consumption:

>>> fc_obj.results()['consumption']['summary']['canopy']['total']

To access 'co2' emissions from all combustion stages:

>>> e_obj.results()['emissions']['co2']

To access total 'co2' emissions for the given scenario across ALL fuelbeds*:

>>> sum(e_obj.results()['emissions']['co2']['total'])

To view units that the emissions data are in:

>>> e_obj.results()['parameters']['units_emissions']

    *Note: if outputs units are per-area units (i.e. tons/acre or kg/ha), these 
    sum' functions will not provide an accurate representation of the overall
    consumption rate for the scenario.*

Output::

    Index 1           Index 2              Index 3                     Index 4       Index 5    
    -----------------------------------------------------------------------------------------------------------------------------

    'parameters'   'fuel moisture: 1000hr'
                   'fuel moisture duff'
                   'fuel moisture pct canopy consumed'
                   'fuel moisture pct shrub blackened'
                   'fuelbed area'
                   'fuelbed ecoregion'
                   'fuelbed fccs id'
                   'units consumption'
                   'units emissions'
    -----------------------------------------------------------------------------------------------------------------------------
                         
    'emissions'    'ch4'                'flaming','smoldering','residual', or 'total'
                   'co'                 'flaming','smoldering','residual', or 'total'
                   'co2'                'flaming','smoldering','residual', or 'total'
                   'nmhc'               'flaming','smoldering','residual', or 'total'
                   'pm'                 'flaming','smoldering','residual', or 'total'
                   'pm10'               'flaming','smoldering','residual', or 'total'
                   'pm25'               'flaming','smoldering','residual', or 'total'
                   
                   'stratum'            'ch4'                       'canopy'             'flaming','smoldering','residual', or 'total
                                                                    'ground fuels'       ''
                                                                    'litter-lichen-moss' ''
                                                                    'nonwoody'           ''
                                                                    'shrub'              ''
                                                                    'woody fuels'        ''
                                        'co'                        'canopy'             ''
                                                                    'ground fuels'       ''
                                                                    'litter-lichen-moss' ''
                                                                    'nonwoody'           ''
                                                                    'shrub'              ''
                                                                    'woody fuels'        ''
                                        'co2'   .....etc.....
                                                

    -----------------------------------------------------------------------------------------------------------------------------
                         
    'heat release' 'flaming'
                   'smoldering'
                   'residual'
                   'total'

    -----------------------------------------------------------------------------------------------------------------------------

    'consumption'  'summary'            'total'                     'flaming','smoldering','residual', or 'total'
                                        'canopy'                    'flaming','smoldering','residual', or 'total'
                                        'ground fuels'              'flaming','smoldering','residual', or 'total'
                                        'litter-lichen-moss'        'flaming','smoldering','residual', or 'total'
                                        'nonwoody'                  'flaming','smoldering','residual', or 'total'
                                        'shrub'                     'flaming','smoldering','residual', or 'total'
                                        'woody fuels'               'flaming','smoldering','residual', or 'total

                   'canopy'             'overstory'                 'flaming','smoldering','residual', or 'total'
                                        'midstory'                  'flaming','smoldering','residual', or 'total'
                                        'understory'                'flaming','smoldering','residual', or 'total'
                                        'ladder fuels'              'flaming','smoldering','residual', or 'total'
                                        'snags class 1 foliage'     'flaming','smoldering','residual', or 'total'
                                        'snags class 1 non foliage' 'flaming','smoldering','residual', or 'total'
                                        'snags class 1 wood'        'flaming','smoldering','residual', or 'total'
                                        'snags class 2'             'flaming','smoldering','residual', or 'total'
                                        'snags class 3'             'flaming','smoldering','residual', or 'total'
        
                   'ground fuels'       'duff upper'                'flaming','smoldering','residual', or 'total'
                                        'duff lower'                'flaming','smoldering','residual', or 'total'
                                        'basal accumulations'       'flaming','smoldering','residual', or 'total'
                                        'squirrel middens'          'flaming','smoldering','residual', or 'total'

                   'litter-lichen-moss' 'litter'                    'flaming','smoldering','residual', or 'total'
                                        'lichen'                    'flaming','smoldering','residual', or 'total'
                                        'moss'                      'flaming','smoldering','residual', or 'total'
                   'nonwoody'           'primary dead'              'flaming','smoldering','residual', or 'total'
                                        'primary live'              'flaming','smoldering','residual', or 'total'
                                        'secondary dead'            'flaming','smoldering','residual', or 'total'
                                        'secondary live'            'flaming','smoldering','residual', or 'total'

                   'shrub'              'primary dead'              'flaming','smoldering','residual', or 'total'
                                        'primary live'              'flaming','smoldering','residual', or 'total'
                                        'secondary dead'            'flaming','smoldering','residual', or 'total'
                                        'secondary live'            'flaming','smoldering','residual', or 'total'
                   'woody fuels'        '1-hr fuels'                'flaming','smoldering','residual', or 'total'
                                        '10-hr fuels'               'flaming','smoldering','residual', or 'total'
                                        '100-hr fuels'              'flaming','smoldering','residual', or 'total'
                                        '1000-hr fuels sound'       'flaming','smoldering','residual', or 'total'
                                        '1000-hr fuels rotten'      'flaming','smoldering','residual', or 'total'
                                        '10000-hr fuels sound'      'flaming','smoldering','residual', or 'total'
                                        '10000-hr fuels rotten'     'flaming','smoldering','residual', or 'total'
                                        '10k+-hr fuels sound'       'flaming','smoldering','residual', or 'total'
                                        '10k+-hr fuels rotten'      'flaming','smoldering','residual', or 'total'
                                        'stumps sound'              'flaming','smoldering','residual', or 'total'
                                        'stumps rotten'             'flaming','smoldering','residual', or 'total'
                                        'stumps lightered'          'flaming','smoldering','residual', or 'total'
    -----------------------------------------------------------------------------------------------------------------------------

""",
)
