"""
This Report class is used in conjunction with the Generator class.

After the Generator performs is tasks, the information contained within it
should be given to the user in a digestable form that allows them to decide
what the next course of action is.

This report formats the data the generator has been reponsible for creating.

By making this object responsible for output regarding the results of the
generation, we can let the Generator class do it's work and pass it's results
off to another object.  This keeps the output uniform, and prevents duplication
of this feature.
"""
import textwrap
import collections

Report = collections.namedtuple('Report',
    'from_dir out_dir tmp_dir source_count generated_count entry_point')

def dump(self):
    print textwrap.dedent("""
    Source rST files .......... (%(source_count)s files) %(from_dir)s 
    Used the template ......... %(tmp_dir)s
    Created ................... %(out_dir)s
    """ % self._asdict())

setattr(Report, 'dump', dump)
