"""XML reporting for coverage.py"""

import os, sys, time
import xml.dom.minidom

from coverage import __url__, __version__
from coverage.backward import sorted            # pylint: disable-msg=W0622
from coverage.report import Reporter

def rate(hit, num):
    """Return the fraction of `hit`/`num`, as a string."""
    return "%.4g" % (float(hit) / (num or 1.0))


class XmlReporter(Reporter):
    """A reporter for writing Cobertura-style XML coverage results."""

    def __init__(self, coverage, ignore_errors=False):
        super(XmlReporter, self).__init__(coverage, ignore_errors)

        self.packages = None
        self.xml_out = None
        self.arcs = coverage.data.has_arcs()

    def report(self, morfs, outfile=None, config=None):
        """Generate a Cobertura-compatible XML report for `morfs`.

        `morfs` is a list of modules or filenames.

        `outfile` is a file object to write the XML to.  `config` is a
        CoverageConfig instance.

        """
        # Initial setup.
        outfile = outfile or sys.stdout

        # Create the DOM that will store the data.
        impl = xml.dom.minidom.getDOMImplementation()
        docType = impl.createDocumentType(
            "coverage", None,
            "http://cobertura.sourceforge.net/xml/coverage-03.dtd"
            )
        self.xml_out = impl.createDocument(None, "coverage", docType)

        # Write header stuff.
        xcoverage = self.xml_out.documentElement
        xcoverage.setAttribute("version", __version__)
        xcoverage.setAttribute("timestamp", str(int(time.time()*1000)))
        xcoverage.appendChild(self.xml_out.createComment(
            " Generated by coverage.py: %s " % __url__
            ))
        xpackages = self.xml_out.createElement("packages")
        xcoverage.appendChild(xpackages)

        # Call xml_file for each file in the data.
        self.packages = {}
        self.report_files(self.xml_file, morfs, config)

        lnum_tot, lhits_tot = 0, 0
        bnum_tot, bhits_tot = 0, 0

        # Populate the XML DOM with the package info.
        for pkg_name in sorted(self.packages.keys()):
            pkg_data = self.packages[pkg_name]
            class_elts, lhits, lnum, bhits, bnum = pkg_data
            xpackage = self.xml_out.createElement("package")
            xpackages.appendChild(xpackage)
            xclasses = self.xml_out.createElement("classes")
            xpackage.appendChild(xclasses)
            for class_name in sorted(class_elts.keys()):
                xclasses.appendChild(class_elts[class_name])
            xpackage.setAttribute("name", pkg_name.replace(os.sep, '.'))
            xpackage.setAttribute("line-rate", rate(lhits, lnum))
            xpackage.setAttribute("branch-rate", rate(bhits, bnum))
            xpackage.setAttribute("complexity", "0")

            lnum_tot += lnum
            lhits_tot += lhits
            bnum_tot += bnum
            bhits_tot += bhits

        xcoverage.setAttribute("line-rate", rate(lhits_tot, lnum_tot))
        xcoverage.setAttribute("branch-rate", rate(bhits_tot, bnum_tot))

        # Use the DOM to write the output file.
        outfile.write(self.xml_out.toprettyxml())

    def xml_file(self, cu, analysis):
        """Add to the XML report for a single file."""

        # Create the 'lines' and 'package' XML elements, which
        # are populated later.  Note that a package == a directory.
        dirname, fname = os.path.split(cu.name)
        dirname = dirname or '.'
        package = self.packages.setdefault(dirname, [ {}, 0, 0, 0, 0 ])

        xclass = self.xml_out.createElement("class")

        xclass.appendChild(self.xml_out.createElement("methods"))

        xlines = self.xml_out.createElement("lines")
        xclass.appendChild(xlines)
        className = fname.replace('.', '_')
        xclass.setAttribute("name", className)
        ext = os.path.splitext(cu.filename)[1]
        xclass.setAttribute("filename", cu.name + ext)
        xclass.setAttribute("complexity", "0")

        branch_stats = analysis.branch_stats()

        # For each statement, create an XML 'line' element.
        for line in analysis.statements:
            xline = self.xml_out.createElement("line")
            xline.setAttribute("number", str(line))

            # Q: can we get info about the number of times a statement is
            # executed?  If so, that should be recorded here.
            xline.setAttribute("hits", str(int(not line in analysis.missing)))

            if self.arcs:
                if line in branch_stats:
                    total, taken = branch_stats[line]
                    xline.setAttribute("branch", "true")
                    xline.setAttribute("condition-coverage",
                        "%d%% (%d/%d)" % (100*taken/total, taken, total)
                        )
            xlines.appendChild(xline)

        class_lines = len(analysis.statements)
        class_hits = class_lines - len(analysis.missing)

        if self.arcs:
            class_branches = sum([t for t,k in branch_stats.values()])
            missing_branches = sum([t-k for t,k in branch_stats.values()])
            class_br_hits = class_branches - missing_branches
        else:
            class_branches = 0.0
            class_br_hits = 0.0

        # Finalize the statistics that are collected in the XML DOM.
        xclass.setAttribute("line-rate", rate(class_hits, class_lines))
        xclass.setAttribute("branch-rate", rate(class_br_hits, class_branches))
        package[0][className] = xclass
        package[1] += class_hits
        package[2] += class_lines
        package[3] += class_br_hits
        package[4] += class_branches
