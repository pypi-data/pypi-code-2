from unittest import TestCase, main
from dh_splitpackage import GlobPattern


class GlobPatternTests(TestCase):

    def test_new_works(self):
        obj = GlobPattern('')
        self.assertTrue(obj is not None)

    def test_new_caches_objects_with_identical_pattern(self):
        obj1 = GlobPattern('foo')
        obj2 = GlobPattern('foo')
        self.assertTrue(obj1 is obj2)

    def test_translate_adds_carret(self):
        self.assertTrue(GlobPattern._translate_to_regexp("").startswith("^"))

    def test_translate_adds_dollar(self):
        self.assertTrue(GlobPattern._translate_to_regexp("").endswith("$"))

    def test_translate_escapes_dots(self):
        initial = "foo.txt"
        expected = "^foo\.txt$"
        observed = GlobPattern._translate_to_regexp(initial)
        self.assertEqual(expected, observed)

    def test_translate_converts_single_stars(self):
        initial = "/foo/*/froz/"
        expected = "^/foo/[^/]*/froz/$"
        observed = GlobPattern._translate_to_regexp(initial)
        self.assertEqual(expected, observed)

    def test_translate_converts_double_star_slash(self):
        initial = "/foo/**/froz/"
        expected = "^/foo/(.+/|)froz/$"
        observed = GlobPattern._translate_to_regexp(initial)
        self.assertEqual(expected, observed)

    def test_translate_converts_everything_properly(self):
        initial = "/foo/**/froz.d/*/something/*else.txt"
        expected = "^/foo/(.+/|)froz\.d/[^/]*/something/[^/]*else\.txt$"
        observed = GlobPattern._translate_to_regexp(initial)
        self.assertEqual(expected, observed)

    def test_match_matches_single_start_correctly(self):
        pattern = GlobPattern("/f*/*.txt")
        for good in [
            "/foo/bar.txt",
            "/foo/froz.txt",
            "/froz/xx.txt"]:
            self.assertTrue(pattern.match(good))

    def test_match_matches_dots_as_normal_characters(self):
        self.assertTrue(GlobPattern("foo.txt").match("foo.txt"))
        self.assertFalse(GlobPattern("foo.txt").match("fooXtxt"))

    def test_match_matches_double_start_slash_correctly(self):
        self.assertTrue(GlobPattern("f**/").match("foo/"))
        self.assertTrue(GlobPattern("f**/").match("far/"))
        # This one fails to match because ** captures directories _only_
        self.assertFalse(GlobPattern("f**/").match("far/far/away.txt"))
        self.assertTrue(GlobPattern("f**/*").match("far/far/away.txt"))


if __name__ == '__main__':
    main()
