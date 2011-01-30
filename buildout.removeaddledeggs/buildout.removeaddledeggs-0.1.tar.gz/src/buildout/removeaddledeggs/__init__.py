# -*- coding: utf-8 -*-

import pprint, os, shutil, zc.buildout
logger = zc.buildout.easy_install.logger

def treat_version_info(dic):
    """Treats the pure version info     
    @return: dictionary"""
    
    for k, v in dic.iteritems():
        if v.find("#") >- 1:  # if a comment in line
            v = v.split("#")[0].strip()
            dic[k] = v
    return dic

def extract_info_eggdir(filename):
    """Extracts the name and version of
    an egg from its eggs/-directory
    @param filename: filename of egg
    @return: tuple of name and version"""
    try:
        name, version = filename.split('-', 2)[:2]
    except ValueError:
        raise NameError, "invalid dir-name: %s" % filename
    return name, version

def rm_egg(path):
    """Remove an egg (directory or zip-archive)
    @param path: absolute path to egg
    @return: None"""    
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.unlink(path)
    except os.error:
        raise

def install(buildout=None):
    
    eggsdir = buildout['buildout'].get('eggs-directory')
    versions = buildout.get('versions')    
    
    # XXX: Is there a possibility to get versions 
    # without comment-string??    
    installedversions =  treat_version_info(versions)   
    
    deleted = []
    invalid = []
    
    for file in os.listdir(eggsdir):
        try:
            egg_name, egg_version = extract_info_eggdir(file)      
        except NameError:
            invalid.append(file)
            continue 
        
        if installedversions.has_key(egg_name):
            
            if installedversions[egg_name] != egg_version.replace('_','-'):
                egg_path = os.path.join(eggsdir, file)
                rm_egg (egg_path)
                deleted.append("%s-%s" % (egg_name, egg_version))
                
    logger.info( "+" * 9 + ' buildout.removeaddledeggs ' + "+" * 9 )

    logger.info( "--> %d eggs removed: %s" % (len(deleted), deleted) )
    logger.info( "--> %d invalid eggs not removed: %s" % (len(invalid), invalid) )

    logger.info( "+" * 45 )
    