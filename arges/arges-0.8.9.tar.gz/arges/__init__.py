# -*- coding: latin-1 -*-

"""
===========
Arges
===========

Arges scripts are very simple and emulate a very high level language from where you call the testing/execution actions. Arges provides a set of utilities for
rapid automated testing to interact with any kind of interfaces including the web ui side (by using Selenium) and the server side / command line testing.

It supports handling parameters, which are totally separated from the scripts.

Within the test scripts you call the actions which by now, are divides into three main categories:

-Web handling. From where you can interact with any web site. Selenium 1.0.1 library is used internally.

-Command line executions. To execute any kind of command and check the return code or its output.

-Parameters handling. 


Quick installation and use
-----------------------------
Just type:

pip install arges

And you are ready to go. Arges will interpret .tcase (test case files) and 
.tsuite (test suite files) in your command line. 

This files are high level testing files which are used to launch your testing 
commands. Within the .tdata files you can put the parameters so your scripts 
could be generic. .tsuite are used to group .tcase and other .tsuite files.

The metaphor of the system is a high level interpreter of a simple "testing" 
language that a business analyst or qa guy could read without messing with 
the code. Your tests could be grouped in tcases, so in this way you will 
build reusable, testing "bricks", such as a login module. 

There is an example in the same program. For the sake of testing arges you 
can try this: 

sudo arges <your_python_dir>/dist-packages/arges/data/dummy_test_dir/dummy_app/tcase/goodbye_cruel_world.tcase 

In case you don't know, the sudo command is just to get administrative rights. 
This is so in Ubuntu and other \*nix systems.

You don't need to be administrator to run arges, but as the report file will be 
created in a "reports" directory within the .tcase dir, you will need some 
administrative rights. You could avoid this, just by copying the dummy dir to 
a home folder. Report file will contain the results of your testing.


Adding your own commands.
-----------------------------
Arges is extensible! 

Just add your own module within argestools/api with a "runCommand" method. 
You will also need to declare it in the "__all__" list of the same package, 
just by editing argestools/api/__init__.py and adding your modules's name to 
the list present within the firsts lines. 
 

Web testing.
-----------------------------
Selenium in included within the system and you could invoke its commands within 
your testing scripts. hello_world.tcase is a simple example. In order to get 
Selenium commands workingm you will need to start Selenium which is present in 
data/thirdparty/selenium-server-1.0.1

Selenium will let you send commands and get information from any web.


@author: Adrián Deccico
"""

#system constants
APP = "Arges"
VERSION = "0.8.9"

TESTCONFIG_SECTION = "arges_test_files_params"   
APPCONFIG_SECTION = "arges_test_app_params" 

LOG_FORMAT = "%(asctime)-15s-L%(levelno)s-%(message)s - %(filename)s-%(lineno)d"
