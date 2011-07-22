import argparse

parser = argparse.ArgumentParser(prog='pysurfer')
parser.add_argument("subject_id",
                    help="subject id as in subjects dir")
parser.add_argument("hemi", metavar="hemi", choices=["lh", "rh"],
                    help="hemisphere to load")
parser.add_argument("surf",
                    help="surface mesh (e.g. 'pial', 'inflated')")
parser.add_argument("-no-curv", action="store_false", dest="curv",
                    help="do not display the binarized surface curvature")
parser.add_argument("-morphometry", metavar="MEAS",
                    help="load morphometry file (e.g. thickness, curvature")
parser.add_argument("-overlay", metavar="FILE",
                    help="load scalar overlay file")
parser.add_argument("-range", metavar=('MIN', 'MAX'), nargs=2,
                    help="overlay threshold and saturation point")
parser.add_argument("-min", type=float,
                    help="overlay threshold")
parser.add_argument("-max", type=float,
                    help="overlay saturation point")
parser.add_argument("-sign", default="abs", choices=["abs", "pos", "neg"],
                    help="overlay sign")
parser.add_argument("-name",
                    help="name to use for the overlay")
