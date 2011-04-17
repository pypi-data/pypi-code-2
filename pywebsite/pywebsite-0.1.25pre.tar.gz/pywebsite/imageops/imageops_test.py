##    pywebsite - Python Website Library
##    Copyright (C) 2009, 2010 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
"""

"""
import time
import unittest
import os
import tempfile

try:
    import imageops
except:
    from pywebsite import imageops

class TestImageops(unittest.TestCase):


    def test_resize(self):
        import pygame

        test_data_dir = "/tmp/imageops_testdata"
        os.system("rm -rf /tmp/imageops_testdata")
        os.system("mkdir -p /tmp/imageops_testdata")


        cache_dir = "/tmp/imageops_testdata/cache" 
        path_to_galleries = "/tmp/imageops_testdata/galleries/" 
        agal = "/tmp/imageops_testdata/galleries/gal1" 

        for p in cache_dir, path_to_galleries, agal:
            os.system("mkdir -p %s" % p)

        apic = os.path.join(agal, "bla.png")
        surf = pygame.Surface((10,10))
        surf.fill((10,10,10,255))
        pygame.image.save(surf, apic)

        iops = imageops.ImageOps(cache_dir, path_to_galleries)


        self.assertFalse(iops.check_valid_paths(["/etc/passwd"]))
        self.assertFalse(iops.check_valid_paths(["../","lala"]))
        self.assertTrue(iops.check_valid_paths(['agal1', "lala.png"]))


        gallery = "gal1" 
        image = "bla.png" 
        width = 33
        height = 33
        rotate = False


        cached_fname = iops.get_cached_fname(gallery,image,width,height,rotate)
        self.assertEqual(cached_fname, '/tmp/imageops_testdata/cache/33x33-gal1-False-bla.png') 


        path = iops.get_image_path(gallery, image)

        # there should not be a cached file there already.
        self.assertFalse(iops.check_cached_fname(path, cached_fname))
        
        
        scaled_fname = iops.resize(gallery,image,width,height,rotate)
        # now the file should be cached.
        self.assertEqual(cached_fname, scaled_fname)
        self.assertTrue( os.path.exists(scaled_fname) )
        self.assertTrue(iops.check_cached_fname(path, cached_fname))

        # check that the new size is ok.
        s = pygame.image.load(scaled_fname)
        self.assertEqual(s.get_size(), (width, height))

        #Create a new version of the file.
        # sleep for the OS to give the file a different time stamp.
        time.sleep(1.0)
        pygame.image.save(surf, apic)
        #os.system("touch %s" % apic)

        # we should need to create a new cached version.
        self.assertFalse(iops.check_cached_fname(path, cached_fname))



        # cleanup.
        os.system("rm -rf /tmp/imageops_testdata")

if __name__ == '__main__':
    unittest.main()

