from pywalk import walk

def test_leaf_replacement():
    tree =  [ 5, 6, -3, [ 7, 8, -2, 1 ], { 'f' : 10, 'g' : -13 } ]
    @walk(tree)
    def negatives_suck(node):
        if node.is_leaf and node.value < 0:
            node.set(-node.value)

    assert(tree == [ 5, 6, 3, [ 7, 8, 2, 1 ], { 'f' : 10, 'g' : 13 } ])
