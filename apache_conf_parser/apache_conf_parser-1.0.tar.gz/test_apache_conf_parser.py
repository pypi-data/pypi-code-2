
import unittest as u_mod
from apache_conf_parser import *

class GenericDirective(Directive):
    def add_line(self, line):
        self.add_to_header(line)
        super(GenericDirective, self).add_line(line)

class TestListAdapter(u_mod.TestCase):
    def test___init___empty_1(self):
        self.assertEqual(list(ListAdapter()), [])
    def test___init___empty_2(self):
        iterable = []
        self.assertEqual(list(ListAdapter(*iterable)), [])
    def test___init___plain(self):
        self.assertEqual(list(ListAdapter(1,2)), [1,2])
    def test___init___list(self):
        iterable = [1,2]
        self.assertEqual(list(ListAdapter(*iterable)), [1,2])
    def test___init___tuple(self):
        iterable = (1,2)
        self.assertEqual(list(ListAdapter(*iterable)), [1,2])
    def test___init___generator(self):
        iterable = (x for x in [1,2])
        self.assertEqual(list(ListAdapter(*iterable)), [1,2])
    def test___init___lc(self):
        iterable = [x for x in [1,2]]
        self.assertEqual(list(ListAdapter(*iterable)), [1,2])
    def test___init___items(self):
        la = ListAdapter(1,2)
        self.assertEqual(la.items, [1,2])
    def test___len___empty(self):
        la = ListAdapter()
        self.assertEqual(len(la), 0)
    def test___len___not_empty(self):
        la = ListAdapter(1,2)
        self.assertEqual(len(la), 2)
    def test___contains___empty(self):
        la = ListAdapter()
        self.assertFalse(1 in la)
    def test___contains___not_empty(self):
        la = ListAdapter(1,2)
        self.assertTrue(1 in la)
    """
    # untested
    def __iter__(self):
        return iter(self.items)
    def __getitem__(self, index):
        return self.items[index]
    def __setitem__(self, index, val):
        self.items[index] = val
    def __delitem__(self, index):
        del self.items[index]
    def insert(self, index, val):
        self.items.insert(index, val)
    """

