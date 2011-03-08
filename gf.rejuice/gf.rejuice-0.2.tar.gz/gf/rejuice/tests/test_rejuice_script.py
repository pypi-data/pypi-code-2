import unittest
import cStringIO
import os
import sys

class TestReplaceUrl(unittest.TestCase):
    
    def test_basic(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.js', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "")
        self.assertEqual(res, {})

    def test_basic0(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    def test_basic1(self):
        
        from gf.rejuice.rejuice_script import replace_url
   
        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})
        
    def test_basic2(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top;} .header {background: #ffffff url(alma/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top;} .header {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    def test_basic3(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top;} .header {background: #ffffff url(korte/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top;} .header {background: #ffffff url(xxxprefix/korte_1.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg', '/this1/korte/korte.jpg': 'korte_1.jpg'})

    def test_basic4(self):
        
        from gf.rejuice.rejuice_script import replace_url
       
        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg?a=abc) no-repeat right top;} .header {background: #ffffff url(korte/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg?a=abc) no-repeat right top;} .header {background: #ffffff url(xxxprefix/korte_1.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg', '/this1/korte/korte.jpg': 'korte_1.jpg'})

    def test_basic5(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(http://valami.hu/alma/korte.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(http://valami.hu/alma/korte.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {})

    def test_basic6(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(alma/korte.jpg) no-repeat right top;} b {background: #ffffff url(korte/korte.jpg) no-repeat right top;}\n .header {background: #ffffff url(alma/eper.jpg) no-repeat right top;} .footer {background: #ffffff url(korte/banan.jpg) no-repeat right top;}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top;} b {background: #ffffff url(xxxprefix/korte_1.jpg) no-repeat right top;}\n .header {background: #ffffff url(xxxprefix/eper.jpg) no-repeat right top;} .footer {background: #ffffff url(xxxprefix/banan.jpg) no-repeat right top;}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg', '/this1/korte/korte.jpg': 'korte_1.jpg', '/this1/alma/eper.jpg': 'eper.jpg', '/this1/korte/banan.jpg': 'banan.jpg'})

    def test_basic7(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url('alma/korte.jpg') no-repeat right top}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    def test_basic8(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(\"alma/korte.jpg\") no-repeat right top}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    def test_basic9(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(  alma/korte.jpg   ) no-repeat right top}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    def test_basic10(self):
        
        from gf.rejuice.rejuice_script import replace_url

        f = cStringIO.StringIO("p {background: #ffffff url(     alma/korte.jpg  ) no-repeat right top}")
        n = cStringIO.StringIO()
        res = replace_url('/this1/infile.css', f, n, 'xxxprefix/') 
        self.assertEqual(n.getvalue(), "p {background: #ffffff url(xxxprefix/korte.jpg) no-repeat right top}\n")
        self.assertEqual(res, {'/this1/alma/korte.jpg': 'korte.jpg'})

    
class TestMain(unittest.TestCase):

    class mock_run_juicer(object):

        def __init__(self):
            self.result = []

        def __call__(self, resources, output):
            self.result.append((resources, output))

    class mock_run_replace_url(object):

        def __init__(self):
            self.result = []

        def __call__(self, output, prod_resource_path):
            self.result.append((output, prod_resource_path))
            images = {'alma/korte.jpg': 'korte.jpg', 'alma/banan.jpg' : 'banan.jpg'}
            return images

    class mock_copy_images(object):

        def __init__(self):
            self.result = []

        def __call__(self, images, prod_resource_path):
            self.result.append((images, prod_resource_path))
    
    def static_path(self, *arg):
        return os.path.join(os.path.dirname(sys.modules[__name__].__file__), *arg)

    def test_basic(self):
    
        mock_run_juicer = self.mock_run_juicer()
        from gf.rejuice.rejuice_script import main
        self.assertRaises(RuntimeError, main, ('xxx', self.static_path('config2/szla.ini')), run_juicer=mock_run_juicer)
        
    def test_basic1(self):
    
        mock_run_juicer = self.mock_run_juicer()
        from gf.rejuice.rejuice_script import main
        main(('xxx', self.static_path('config2/szla.ini'), 'filter:rejuice'), run_juicer=mock_run_juicer)
        self.assertEqual(mock_run_juicer.result, 
            [
                (('/this/static/views/static/default.css',), '/this/static/views/static/default.min.css'), 
                (('/this/static/views/static/default.js',), '/this/static/views/static/default.min.js')
            ])
    
    def test_extend(self):
    
        mock_run_juicer = self.mock_run_juicer()
        mock_run_replace_url = self.mock_run_replace_url()
        mock_copy_images = self.mock_copy_images()
        def mock_remove_file(f):
            pass

        from gf.rejuice.rejuice_script import main
        
        main(('xxx', self.static_path('config2/szla2.ini'), 'filter:rejuice'), run_juicer=mock_run_juicer, 
            run_replace_url=mock_run_replace_url, copy_images=mock_copy_images,
            remove_file=mock_remove_file)
        self.assertEqual(len(mock_run_juicer.result), 3)
        self.assertEqual(mock_run_juicer.result[0][0],
            ('/this/views/static/default.css', '/this/views/static2/static.css'))
        self.assertEqual(mock_run_juicer.result[1],
            (('/this/views/static/default.js',), '/this/views/static/default.min.js'))
        self.assertEqual(mock_run_juicer.result[2], (('/this/views/static/static2.css',),
            '/this/views/static/static.min.css'))

        self.assertEqual(mock_run_replace_url.result[0][1], '/this/views/static/default.min.css')
        self.assertEqual(len(mock_run_replace_url.result), 1)
        
        self.assertEqual(mock_copy_images.result, 
            [({'alma/korte.jpg': 'korte.jpg', 'alma/banan.jpg': 'banan.jpg'},
            '/this/views/static/default.min.css')]) 
 
