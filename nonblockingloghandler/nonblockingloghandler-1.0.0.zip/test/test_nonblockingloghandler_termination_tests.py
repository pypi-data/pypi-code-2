#!/usr/bin/env python

import subprocess
import time
import unittest

class TestNonblockingLogHandlerTerminationTests(unittest.TestCase):

    def execute_and_check_terminates(self, command, period_to_wait = 10):
        external_program = subprocess.Popen(command)
        poll_period = 0.25 # seconds
        total_polls = int(period_to_wait / poll_period)
        for junk_i in range(total_polls):
            time.sleep(poll_period)
            if external_program.poll() is not None:
                self.assertEquals(external_program.returncode, 0)
                # Program terminated. Test passed.
                break
        else:
            # Program didn't terminate in time. Test failed.
            external_program.kill()
            self.fail("Test failed to self-terminate")

    def test_termination_1(self):
        self.execute_and_check_terminates("python test_nonblockingloghandler_termination_subtest1.py")

    def test_termination_2(self):
        self.execute_and_check_terminates("python test_nonblockingloghandler_termination_subtest2.py")

    def test_termination_3(self):
        self.execute_and_check_terminates("python test_nonblockingloghandler_termination_subtest3.py")

if __name__ == "__main__":
    unittest.main()
