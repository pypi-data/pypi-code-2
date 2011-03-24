from logging import getLogger
from tempfile import TemporaryFile
from zipfile import ZipFile

from lxml import etree



log = getLogger('dspace.sword.item')

class SwordItem(object):
    """ Packaging and data for a single item deposit """
    def __init__(self):
        self._files = {}
        self._root = etree.XML('''
            <mets ID="sort-mets_mets" OBJID="sword-mets" LABEL="DSpace SWORD Item"
                PROFILE="DSpace METS SIP Profile 1.0" xmlns="http://www.loc.gov/METS/"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">
            </mets>
            ''')
    
    def add_file(self, data, filename, bundle='CONTENT'):
        """ Add or replace a file, filenames must be unique and data must 
        either be the all of the data in a string or a file-like object that 
        can be read, filenames for a file to open are not acceptable (for now) """
        if filename == 'mets.xml':
            raise ValueError('mets.xml is a reserved filename')
        
        self._files[filename] = (bundle, data,)
    
    def add_descriptive_metadata(self, data):
        count = len(self._root.findall('{http://www.loc.gov/METS/}dmdSec')) + 1
        dmd = etree.Element('{http://www.loc.gov/METS/}dmdSec',
                            ID='dmd-%d' % (count,),
                            GROUPID='dmd-grp-%d' % (count,))
        if isinstance(data,basestring):
            dmd.append(etree.fromstring(data))
        else:
            dmd.append(data)
        
        self._root.append(dmd)
    
    def get_mets_description(self):
        root = self._root.__copy__()
        
        file_sec = etree.Element('{http://www.loc.gov/METS/}fileSec')
        struct_map = etree.Element('{http://www.loc.gov/METS/}structMap',
                                   ID="sword-mets-struct-1", LABEL="STRUCTURE",
                                   TYPE="LOGICAL")
        structure = etree.Element('{http://www.loc.gov/METS/}div',
                                  ID="div-0", DMDID="dmd-1", TYPE="DSpace Item")
        
        bundles = {}
        
        for filename, combined in self._files.iteritems():
            bundles.setdefault(combined[0], []).append(filename)
        
        group_count = 0
        file_count = 0
        
        for bundle, files in bundles.iteritems():
            group_count += 1
            group = etree.Element('{http://www.loc.gov/METS/}fileGrp',
                                  ID='fgrp-%d' % (group_count,),
                                  USE=bundle)
            for filename in files:
                file_count += 1
                mfile = etree.Element('{http://www.loc.gov/METS/}file',
                                      GROUPID='fgid-%d' % (file_count,),
                                      ID='file-%d' % (file_count,))
                location = etree.Element('{http://www.loc.gov/METS/}FLocat',
                                         LOCTYPE='URL')
                location.set('{http://www.w3.org/1999/xlink}href', filename)
                div = etree.Element('{http://www.loc.gov/METS/}div',
                                    ID='div-%d' % (file_count,),
                                    TYPE='DSpace Bitstream')
                etree.SubElement(div, '{http://www.loc.gov/METS/}fptr',
                                 FILEID='file-%d' % (file_count,))
                mfile.append(location)
                group.append(mfile)
                structure.append(div)
                
            file_sec.append(group)
        
        root.append(file_sec)
        struct_map.append(structure)
        root.append(struct_map)
        
        log.debug(etree.tostring(root))
        return etree.tostring(root)
    
    def get_package(self):
        package = TemporaryFile()
        zipped = ZipFile(package, 'w')
        
        zipped.writestr('mets.xml', self.get_mets_description())
        for filename, combined in self._files.iteritems():
            data = combined[1]
            if isinstance(data, basestring):
                zipped.writestr(filename, data)
            elif hasattr(data,'read'):
                zipped.writestr(filename, data.read())
        
        zipped.close()
        package.seek(0)
        return package
    