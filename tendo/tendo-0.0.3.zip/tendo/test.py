#-----------------------------------------------------------------------------
# 2010  Sorin Sbarnea

import unittest


class AlfTest(unittest.TestCase):

    def test_class_predefined_table(self):
        self.assertEqual(1, 1, "Wrong test!")


def runtests():
    unittest.main()


if __name__ == '__main__':
    #runtests()
	import tee
	tee.tee_console(False)
	tee.tee_logger(None)
	tee.tee("python --version")

