import os
import os.path
import unittest

def find_python_module(qualified_module_name, root_dir):
    """This utility function looks for a python module
    under the specified directory. It returns the full
    path to the directory above the module. This directory can
    be added to sys.path to successfully import the module. If
    the module is not found, we return None.

    There is a special case for when the root directory is the
    first (topmost) component of the module. In this case, we return
    the directory above the root directory.
    """
    def check_module_file(parent_dir, module_name):
        module_file = os.path.join(parent_dir, module_name + ".py")
        if os.path.exists(module_file):
            return True
        else:
            return False
    
    def check_dir(current_dir, module_list):
        """Return True if the module_list exists in the current directory"""
        if len(module_list)==1:
            return check_module_file(current_dir, module_list[0])
        else:
            next_dir = os.path.join(current_dir, module_list[0])
            if os.path.isdir(next_dir) and os.path.exists(os.path.join(next_dir, "__init__.py")):
                return check_dir(next_dir, module_list[1:])
            else:
                return False

    full_module_list = qualified_module_name.split('.')
    for (dirname, subdirs, files) in os.walk(os.path.abspath(os.path.expanduser(root_dir))):
         module_path = check_dir(dirname, full_module_list)
         if module_path:
             return dirname
    # if we get here, the module isn't under root_dir. we have a special case for when
    # current_dir is the top directory of the module.
    if check_dir(os.path.dirname(root_dir), full_module_list):
        return os.path.dirname(root_dir)
    else:
        return None


class TestFindPythonModule(unittest.TestCase):
    def _make_py_file(self, parent_dir, name):
        with open(os.path.join(parent_dir, name), "w") as f:
            f.write("# \n")

    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.w_dir = os.path.join(self.temp_dir, "w")
        os.mkdir(self.w_dir)
        self.x_dir = os.path.join(self.w_dir, "x")
        os.mkdir(self.x_dir)
        self._make_py_file(self.x_dir, "__init__.py")
        self.y_dir = os.path.join(self.x_dir, "y")
        os.mkdir(self.y_dir)
        self._make_py_file(self.y_dir, "__init__.py")
        self._make_py_file(self.y_dir, "z.py")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_find_from_temp_dir(self):
        """Check for x.y.z from temp_dir. This should return tmpdir/w.
        """
        res = find_python_module("x.y.z", self.temp_dir)
        self.assertEqual(res, self.w_dir)

    def test_find_from_w(self):
        """Check for x.y.z from w. This should return tmpdir/w.
        """
        res = find_python_module("x.y.z", self.w_dir)
        self.assertEqual(res, self.w_dir)

    def test_find_from_x(self):
        """Check for x.y.z from x. This should return tmpdir/w
        """
        res = find_python_module("x.y.z", self.x_dir)
        self.assertEqual(res, self.w_dir)

    def test_find_z_from_y(self):
        """Check for z from y. This should return tmpdir/w/x/y.
        """
        res = find_python_module("z", self.y_dir)
        self.assertEqual(res, self.y_dir)

    def test_find_from_y(self):
        """Check for x.y.z from y. This should return None.
        """
        res = find_python_module("x.y.z", self.y_dir)
        self.assertEqual(res, None)

    def test_find_bogus_from_w(self):
        """Check for a.b.c from temp_dir. This should return None"""
        res = find_python_module("a.b.c", self.temp_dir)
        self.assertEqual(res, None)


if __name__ == '__main__':
    unittest.main()
