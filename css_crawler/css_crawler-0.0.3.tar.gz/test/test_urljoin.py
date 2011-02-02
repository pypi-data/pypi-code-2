from css_crawler.lib.css.fetch import join_url
import nose


def test_strange_path1():
    """
    Test a strange path: http://site.com/ & /path/../path/.././path/./
    """
    res = join_url('http://site.com/', '/path/../path/.././path/./')[1]

    nose.tools.assert_equal(res, 'http://site.com/path')


def test_strange_path2():
    """
    Test a strange path:
        http://site.com/path/x.html & /path/../path/.././path/./y.html
    """
    res = join_url('http://site.com/path/x.html',
        '/path/../path/.././path/./y.html')[1]

    nose.tools.assert_equal(res, 'http://site.com/path/y.html')


def test_strange_too_far1():
    """
    Test a path that .. up too far:
        http://site.com/ & ../../../../path/
    """
    res = join_url('http://site.com/', '../../../../path/')[1]

    nose.tools.assert_equal(res, 'http://site.com/path')


def test_strange_too_far2():
    """
    Test a path that .. up too far:
        http://site.com/x/x.html & ../../../../path/moo.html
    """
    res = join_url('http://site.com/x/x.html', '../../../../path/moo.html')[1]

    nose.tools.assert_equal(res, 'http://site.com/path/moo.html')


def test_strange_combine1():
    """
    Test how url are combined: http://site.com/99/x.html & 1/2/3/moo.html
    """
    res = join_url('http://site.com/99/x.html', '1/2/3/moo.html')[1]

    nose.tools.assert_equal(res, 'http://site.com/99/1/2/3/moo.html')


def test_strange_combine2():
    """
    Test how url are combined: http://site.com/99/x.html & ../1/2/3/moo.html
    """
    res = join_url('http://site.com/99/x.html', '../1/2/3/moo.html')[1]

    nose.tools.assert_equal(res, 'http://site.com/1/2/3/moo.html')


def test_empty_path():
    """
    Test if an ending / is added to www.server.com like urls
    """
    res = join_url('http://site.com', '')[1]

    nose.tools.assert_equal(res, 'http://site.com/')


def test_noempty_path():
    """
    Test if an ending / is added to www.server.com/index.html like urls
    """
    res = join_url('http://site.com/index.html', '')[1]

    nose.tools.assert_equal(res, 'http://site.com/index.html')
