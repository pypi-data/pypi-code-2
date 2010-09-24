import svectors

# dot product (= cosine if vectors are normalized)

VECTORS = {"man": {1:0.456, 4:0.123, 7:0.765},
           "tree": {2:0.836, 4:0.898, 7:0.234, 9:0.231},
           "house": {1:0.913, 2:0.021, 9:0.923}}

svectors.write_dotimage(VECTORS, "dot_test.img")
data = svectors.load_image("dot_test.img")
print(data.dot("man", "tree"))


# bounded Jiang-Conrath similarity (= JC/(1+JC))

PATH = "/proj/corpora/wordnet/3.0/dict"
FREQ = {("man", "N"): 17, ("tree", "N"): 234, ("sleep", "V"): 3}

svectors.write_bjcimage(PATH, FREQ, "bjc_test.img")
data = svectors.load_image("bjc_test.img")
print(data.bjc("manN", "treeN"))
