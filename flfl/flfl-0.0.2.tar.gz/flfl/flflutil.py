# encoding: utf-8
__all__ = ['rewriteXml', 'mkswf', 'checkConfigPath', 'getConfigPath']
import flfl.fljscompiler
CONFIG = 'flfl.cfg'

class FlflGeneralException(Exception):pass

def rewriteXml(fd, strc):
    from xml.etree.ElementTree import ElementTree, tostring
    dom = ElementTree(file=fd)
    #doActionのなかみを消す
    tags = dom.find('./Header/tags')
    c = _createFrame(tags, strc['frames'], strc['hasmain'])
    defbs = tags.findall('./DefineButton2')
    defmc = tags.findall('./DefineSprite')
    defs = []
    for code in strc['objects']:
        targ = None
        if code[0]=='mc':
            for i in defmc:
                if 'objectID' in i.attrib and code[1] == int(i.attrib['objectID']):
                    targ = i
                    tmp = i.find('./tags')
                    if not tmp: raise FlflGeneralException('invalid xml')
                    _createFrame(tmp, code[2], code[3])
                    break
        if code[0]=='button':
            for i in defbs:
                if 'objectID' in i.attrib and code[1] == int(i.attrib['objectID']):
                    targ = i
                    break
        if targ is None:
            raise Exception('no %s id=%s' % (code[0], code[1]))
        tags.remove(targ)
        defs.append(targ)
    for d in defs:
        tags.insert(-1*c-1, d)
    pos = tags.findall('./PlaceObject2')
    for d in pos:
        tags.remove(d)
        tags.insert(-2, d)
    return tostring(dom.getroot())

def _createFrame(parent, frames, hasmain=False):
    actions = parent.findall('./DoAction')
    showframe = parent.findall('./ShowFrame')
    for i in actions + showframe:
        parent.remove(i)
    c = 0
    sf = parent.makeelement('ShowFrame', {})
    parent.insert(-1, sf)
    c += 1
    if frames:
        if hasmain:
            da = parent.makeelement('DoAction', {})
            parent.insert(-2, da)
            frames -= 1
            c+=1
        for i in range(frames):
            da = parent.makeelement('DoAction', {})
            parent.insert(-1, da)
            c+=1
    return c

def getConfigPath():
    from os.path import expanduser, join, exists
    path = join(expanduser('~'), '.flfl')
    if not exists(path):
        checkConfigPath()
    return path

def checkConfigPath():
    from os import mkdir
    from os.path import expanduser, join, exists, dirname
    from shutil import copyfile
    flflpath = join(expanduser('~'), '.flfl')
    if not exists(flflpath):
        try:
            mkdir(flflpath)
        except:
            print('cannot create: '+flflpath)
            exit(-1)
    conf = join(flflpath, CONFIG)
    if not exists(conf):
        try:
            copyfile(join(dirname(__file__), CONFIG), conf)
        except:
            print('cannot create config file: ' + conf)

def readConfig(path):
    from ConfigParser import SafeConfigParser
    from os.path import join, dirname
    if not path:
        path = join(getConfigPath(), CONFIG)

    config = SafeConfigParser({'outpath': getConfigPath()})
    try:
        config.readfp(open(path))
    except IOError, e:
        print(e)
        exit(-1)
    return config

def mkswf(xmlpath, sourcepath, output=None, asmf=False, xmlf=False,
          swfmillcmd=None, flasmcmd=None, configpath=None,
          cmpr=flfl.fljscompiler.FljsCompiler):
    from tempfile import mkstemp
    from subprocess import Popen, PIPE
    import os

    def trywrite(path, str):
        try:
            io = open(path, 'w')
            io.write(str)
            io.close()
        except:
            print('cannot write to %s' % path)

    config = readConfig(configpath)
    if not swfmillcmd:
        swfmillcmd = config.get('flfl', 'swfmill')
    if not flasmcmd:
        flasmcmd = config.get('flfl', 'flasm')

    _, tmpswf = mkstemp('.swf')
    c = cmpr(tmpswf)
    c.readFile(sourcepath, config.get('flfl', 'outpath'))
    strc = c.getStructure()
    xmlfd = file(xmlpath)
    nxml = rewriteXml(xmlfd, strc)
    xmlfd.close()
    if xmlf:
        if not output:
            fn = os.path.basename(sourcepath.split('.')[0]) + '.xml'
        else:
            fn = output
        trywrite(fn, nxml)
        return

    try:
        _, nxmlpath = mkstemp('.xml')
        nxmlfd = file(nxmlpath, 'w')
        nxmlfd.write(nxml)
        nxmlfd.close()

        swffd = file(tmpswf, 'w')
        pipe = Popen(args='%s xml2swf %s' % (swfmillcmd, nxmlpath), stdout=swffd, stderr=PIPE, shell=True)
        pipe.wait()
        if pipe.returncode != 0:
            print('swfmill error: '+pipe.stderr.read())
            exit(-1)
            swffd.close()
    finally:
        os.remove(nxmlpath)

    asm = c.run()
    if asmf:
        if not output:
            fn = os.path.basename(sourcepath.split('.')[0]) + '.flm'
        else:
            fn = output
        trywrite(fn, asm)
        return

    try:
        _, tmpasm = mkstemp('.flm')
        trywrite(tmpasm, asm)

        pipe2 = Popen('%s %s'%(flasmcmd, tmpasm), stderr=PIPE, shell=True)
        r = pipe2.wait()
        if pipe2.returncode != 0:
            print('flasm error: '+pipe2.stderr.read())
            exit(-1)
    finally:
        os.remove(tmpasm)

    try:
        nswffd = file(tmpswf)
        out = nswffd.read()
    finally:
        nswffd.close()

    if not output:
        output = 'a.swf'
    trywrite(output, out)


