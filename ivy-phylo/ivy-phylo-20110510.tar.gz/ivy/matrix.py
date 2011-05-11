"""
Functions for dealing with trees as matrices.
"""

def vcv(root):
    "leaf variances and covariances"
    from collections import defaultdict
    leafdists = root.leaf_distances()
    var = defaultdict(float)
    cov = defaultdict(float)
    for node in root.postiter(lambda x: x.children):
        c = sum([ x.length for x in node.rootpath(root) if x.parent ])
        dists = leafdists[node]
        leaves = dists.keys()
        for lf1 in leaves:
            for lf2 in leaves:
                if lf1 is not lf2:
                    k = frozenset((lf1, lf2))
                    v = dists[lf1] + dists[lf2]
                    if (k not in var) or (k in var and var[k] > v):
                        var[k] = v
                        cov[k] = c
    return var, cov

## def vcv(root, labels=None):
##     """
##     Compute the variance-covariance matrix.
##     """
##     labels = labels or [ lf.label for lf in root.leaves() ]
##     N = len(labels)
##     var = [ [ 0 for x in labels ] for y in labels ]
##     cov = [ [ None for x in labels ] for y in labels ]
##     d = root.leaf_distances()
##     for i in range(N):
##         for j in range(i+1, N):
##             li = labels[i]
##             lj = labels[j]
##             for n in root.postiter():
##                 l2d = d[n]
##                 if (not n.isleaf) and (li in l2d) and (lj in l2d):
##                     dist = l2d[li] + l2d[lj]
##                     var[i][j] = dist
##                     cov[i][j] = sum([ x.length for x in n.rootpath()
##                                       if x.parent ])
##                     break
##     return var, cov
