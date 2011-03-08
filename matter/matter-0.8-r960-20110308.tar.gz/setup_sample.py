#!/usr/bin/env python

def preparePackage( package, sourceRoot = "." ):
    package.changeRoot( sourceRoot )
    #------------------------------------------------------------
    #dependencies
    #
    #------------------------------------------------------------
    
    #--------------------------------------------------------
    # now add subdirs
    #
    package.addPurePython(
        sourceDir = 'sample',
        destModuleName = 'sample' )
    package.addPurePython(
        sourceDir = 'interaction',
        destModuleName = 'interaction' )
    package.addData( 
        sourceDir = "interactionDb",
        destDir = "interactionDb")

    return package

if __name__ == "__main__":
    from distutils_adpt.Package import Package
    package = Package('sample', '1.0')
    preparePackage(package)
    package.setup()

