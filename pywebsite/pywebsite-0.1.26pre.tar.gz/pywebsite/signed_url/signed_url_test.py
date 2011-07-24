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
    import signed_url
except:
    from pywebsite import signed_url


class TestHashUrl(unittest.TestCase):


    def test_hash(self):

        values = ["image.png", "10"]
        secret_salt = "thesepretz"
        keys = None
        hash = signed_url.sign(values, secret_salt, keys = keys)
        self.assertEqual(hash, 'pQ23QYykQcFNcfw-YAvSQsU8Jlk')
        # different secret_salt, different hash.
        hash2 = signed_url.sign(values, 'differentsecret_salt', keys = None)
        self.assertEqual(hash2, '_mTfyMd5hpN9xS--PeDiIlhmCxQ')

        # see that the hash is ok.
        self.assertTrue( signed_url.verify(values, secret_salt, hash, keys=keys) )

        keys = ['k1', 'k2']
        hash = signed_url.sign(values, secret_salt, keys = keys)
        self.assertTrue( signed_url.verify(values, secret_salt, hash, keys=keys) )

        # if we only use the first 6 characters see if that is ok too.
        self.assertTrue( signed_url.verify(values, secret_salt, hash[:6], 
                                         keys=keys, length_used = 6) )


    # this seems to be machine independent.  So disable for now.
    def XXtest_timing_attack(self):
        """ a timing attack is when you can use the timing to find out
            information about the signature.
        """
        # 
        
        values = ["image.png", "10"]
        secret_salt = "thesepretz"
        keys = None
        hash = signed_url.sign(values, secret_salt, keys = keys)
        # see that the hash is ok.
        self.assertTrue( signed_url.verify(values, secret_salt, hash, keys=keys) )
        

        # Now lets time one that is correct to the first part, but not the second.
        right_hash = hash
        # the first character is different.
        #offone_hash = 'X' + hash[1:]
        offone_hash = hash[:-1] + 'x'

        timer = time.time


        # we repeat a number of times to try and figure out the number of 
        # times the comparisons are different.

        worked_ok = 0
        repeat_times = 10

        for x in range(repeat_times):
            times = []
            times2 = []
            num_times = 100
            for x in range(num_times):
                t1 = timer()
                signed_url.verify(values, secret_salt, hash, keys=keys)
                t2 = timer()

                tt1 = timer()
                signed_url.verify(values, secret_salt, offone_hash, keys=keys)
                tt2 = timer()
                times.append(t2-t1)
                times2.append(tt2-tt1)


            #print (times)
            #print (times2)

            average1 = sum(times) / len(times)
            average2 = sum(times2) / len(times2)
            #print ((average1, average2))
            #print (average2 < average1)

            tot = 0
            for t1,t2 in zip(times, times2):
                if (t2 > t1):
                    tot += 1
            #print (len(times), tot)

            # see if the number of timings is fairly close statistically.
            error_range = (num_times / 10) + 2
            if abs(tot - (num_times/2)) <= error_range:
                worked_ok += 1


        #print (worked_ok, repeat_times )
        # mostly they should have worked.
        self.assertTrue(worked_ok >= repeat_times -1)



if __name__ == '__main__':
    unittest.main()