class TestNode(u_mod.TestCase):
    CLASS = Node
    def test_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])

    def test_match_empty(self):
        self.assertTrue(self.CLASS.match(""))
    def test_match_not_empty(self):
        self.assertTrue(self.CLASS.match("something"))
    def test_match_None(self):
        self.assertFalse(self.CLASS.match(None))

    def test_add_line_complete_1(self):
        node = self.CLASS()
        node.complete = True
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_2(self):
        node = self.CLASS()
        node.add_line("")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_3(self):
        node = self.CLASS()
        node.add_line("first")
        with self.assertRaises(NodeCompleteError):
            node.add_line("second")
    def test_add_line_added_first(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertEqual(node.lines[0], "first")
    def test_add_line_added_second(self):
        node = self.CLASS()
        node.add_line("first")
        node.complete = False
        node.add_line("second")
        self.assertEqual(node.lines[0], "first")
        self.assertEqual(node.lines[1], "second")
    def test_add_line_autocomplete(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertTrue(node.complete)
    def test_add_line_autochanged(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertFalse(node.changed)
    def test_add_line_continuation(self):
        node = self.CLASS()
        node.add_line("first\\")
        self.assertFalse(node.complete)
    def test_add_line_space_continuation(self):
        node = self.CLASS()
        node.add_line("first \\")
        self.assertFalse(node.complete)

    def test___str___empty(self):
        node = self.CLASS()
        self.assertEqual("", str(node))
    @u_mod.skip("works if add_line on a complete node sets changed instead of raising.")
    def test___str___multiple(self):
        line1 = "first"
        line2 = "second"
        node = self.CLASS()
        node.add_line(line1)
        node.add_line(line2)
        self.assertEqual(line1+"\n"+line2, str(node))
    def test___str___new(self):
        line = "first"
        node = self.CLASS()
        node.add_line(line)
        self.assertEqual(line, str(node))
    def test___str___changed(self):
        # should match self.content
        line = "first"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line, str(node))

    def test_pprint_empty(self):
        node = self.CLASS()
        self.assertEqual("", node.pprint())
    def test_pprint_empty_depth_0(self):
        node = self.CLASS()
        self.assertEqual("", node.pprint(0))
    def test_pprint_empty_depth_1(self):
        node = self.CLASS()
        self.assertEqual(INDENT, node.pprint(1))
    def test_pprint_empty_depth_1_keyword(self):
        node = self.CLASS()
        self.assertEqual(INDENT, node.pprint(depth=1))
    def test_pprint_empty_depth_2(self):
        node = self.CLASS()
        self.assertEqual(INDENT*2, node.pprint(2))
    def test_pprint_blank_depth_0(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual("", node.pprint(0))
    def test_pprint_blank_depth_1(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual(INDENT, node.pprint(1))
    def test_pprint_blank_depth_2(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual(INDENT*2, node.pprint(2))
    def test_pprint_depth_0(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertEqual("first", node.pprint(0))
    def test_pprint_depth_1(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertEqual(INDENT+"first", node.pprint(1))
    def test_pprint_depth_2(self):
        node = self.CLASS()
        node.add_line("first")
        self.assertEqual(INDENT*2+"first", node.pprint(2))
    def test_pprint_leading_spaces(self):
        node = self.CLASS()
        node.add_line("  first")
        self.assertEqual("first", node.pprint())


class TestCommentNode(u_mod.TestCase):
    CLASS = CommentNode
    def test_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])

    def test_match_None(self):
        self.assertFalse(self.CLASS.match(None))
    def test_match_empty(self):
        self.assertFalse(self.CLASS.match(""))

    def test_match_comment_solo(self):
        self.assertTrue(self.CLASS.match("#"))
    def test_match_comment_solo_space(self):
        self.assertTrue(self.CLASS.match(" #"))
    def test_match_comment_space(self):
        self.assertTrue(self.CLASS.match(" # this is a comment"))
    def test_match_comment_no_space(self):
        self.assertTrue(self.CLASS.match("# this is a comment"))
    def test_match_comment_continuation(self):
        self.assertFalse(self.CLASS.match("# this is a comment\\"))

    def test_match_blank_spaces(self):
        self.assertFalse(self.CLASS.match("   "))
    def test_match_blank_tabs(self):
        self.assertFalse(self.CLASS.match("		"))
    def test_match_blank_continuation(self):
        self.assertFalse(self.CLASS.match("   \\"))

    def test_match_simple_directive_just_name(self):
        self.assertFalse(self.CLASS.match("name"))
    def test_match_simple_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match(" name"))
    def test_match_simple_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("name "))
    def test_match_simple_directive_just_name_continuation(self):
        self.assertFalse(self.CLASS.match("name\\"))
    def test_match_simple_directive_name_and_args(self):
        self.assertFalse(self.CLASS.match("name something else"))
    def test_match_simple_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("   name something else"))
    def test_match_simple_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("name something else   "))
    def test_match_simple_directive_continuation(self):
        self.assertFalse(self.CLASS.match("name something else\\"))

    def test_match_complex_directive_empty(self):
        self.assertFalse(self.CLASS.match("<>"))
    def test_match_complex_directive_empty_space(self):
        self.assertFalse(self.CLASS.match("< >"))
    def test_match_complex_directive_just_name(self):
        self.assertFalse(self.CLASS.match("<name>"))
    def test_match_complex_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match("< name>"))
    def test_match_complex_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name >"))
    def test_match_complex_directive_just_name_open(self):
        self.assertFalse(self.CLASS.match("<name"))
    def test_match_complex_directive_just_name_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name\\"))
    def test_match_complex_directive_just_name_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name \\"))
    def test_match_complex_directive_just_name_invalid_1(self):
        self.assertFalse(self.CLASS.match("<na+me>"))
    def test_match_complex_directive_just_name_invalid_2(self):
        self.assertFalse(self.CLASS.match("<na<me>"))
    def test_match_complex_directive_name_and_args_open(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2"))
    def test_match_complex_directive_name_and_args_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2\\"))
    def test_match_complex_directive_name_and_args_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2 \\"))
    def test_match_complex_directive_closed(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>"))
    def test_match_complex_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("  <name arg1 arg2>"))
    def test_match_complex_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>  "))
    def test_match_complex_directive_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>\\"))
    def test_match_complex_directive_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> \\"))
    def test_match_complex_directive_trailing_text(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> text"))

    def test___str___empty(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            str(node)
    def test___str___new(self):
        line = "# comment"
        node = self.CLASS()
        node.add_line(line)
        self.assertEqual(line, str(node))
    def test___str___changed_1(self):
        line = "# comment"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line, str(node))
    #@u_mod.skip("Currently comments cannot have leading spaces.")
    def test___str___changed_2(self):
        line = " # comment"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line.lstrip(), str(node))
    def test___str___changed_3(self):
        line = "# comment   "
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line, str(node))

    def test_pprint_empty(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint()
    def test_pprint_empty_depth_0(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint(0)
    def test_pprint_empty_depth_1(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint(1)
    def test_pprint_empty_depth_1_keyword(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint(depth=1)
    def test_pprint_empty_depth_2(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint(2)
    def test_pprint_depth_0(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertEqual("# comment", node.pprint(0))
    def test_pprint_depth_1(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertEqual(INDENT+"# comment", node.pprint(1))
    def test_pprint_depth_2(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertEqual(INDENT*2+"# comment", node.pprint(2))
    #@u_mod.skip("Currently comments cannot have leading spaces.")
    def test_pprint_leading_space(self):
        line = " # comment"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line.lstrip(), str(node))

    #@u_mod.skip("Currently comments cannot have leading spaces.")
    def test_add_line_leading_space_1(self):
        node = self.CLASS()
        node.add_line(" # comment")
        self.assertEqual(node.lines[0], " # comment")
    #@u_mod.skip("Currently comments cannot have leading spaces.")
    def test_add_line_leading_space_2(self):
        node = self.CLASS()
        node.add_line("  # comment")
        self.assertEqual(node.lines[0], "  # comment")
    #@u_mod.skip("Currently comments cannot have leading spaces.")
    def test_add_line_leading_space_3(self):
        node = self.CLASS()
        node.add_line("	# comment")
        self.assertEqual(node.lines[0], "	# comment")
    def test_add_line_complete_1(self):
        node = self.CLASS()
        node.complete = True
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_1(self):
        node = self.CLASS()
        node.complete = True
        with self.assertRaises(NodeCompleteError):
            node.add_line("# comment")
    def test_add_line_complete_3(self):
        node = self.CLASS()
        node.add_line("# comment")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_4(self):
        node = self.CLASS()
        node.add_line("# comment")
        with self.assertRaises(NodeCompleteError):
            node.add_line("# comment")
    def test_add_line_added_first(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertEqual(node.lines[0], "# comment")
    def test_add_line_autocomplete(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertTrue(node.complete)
    def test_add_line_autochanged(self):
        node = self.CLASS()
        node.add_line("# comment")
        self.assertFalse(node.changed)
    def test_add_line_continuation(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("# comment\\")
    def test_add_line_space_continuation(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("# comment \\")


class TestBlankNode(u_mod.TestCase):
    CLASS = BlankNode
    def test_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])

    def test_match_None(self):
        self.assertFalse(self.CLASS.match(None))
    def test_match_empty(self):
        self.assertTrue(self.CLASS.match(""))

    def test_match_comment_solo(self):
        self.assertFalse(self.CLASS.match("#"))
    def test_match_comment_solo_space(self):
        self.assertFalse(self.CLASS.match(" #"))
    def test_match_comment_space(self):
        self.assertFalse(self.CLASS.match(" # this is a comment"))
    def test_match_comment_no_space(self):
        self.assertFalse(self.CLASS.match("# this is a comment"))
    def test_match_comment_continuation(self):
        self.assertFalse(self.CLASS.match("# this is a comment\\"))

    def test_match_blank_spaces(self):
        self.assertTrue(self.CLASS.match("   "))
    def test_match_blank_tabs(self):
        self.assertTrue(self.CLASS.match("		"))
    def test_match_blank_continuation(self):
        self.assertFalse(self.CLASS.match("   \\"))

    def test_match_simple_directive_just_name(self):
        self.assertFalse(self.CLASS.match("name"))
    def test_match_simple_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match(" name"))
    def test_match_simple_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("name "))
    def test_match_simple_directive_just_name_continuation(self):
        self.assertFalse(self.CLASS.match("name\\"))
    def test_match_simple_directive_name_and_args(self):
        self.assertFalse(self.CLASS.match("name something else"))
    def test_match_simple_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("   name something else"))
    def test_match_simple_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("name something else   "))
    def test_match_simple_directive_continuation(self):
        self.assertFalse(self.CLASS.match("name something else\\"))

    def test_match_complex_directive_empty(self):
        self.assertFalse(self.CLASS.match("<>"))
    def test_match_complex_directive_empty_space(self):
        self.assertFalse(self.CLASS.match("< >"))
    def test_match_complex_directive_just_name(self):
        self.assertFalse(self.CLASS.match("<name>"))
    def test_match_complex_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match("< name>"))
    def test_match_complex_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name >"))
    def test_match_complex_directive_just_name_open(self):
        self.assertFalse(self.CLASS.match("<name"))
    def test_match_complex_directive_just_name_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name\\"))
    def test_match_complex_directive_just_name_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name \\"))
    def test_match_complex_directive_just_name_invalid_1(self):
        self.assertFalse(self.CLASS.match("<na+me>"))
    def test_match_complex_directive_just_name_invalid_2(self):
        self.assertFalse(self.CLASS.match("<na<me>"))
    def test_match_complex_directive_name_and_args_open(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2"))
    def test_match_complex_directive_name_and_args_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2\\"))
    def test_match_complex_directive_name_and_args_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2 \\"))
    def test_match_complex_directive_closed(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>"))
    def test_match_complex_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("  <name arg1 arg2>"))
    def test_match_complex_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>  "))
    def test_match_complex_directive_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>\\"))
    def test_match_complex_directive_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> \\"))
    def test_match_complex_directive_trailing_text(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> text"))

    def test___str___empty(self):
        node = self.CLASS()
        self.assertEqual("", str(node))
    def test___str___new_1(self):
        line = "    "
        node = self.CLASS()
        node.add_line(line)
        self.assertEqual("    ", str(node))
    def test___str___new_2(self):
        line = "	"
        node = self.CLASS()
        node.add_line(line)
        self.assertEqual("	", str(node))
    def test___str___changed(self):
        line = "    "
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual("    ", str(node))

    def test_pprint_blank_depth_0(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual("", node.pprint(0))
    def test_pprint_blank_depth_1(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual("", node.pprint(1))
    def test_pprint_blank_depth_2(self):
        node = self.CLASS()
        node.add_line("")
        self.assertEqual("", node.pprint(2))
    def test_pprint_depth_0(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertEqual("", node.pprint(0))
    def test_pprint_depth_1(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertEqual("", node.pprint(1))
    def test_pprint_depth_2(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertEqual("", node.pprint(2))
    def test_pprint_spaces(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertEqual("", node.pprint())

    def test_add_line_newline(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("\n")
    def test_add_line_complete_1(self):
        node = self.CLASS()
        node.complete = True
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_2(self):
        node = self.CLASS()
        node.add_line("")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_added_first(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertEqual(node.lines[0], "    ")
    def test_add_line_autocomplete(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertTrue(node.complete)
    def test_add_line_autochanged(self):
        node = self.CLASS()
        node.add_line("    ")
        self.assertFalse(node.changed)
    def test_add_line_continuation(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("  \\")


class TestDirective(u_mod.TestCase):
    CLASS = GenericDirective

    """
    class Name(object):
        def __get__(self, obj, cls):
            if not hasattr(obj, "_name"):
                return None
            return obj._name
        def __set__(self, obj, value):
            if hasattr(obj, "_name") and obj._name is not None:
                raise DirectiveError("Name is already set.  Cannot set to %s" % value)
            if not re_mod.match(obj.NAME_RE, value):
                raise DirectiveError("Invalid name: %s" % value)
            obj._name = value
    name = Name()
    """

    def test_new_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])

    def test_new_name(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.name
    def test_name_header_incomplete_1(self):
        node = self.CLASS()
        node.add_line("name\\")
        self.assertEqual(node.name, "name")
    def test_name_header_incomplete_2(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        self.assertEqual(node.name, "name")
    def test_name_complete_1(self):
        node = self.CLASS()
        node.add_line("name arg1")
        node.complete = True
        self.assertEqual(node.name, "name")
    def test_name_complete_2(self):
        node = self.CLASS()
        node.add_line("name arg1")
        node.complete = False
        self.assertEqual(node.name, "name")
    def test_name_complete_3(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertEqual(node.name, "name")

    """

    def add_header(self, line):
        if "<" in line or ">" in line:
            raise DirectiveError("Angle brackets not allowed in directive headers.")
        if line[-1] == "\\":
            line = line[:-1]
        parts = line.strip().split()
        if not self.name:
            self.name = parts[0]
            parts = parts[1:]
        for part in parts:
            self.arguments.append(part)

    def __repr__(self):
        return "<%s Directive at %s>" % (
                self.name,
                id(self),
                )
    def pprint(self, depth=0):
        return "%s%s %s" % (
                INDENT*depth, 
                self.name, 
                " ".join([arg for arg in self.arguments]),
                )
    """
    def test_new_args(self):
        # even though the name is not set yet...
        node = self.CLASS()
        self.assertEqual(node.arguments, [])
    def test_args_header_incomplete_1(self):
        node = self.CLASS()
        node.add_line("name\\")
        self.assertEqual(node.arguments, [])
    def test_args_header_incomplete_2(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        self.assertEqual(node.arguments, ["arg1",])
    def test_args_complete_empty_args_1(self):
        node = self.CLASS()
        node.add_to_header("name")
        node.complete = True
        self.assertEqual(node.arguments, [])
    def test_args_complete_empty_args_2(self):
        node = self.CLASS()
        node.add_to_header("name")
        self.assertEqual(node.arguments, [])
    def test_args_complete_not_empty_args_1(self):
        node = self.CLASS()
        node.add_to_header("name arg1")
        self.assertEqual(node.arguments, ["arg1",])
    def test_args_complete_not_empty_args_2(self):
        node = self.CLASS()
        node.add_to_header("name arg1 arg2")
        self.assertEqual(node.arguments, ["arg1", "arg2"])
    def test_args_complete_not_empty_args_3(self):
        node = self.CLASS()
        node.add_to_header("name\\")
        node.add_to_header("arg1")
        self.assertEqual(node.arguments, ["arg1",])
    def test_args_complete_not_empty_args_4(self):
        node = self.CLASS()
        node.add_to_header("name arg1\\")
        node.add_to_header("arg2")
        self.assertEqual(node.arguments, ["arg1", "arg2"])

    def test_new_content(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.content

class TestSimpleDirective(u_mod.TestCase):
    CLASS = SimpleDirective
    def test_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])

    def test_match_None(self):
        self.assertFalse(self.CLASS.match(None))
    def test_match_empty(self):
        self.assertFalse(self.CLASS.match(""))

    def test_match_comment_solo(self):
        self.assertFalse(self.CLASS.match("#"))
    def test_match_comment_solo_space(self):
        self.assertFalse(self.CLASS.match(" #"))
    def test_match_comment_space(self):
        self.assertFalse(self.CLASS.match(" # this is a comment"))
    def test_match_comment_no_space(self):
        self.assertFalse(self.CLASS.match("# this is a comment"))
    def test_match_comment_continuation(self):
        self.assertFalse(self.CLASS.match("# this is a comment\\"))

    def test_match_blank_spaces(self):
        self.assertFalse(self.CLASS.match("   "))
    def test_match_blank_tabs(self):
        self.assertFalse(self.CLASS.match("		"))
    def test_match_blank_continuation(self):
        self.assertFalse(self.CLASS.match("   \\"))

    def test_match_simple_directive_just_name(self):
        self.assertTrue(self.CLASS.match("name"))
    def test_match_simple_directive_just_name_leading_space(self):
        self.assertTrue(self.CLASS.match(" name"))
    def test_match_simple_directive_just_name_trailing_space(self):
        self.assertTrue(self.CLASS.match("name "))
    def test_match_simple_directive_just_name_continuation(self):
        self.assertTrue(self.CLASS.match("name\\"))
    def test_match_simple_directive_name_and_args(self):
        self.assertTrue(self.CLASS.match("name something else"))
    def test_match_simple_directive_leading_space(self):
        self.assertTrue(self.CLASS.match("   name something else"))
    def test_match_simple_directive_trailing_space(self):
        self.assertTrue(self.CLASS.match("name something else   "))
    def test_match_simple_directive_continuation(self):
        self.assertTrue(self.CLASS.match("name something else\\"))

    def test_match_complex_directive_empty(self):
        self.assertFalse(self.CLASS.match("<>"))
    def test_match_complex_directive_empty_space(self):
        self.assertFalse(self.CLASS.match("< >"))
    def test_match_complex_directive_just_name(self):
        self.assertFalse(self.CLASS.match("<name>"))
    def test_match_complex_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match("< name>"))
    def test_match_complex_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name >"))
    def test_match_complex_directive_just_name_open(self):
        self.assertFalse(self.CLASS.match("<name"))
    def test_match_complex_directive_just_name_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name\\"))
    def test_match_complex_directive_just_name_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name \\"))
    def test_match_complex_directive_just_name_invalid_1(self):
        self.assertFalse(self.CLASS.match("<na+me>"))
    def test_match_complex_directive_just_name_invalid_2(self):
        self.assertFalse(self.CLASS.match("<na<me>"))
    def test_match_complex_directive_name_and_args_open(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2"))
    def test_match_complex_directive_name_and_args_open_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2\\"))
    def test_match_complex_directive_name_and_args_open_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2 \\"))
    def test_match_complex_directive_closed(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>"))
    def test_match_complex_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("  <name arg1 arg2>"))
    def test_match_complex_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>  "))
    def test_match_complex_directive_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>\\"))
    def test_match_complex_directive_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> \\"))
    def test_match_complex_directive_trailing_text(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> text"))

    def test___str___empty(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            str(node)
    def test___str___multiple(self):
        line1 = "name arg1\\"
        line2 = "arg2 arg3"
        node = self.CLASS()
        node.add_line(line1)
        node.add_line(line2)
        self.assertEqual(line1+"\n"+line2, str(node))
    def test___str___new(self):
        line = "name"
        node = self.CLASS()
        node.add_line(line)
        self.assertEqual(line, str(node))
    def test___str___changed_1(self):
        line = "name"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line, str(node))
    def test___str___changed_2(self):
        line = "name arg1"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual(line, str(node))
    def test___str___changed_3(self):
        line = "    name"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual("name", str(node))
    def test___str___changed_4(self):
        line = "    name arg1"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual("name arg1", str(node))
    def test___str___changed_5(self):
        line = "    name	arg1"
        node = self.CLASS()
        node.add_line(line)
        node.changed = True
        self.assertEqual("name arg1", str(node))

    def test_pprint_depth_0(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertEqual("name arg1", node.pprint(0))
    def test_pprint_depth_1(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertEqual(INDENT+"name arg1", node.pprint(1))
    def test_pprint_depth_2(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertEqual(INDENT*2+"name arg1", node.pprint(2))

    def test_add_line_complete_1(self):
        node = self.CLASS()
        node.name = "name"
        node.complete = True
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_2(self):
        node = self.CLASS()
        node.add_line("name arg1")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_3(self):
        node = self.CLASS()
        node.add_line("name arg1")
        with self.assertRaises(NodeCompleteError):
            node.add_line("arg2 arg3")
    def test_add_line_incomplete_header_name_and_arg_invalid(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("name <arg1\\")
    def test_add_line_incomplete_header_name_and_arg_invalid_multi(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("<arg2\\")
    def test_add_line_complete_header_name_and_arg_invalid(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("name <arg1")
    def test_add_line_complete_header_name_and_arg_invalid_multi(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("<arg2")
    def test_add_line_complete_header_name_and_arg_invalid_close(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("name arg1>")
    def test_add_line_complete_header_name_and_arg_invalid_close_multi(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("arg2>")
    def test_add_line_added_first(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertEqual(node.lines[0], "name arg1")
    def test_add_line_added_second_1(self):
        node = self.CLASS()
        node.add_line("name arg1")
        node.complete = False
        node.add_line("arg2")
        self.assertEqual(node.lines[0], "name arg1")
        self.assertEqual(node.lines[1], "arg2")
    def test_add_line_added_second_2(self):
        node = self.CLASS()
        node.add_line("name arg1")
        node.complete = False
        node.add_line("arg2 ")
        self.assertEqual(node.lines[0], "name arg1")
        self.assertEqual(node.lines[1], "arg2 ")
    def test_add_line_autocomplete(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertTrue(node.complete)
    def test_add_line_autochanged(self):
        node = self.CLASS()
        node.add_line("name arg1")
        self.assertFalse(node.changed)
    def test_add_line_continuation_1(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        self.assertFalse(node.complete)
    def test_add_line_continuation_2(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        node.add_line("arg2\\")
        self.assertFalse(node.complete)
    def test_add_line_continuation_3(self):
        node = self.CLASS()
        node.add_line("name arg1\\")
        node.add_line("arg2")
        self.assertTrue(node.complete)
    def test_add_line_space_continuation(self):
        node = self.CLASS()
        node.add_line("name arg1 \\")
        self.assertFalse(node.complete)


class TestComplexDirective(u_mod.TestCase):
    CLASS = ComplexDirective
    def test_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_not_changed(self):
        node = self.CLASS()
        self.assertFalse(node.changed)
    def test_lines_empty(self):
        node = self.CLASS()
        self.assertEqual(node.lines, [])
    def test_header_ready(self):
        node = self.CLASS()
        self.assertIsInstance(node.header, SimpleDirective)
    def test_header_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.header.complete)
    def test_body_ready(self):
        node = self.CLASS()
        self.assertIsInstance(node.body, ComplexNode)
    def test_body_not_complete(self):
        node = self.CLASS()
        self.assertFalse(node.body.complete)
    def test_tail_empty(self):
        node = self.CLASS()
        self.assertEqual(node.tail, "")
    def test_tail_not_matched(self):
        node = self.CLASS()
        self.assertFalse(node.tailmatch)

    def test_match_None(self):
        self.assertFalse(self.CLASS.match(None))
    def test_match_empty(self):
        self.assertFalse(self.CLASS.match(""))

    def test_match_comment_solo(self):
        self.assertFalse(self.CLASS.match("#"))
    def test_match_comment_solo_space(self):
        self.assertFalse(self.CLASS.match(" #"))
    def test_match_comment_space(self):
        self.assertFalse(self.CLASS.match(" # this is a comment"))
    def test_match_comment_no_space(self):
        self.assertFalse(self.CLASS.match("# this is a comment"))
    def test_match_comment_continuation(self):
        self.assertFalse(self.CLASS.match("# this is a comment\\"))

    def test_match_blank_spaces(self):
        self.assertFalse(self.CLASS.match("   "))
    def test_match_blank_tabs(self):
        self.assertFalse(self.CLASS.match("		"))
    def test_match_blank_continuation(self):
        self.assertFalse(self.CLASS.match("   \\"))

    def test_match_simple_directive_just_name(self):
        self.assertFalse(self.CLASS.match("name"))
    def test_match_simple_directive_just_name_leading_space(self):
        self.assertFalse(self.CLASS.match(" name"))
    def test_match_simple_directive_just_name_trailing_space(self):
        self.assertFalse(self.CLASS.match("name "))
    def test_match_simple_directive_just_name_continuation(self):
        self.assertFalse(self.CLASS.match("name\\"))
    def test_match_simple_directive_name_and_args(self):
        self.assertFalse(self.CLASS.match("name something else"))
    def test_match_simple_directive_leading_space(self):
        self.assertFalse(self.CLASS.match("   name something else"))
    def test_match_simple_directive_trailing_space(self):
        self.assertFalse(self.CLASS.match("name something else   "))
    def test_match_simple_directive_continuation(self):
        self.assertFalse(self.CLASS.match("name something else\\"))

    def test_match_complex_directive_empty(self):
        self.assertFalse(self.CLASS.match("<>"))
    def test_match_complex_directive_empty_space(self):
        self.assertFalse(self.CLASS.match("< >"))
    def test_match_complex_directive_just_name(self):
        self.assertTrue(self.CLASS.match("<name>"))
    def test_match_complex_directive_just_name_leading_space(self):
        self.assertTrue(self.CLASS.match("< name>"))
    def test_match_complex_directive_just_name_trailing_space(self):
        self.assertTrue(self.CLASS.match("<name >"))
    def test_match_complex_directive_just_name_open(self):
        self.assertFalse(self.CLASS.match("<name"))
    def test_match_complex_directive_just_name_open_continuation(self):
        self.assertTrue(self.CLASS.match("<name\\"))
    def test_match_complex_directive_just_name_open_space_continuation(self):
        self.assertTrue(self.CLASS.match("<name \\"))
    def test_match_complex_directive_just_name_invalid_1(self):
        self.assertFalse(self.CLASS.match("<na+me>"))
    def test_match_complex_directive_just_name_invalid_2(self):
        self.assertFalse(self.CLASS.match("<na<me>"))
    def test_match_complex_directive_name_and_args_open(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2"))
    def test_match_complex_directive_name_and_args_open_continuation(self):
        self.assertTrue(self.CLASS.match("<name arg1 arg2\\"))
    def test_match_complex_directive_name_and_args_open_space_continuation(self):
        self.assertTrue(self.CLASS.match("<name arg1 arg2 \\"))
    def test_match_complex_directive_closed(self):
        self.assertTrue(self.CLASS.match("<name arg1 arg2>"))
    def test_match_complex_directive_leading_space(self):
        self.assertTrue(self.CLASS.match("  <name arg1 arg2>"))
    def test_match_complex_directive_trailing_space(self):
        self.assertTrue(self.CLASS.match("<name arg1 arg2>  "))
    def test_match_complex_directive_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2>\\"))
    def test_match_complex_directive_space_continuation(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> \\"))
    def test_match_complex_directive_trailing_text(self):
        self.assertFalse(self.CLASS.match("<name arg1 arg2> text"))

    def test_name_new(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.name
    def test_name_header_incomplete(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        self.assertEqual(node.name, "name")
    def test_name_header_complete(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.name, "name")
    def test_name_complete(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual(node.name, "name")

    def test_args_new(self):
        node = self.CLASS()
        self.assertEqual(node.arguments, [])
    def test_args_header_incomplete(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        self.assertEqual(node.arguments, ["arg1",])
    def test_args_header_complete_empty(self):
        node = self.CLASS()
        node.add_line("<name>")
        self.assertEqual(node.arguments, [])
    def test_args_header_complete(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.arguments, ["arg1",])
    def test_args_complete(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual(node.arguments, ["arg1",])

    def test_add_line_complete_1(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.complete = True
    def test_add_line_complete_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_3(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        with self.assertRaises(NodeCompleteError):
            node.add_line("extra")
    def test_add_line_complete_4(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("inner argument1 argument2")
        node.add_line("</name>")
        with self.assertRaises(NodeCompleteError):
            node.add_line("")
    def test_add_line_complete_5(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("inner argument1 argument2")
        node.add_line("</name>")
        with self.assertRaises(NodeCompleteError):
            node.add_line("extra")

    def test_add_line_complete_tail_added_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertTrue(node.body.complete)
    def test_add_line_complete_tail_added_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual(node.tail, "</name>")
    def test_add_line_complete_tail_added_3(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertTrue(node.tailmatch)

    # incomplete header
    def test_add_line_incomplete_header_only_name_lines(self):
        node = self.CLASS()
        node.add_line("<name\\")
        self.assertEqual(node.lines[0], "<name\\")
    def test_add_line_incomplete_header_only_name_header_name(self):
        node = self.CLASS()
        node.add_line("<name\\")
        self.assertEqual(node.header.name, "name")
    def test_add_line_incomplete_header_only_name_header_args(self):
        node = self.CLASS()
        node.add_line("<name\\")
        self.assertEqual(node.header.arguments, [])

    def test_add_line_incomplete_header_only_name_lines_multi_1(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1\\")
        self.assertEqual(node.lines[0], "<name\\")
    def test_add_line_incomplete_header_only_name_lines_multi_2(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1\\")
        self.assertEqual(node.lines[1], "arg1\\")
    def test_add_line_incomplete_header_only_name_header_name_multi(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1\\")
        self.assertEqual(node.header.name, "name")
    def test_add_line_incomplete_header_only_name_header_args_multi(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1\\")
        self.assertEqual(node.header.arguments, ["arg1",])

    def test_add_line_incomplete_header_name_and_arg_lines(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        self.assertEqual(node.lines[0], "<name arg1\\")
    def test_add_line_incomplete_header_name_and_arg_header_name(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        self.assertEqual(node.header.name, "name")
    def test_add_line_incomplete_header_name_and_arg_header_args(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        self.assertEqual(node.header.arguments, ["arg1",])

    def test_add_line_incomplete_header_name_and_arg_lines_multi_1(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2\\")
        self.assertEqual(node.lines[0], "<name arg1\\")
    def test_add_line_incomplete_header_name_and_arg_lines_multi_2(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2\\")
        self.assertEqual(node.lines[1], "arg2\\")
    def test_add_line_incomplete_header_name_and_arg_header_name_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2\\")
        self.assertEqual(node.header.name, "name")
    def test_add_line_incomplete_header_name_and_arg_header_args_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2\\")
        self.assertEqual(node.header.arguments, ["arg1", "arg2"])

    # complete header
    def test_add_line_complete_header_only_name_lines(self):
        node = self.CLASS()
        node.add_line("<name>")
        self.assertEqual(node.lines[0], "<name>")
    def test_add_line_complete_header_only_name_header_name(self):
        node = self.CLASS()
        node.add_line("<name>")
        self.assertEqual(node.header.name, "name")
    def test_add_line_complete_header_only_name_header_args(self):
        node = self.CLASS()
        node.add_line("<name>")
        self.assertEqual(node.header.arguments, [])

    def test_add_line_complete_header_only_name_lines_multi_1(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1>")
        self.assertEqual(node.lines[0], "<name\\")
    def test_add_line_complete_header_only_name_lines_multi_2(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1>")
        self.assertEqual(node.lines[1], "arg1>")
    def test_add_line_complete_header_only_name_header_name_multi(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1>")
        self.assertEqual(node.header.name, "name")
    def test_add_line_complete_header_only_name_header_args_multi(self):
        node = self.CLASS()
        node.add_line("<name\\")
        node.add_line("arg1>")
        self.assertEqual(node.header.arguments, ["arg1",])

    def test_add_line_complete_header_name_and_arg_lines(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.lines[0], "<name arg1>")
    def test_add_line_complete_header_name_and_arg_header_name(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.header.name, "name")
    def test_add_line_complete_header_name_and_arg_header_args(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.header.arguments, ["arg1",])

    def test_add_line_complete_header_name_and_arg_lines_multi_1(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2>")
        self.assertEqual(node.lines[0], "<name arg1\\")
    def test_add_line_complete_header_name_and_arg_lines_multi_2(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2>")
        self.assertEqual(node.lines[1], "arg2>")
    def test_add_line_complete_header_name_and_arg_header_name_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2>")
        self.assertEqual(node.header.name, "name")
    def test_add_line_complete_header_name_and_arg_header_args_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        node.add_line("arg2>")
        self.assertEqual(node.header.arguments, ["arg1", "arg2"])

    # invalid headers
    def test_add_line_incomplete_header_name_and_arg_invalid(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("<name <arg1\\")
    def test_add_line_incomplete_header_name_and_arg_invalid_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("<arg2\\")
    def test_add_line_complete_header_name_and_arg_invalid(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("<name <arg1>")
    def test_add_line_complete_header_name_and_arg_invalid_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("<arg2>")
    def test_add_line_complete_header_name_and_arg_invalid_trailing(self):
        node = self.CLASS()
        with self.assertRaises(InvalidLineError):
            node.add_line("<name arg1>extra")
    def test_add_line_complete_header_name_and_arg_invalid_trailing_multi(self):
        node = self.CLASS()
        node.add_line("<name arg1\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("arg2>extra")

    def test_add_line_after_header(self):
    	# lines after header don't go into self.lines
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        self.assertFalse("something else" in node.lines)
    def test_add_line_complete_check_tail(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertFalse("</name>" in node.lines)
    def test_add_line_not_complete_empty_body_check_body(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        self.assertEqual(node.body.nodes, [])
    def test_add_line_not_complete_not_empty_body_check_body(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        node.add_line("</name>")
        self.assertEqual(len(node.body.nodes), 1)
        self.assertTrue(str(node.body.nodes[0]), "something else")
    def test_add_line_complete_empty_body_check_body(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual(node.body.nodes, [])
    def test_add_line_complete_not_empty_body_check_body(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        node.add_line("</name>")
        self.assertEqual(len(node.body.nodes), 1)
        self.assertTrue(str(node.body.nodes[0]), "something else")
    def test_add_line_invalid_tail_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        with self.assertRaises(NodeMatchError):
            node.add_line("</name arg1>")
    def test_add_line_invalid_tail_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        with self.assertRaises(NodeMatchError):
            node.add_line("</name arg1>")

    def test_add_line_body_not_stable_finish_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  <something else>")
        node.add_line("  </something>")
        node.add_line("</name>")
        self.assertTrue(node.complete)
        self.assertEqual(len(node.body.nodes), 1)
    def test_add_line_body_not_stable_finish_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  something else\\")
        node.add_line("  finally")
        node.add_line("</name>")
        self.assertTrue(node.complete)
        self.assertEqual(len(node.body.nodes), 1)
    def test_add_line_body_not_stable_close_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  <something else>")
        with self.assertRaises(NodeMatchError):
            node.add_line("</name>")
    def test_add_line_body_not_stable_close_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  something else\\")
        with self.assertRaises(InvalidLineError):
            node.add_line("</name>")

    def test___str___empty(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            str(node)
    def test___str___incomplete_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        with self.assertRaises(NodeCompleteError):
            str(node)
    def test___str___incomplete_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.body.complete = True
        with self.assertRaises(NodeCompleteError):
            str(node)
    def test___str___complete_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual(str(node), "<name arg1>\n</name>")
    def test___str___complete_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("    something here")
        node.add_line("</name>")
        self.assertEqual(str(node), "<name arg1>\n    something here\n</name>")

    def test_pprint_new(self):
        node = self.CLASS()
        with self.assertRaises(NodeCompleteError):
            node.pprint()
    def test_pprint_header_only(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        with self.assertRaises(NodeCompleteError):
            node.pprint()
    def test_pprint_not_complete(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        with self.assertRaises(NodeCompleteError):
            node.pprint()
    def test_pprint_depth_0(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n</name>", node.pprint(0))
    def test_pprint_depth_0_spaces(self):
        node = self.CLASS()
        node.add_line("<name     arg1>")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n</name>", node.pprint(0))
    def test_pprint_depth_0_tab(self):
        node = self.CLASS()
        node.add_line("<name	arg1>")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n</name>", node.pprint(0))
    def test_pprint_depth_0_nested(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something here")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n"+INDENT+"something here\n</name>", node.pprint(0))
    def test_pprint_depth_0_nested_indented_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  something here")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n"+INDENT+"something here\n</name>", node.pprint(0))
    def test_pprint_depth_0_nested_indented_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("    something here")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n"+INDENT+"something here\n</name>", node.pprint(0))
    def test_pprint_depth_1(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual("%s<name arg1>\n%s</name>" % ((INDENT,)*2), node.pprint(1))
    def test_pprint_depth_1_nested(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something here")
        node.add_line("</name>")
        self.assertEqual("%s<name arg1>\n%s%ssomething here\n%s</name>" % ((INDENT,)*4), node.pprint(1))
    def test_pprint_depth_1_nested_indented(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("    something here")
        node.add_line("</name>")
        self.assertEqual("%s<name arg1>\n%s%ssomething here\n%s</name>" % ((INDENT,)*4), node.pprint(1))
    def test_pprint_depth_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("</name>")
        self.assertEqual("%s%s<name arg1>\n%s%s</name>"  % ((INDENT,)*4), node.pprint(2))
    def test_pprint_leading_space_1(self):
        node = self.CLASS()
        node.add_line("  <name arg1>")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n</name>", node.pprint())
    def test_pprint_leading_space_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("  </name>")
        self.assertEqual("<name arg1>\n</name>", node.pprint())
    def test_pprint_leading_space_3(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("something else")
        node.add_line("</name>")
        self.assertEqual("<name arg1>\n%ssomething else\n</name>" % INDENT, node.pprint())

    def test_complete_1(self):
        node = self.CLASS()
        node.header.name = "name"
        node.header.complete = True
        node.body.complete = True
        node.tailmatch = True
        self.assertTrue(node.complete)
    def test_complete_2(self):
        node = self.CLASS()
        node.add_line("<name arg1>")
        node.add_line("    inner 5")
        node.add_line("</name>")
        self.assertTrue(node.complete)
    def test_complete_new_1(self):
        node = self.CLASS()
        self.assertFalse(node.complete)
    def test_complete_new_2(self):
        node = self.CLASS()
        node.header.complete = False
        node.body.complete = False
        node.tailmatch = False
        self.assertFalse(node.complete)
    def test_complete_order_1(self):
        node = self.CLASS()
        node.header.name = "name"
        node.header.complete = True
        node.body.complete = False
        node.tailmatch = False
        self.assertFalse(node.complete)
    def test_complete_order_2(self):
        node = self.CLASS()
        node.header.name = "name"
        node.header.complete = True
        node.body.complete = True
        node.tailmatch = False
        self.assertFalse(node.complete)
    def test_complete_order_3(self):
        node = self.CLASS()
        node.header.name = "name"
        node.header.complete = True
        node.body.complete = False
        node.tailmatch = True
        with self.assertRaises(NodeCompleteError):
            node.complete
    def test_complete_order_4(self):
        node = self.CLASS()
        node.header.complete = False
        node.body.complete = False
        node.tailmatch = True
        with self.assertRaises(NodeCompleteError):
            node.complete
    def test_complete_order_5(self):
        node = self.CLASS()
        node.header.complete = False
        node.body.complete = True
        node.tailmatch = False
        with self.assertRaises(NodeCompleteError):
            node.complete
    def test_complete_order_6(self):
        node = self.CLASS()
        node.header.complete = False
        node.body.complete = True
        node.tailmatch = True
        with self.assertRaises(NodeCompleteError):
            node.complete
        

class TestComplexNode(u_mod.TestCase):
    CLASS = ComplexNode
    #def test___str___empty(self):
    #    node = self.CLASS()
    #    with self.assertRaises(NodeCompleteError):
    #        str(node)
    #@u_mod.skip("works if add_line on a complete node sets changed instead of raising.")
    #def test___str___multiple(self):
    #    line1 = "first"
    #    line2 = "second"
    #    node = self.CLASS()
    #    node.add_line(line1)
    #    node.add_line(line2)
    #    self.assertEqual(line1+"\n"+line2, str(node))
    #def test___str___new(self):
    #    line = "first"
    #    node = self.CLASS()
    #    node.add_line(line)
    #    self.assertEqual(line, str(node))
    #def test___str___changed(self):
    #    # should match self.content
    #    line = "first"
    #    node = self.CLASS()
    #    node.add_line(line)
    #    node.changed = True
    #    self.assertEqual(line, str(node))

    #def test_pprint_empty(self):
    #    node = self.CLASS()
    #    self.assertEqual("", node.pprint())
    #def test_pprint_empty_depth_0(self):
    #    node = self.CLASS()
    #    self.assertEqual("", node.pprint(0))
    #def test_pprint_empty_depth_1(self):
    #    node = self.CLASS()
    #    self.assertEqual(INDENT, node.pprint(1))
    #def test_pprint_empty_depth_1_keyword(self):
    #    node = self.CLASS()
    #    self.assertEqual(INDENT, node.pprint(depth=1))
    #def test_pprint_empty_depth_2(self):
    #    node = self.CLASS()
    #    self.assertEqual(INDENT*2, node.pprint(2))
    #def test_pprint_blank_depth_0(self):
    #    node = self.CLASS()
    #    node.add_line("")
    #    self.assertEqual("", node.pprint(0))
    #def test_pprint_blank_depth_1(self):
    #    node = self.CLASS()
    #    node.add_line("")
    #    self.assertEqual(INDENT, node.pprint(1))
    #def test_pprint_blank_depth_2(self):
    #    node = self.CLASS()
    #    node.add_line("")
    #    self.assertEqual(INDENT*2, node.pprint(2))
    #def test_pprint_depth_0(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertEqual("first", node.pprint(0))
    #def test_pprint_depth_1(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertEqual(INDENT+"first", node.pprint(1))
    #def test_pprint_depth_2(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertEqual(INDENT*2+"first", node.pprint(2))

    """
    def __init__(self, candidates):
        super(ComplexNode, self).__init__()
        self.candidates = candidates
        self.nodes = []

    def get_node(self, line):
        for node_cls in self.candidates:
            if node_cls.match(line):
                return node_cls()
        raise NodeMatchError("No matching node: %s" % line)

    def add_line(self, line, depth=0):
        if self.nodes and not self.nodes[-1].complete:
            self.nodes[-1].add_line(line, depth=depth+1)
        else:
            newnode = self.get_node(line)
            newnode.add_line(line)
            self.nodes.append(newnode)

    def __str__(self):
        return "".join(node for node in self.nodes)
    """
    #def test_add_line_complete_1(self):
    #    node = self.CLASS()
    #    node.complete = True
    #    with self.assertRaises(NodeCompleteError):
    #        node.add_line("")
    #def test_add_line_complete_2(self):
    #    node = self.CLASS()
    #    node.add_line("")
    #    with self.assertRaises(NodeCompleteError):
    #        node.add_line("")
    #def test_add_line_complete_3(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    with self.assertRaises(NodeCompleteError):
    #        node.add_line("second")
    #def test_add_line_added_first(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertEqual(node.lines[0], "first")
    #def test_add_line_added_second(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    node.complete = False
    #    node.add_line("second")
    #    self.assertEqual(node.lines[0], "first")
    #    self.assertEqual(node.lines[1], "second")
    #def test_add_line_autocomplete(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertTrue(node.complete)
    #def test_add_line_autochanged(self):
    #    node = self.CLASS()
    #    node.add_line("first")
    #    self.assertFalse(node.changed)
    #def test_add_line_continuation(self):
    #    node = self.CLASS()
    #    node.add_line("first\\")
    #    self.assertFalse(node.complete)
    #def test_add_line_space_continuation(self):
    #    node = self.CLASS()
    #    node.add_line("first \\")
    #    self.assertFalse(node.complete)


class TestApacheConfParser(u_mod.TestCase):
    """
    def __init__(self, source, infile=True, delay=False):
        super(Parser, self).__init__(NODES)
	self.source = source.splitlines()
	if infile:
            self.source = (line.strip("\n") for line in open(source))
        if not delay:
            self.parse()

    def parse(self):
        if self.complete:
            return
        for line in self.source:
            self.add_line(line)
        self.complete = True
    """            

if __name__ == '__main__':
    u_mod.main()
