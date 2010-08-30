import currypy
import sys
import unittest


import pypatterns.filter as FilterModule
import pomsets.definition as DefinitionModule
import pomsets.parameter as ParameterModule



# TODO:
# this is copied from TestWxApplication
# in the pomsets source code
# need to consolicate
def createShellDefinition(executable, inputParameters, parameterOrderings):
    definition = DefinitionModule.createShellProcessDefinition(
        inputParameters=inputParameters,
        parameterOrderings=parameterOrderings
    )
    definition.executable = currypy.Curry(FilterModule.FUNCTION_IDENTITY,
                                              object=executable)
    return definition


# TODO:
# this is copied from TestWxApplication
# in the pomsets source code
# need to consolicate
def createWordCountDefinition():
    
    parameterOrdering = DefinitionModule.createParameterOrderingTable()
    row = parameterOrdering.addRow()
    row.setColumn('source', 'input file')
    row.setColumn('target', 'output file')
    
    definition = createShellDefinition(
        ['/Users/mjpan/pomsets/trunk/src/test/scripts/wordcount.py'],
        {
            'input file':{
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE:True,
            },
            'output file':{
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE:True,
                ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT:True,
            }
        },
        parameterOrdering
    )
    return definition

DEFINITION_WORDCOUNT = createWordCountDefinition()

# TODO:
# this is copied from TestWxApplication
# in the pomsets source code
# need to consolicate
def createWordCountReduceDefinition():
    
    parameterOrdering = DefinitionModule.createParameterOrderingTable()
    row = parameterOrdering.addRow()
    row.setColumn('source', 'input files')
    row.setColumn('target', 'output file')
    
    definition = createShellDefinition(
        ['/Users/mjpan/pomsets/trunk/src/test/scripts/wordcount_reduce.py'],
        {
            'input files':{
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE:True,
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS:{
                    ParameterModule.COMMANDLINE_PREFIX_FLAG:['-input']
                }
            },
            'output file':{
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE:True,
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS:{
                    ParameterModule.COMMANDLINE_PREFIX_FLAG:['-output']
                },
                ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT:True,
            }
        },
        parameterOrdering
    )
    return definition

DEFINITION_WORDCOUNT_REDUCE = createWordCountReduceDefinition()



