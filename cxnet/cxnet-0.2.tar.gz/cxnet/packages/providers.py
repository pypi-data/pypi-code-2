import packages
import os
import shelve

"""Get and store the providers.

virtual package:
  A package which can be in dependencies, but does not exists.
  Some packages can provide it.

  E.g. editor
  vim and other packages provides it.
  See the result of::

    apt-cache show vim

provider:
  A package which provides a virtual package.

providers:
  provider -> virtual packages direction

reverese providers:
  virtual package -> providers direction

"""
#TODO to_file and from_file file=???

def get_providers():
    """provider -> virtual package direction
    
    It can be very slow."""

    names=packages.pkg_names()

    prov = []
    for name in names:
	os.system("apt-cache show %s>temp" % name)
	f=open("temp")
	lines = f.readlines()
	f.close()
	for line in lines:
	    if line.startswith("Provides"):
		prov.append((name, line.split(None,1)[1]))

    print prov

    s=shelve.open("prov.db")
    s["prov"]=prov
    s.close()

def reverse_prov():
    """virtual package -> providers direction
    
    :Returns:
    
    A dictionary with virtual:list_of_providers items.
    
    """
    s=shelve.open("prov.db")
    prov = s["prov"]
    rprov={}
    for name, pr in prov:
	for p in pr:
	    if p in rprov:
		rprov[p].append(name)
	    else:
		rprov[p]=[name]
    s["reverse prov"]=rprov
    s.close()

    return rprov
 
def reverse_prov_to_file(file="ubuntu_packages_reverse_prov.txt"):
    """Stores reverese providers in a file to archive."""

    f=open(file, "w")
    f.write("""# Lists virtual packages with the packages provides them. 
# <virtual package> <-- <prov1>:<prov2>:...

""")

    for k in rprov.keys():
	f.write("%s <-- %s\n" %(k, ":".join(rprov[k])) )
    f.close()

def reverse_prov_from_file(file="ubuntu_packages_reverse_prov.txt"):
    """Recall reverese providers from an archive file."""

    f=open(file)

    while True:
	line = f.readline()
	if not line.startswith("#") and len(line)>1 :
	    break
    
    lines = f.readlines()
    lines = [line.split() for line in lines]

    rprov = {}
    for virtual, arrow, packages in lines:
	rprov[virtual] = packages.split(":")
    return rprov

def get_reverse_providers(virtual_packages=["editor"]):
    import popen2
    reverse_providers ={}
    for vpackage in virtual_packages:
	fin, fout = popen2.popen2("apt-cache showpkg %s" % vpackage)
	lines=fin.readlines()
	ix = lines.index("Reverse Provides: \n") + 1
	providers = [line.split()[0] for line in lines[ix:] ]
	reverse_providers[vpackage] = providers
	print "** %s **" % vpackage
	print ", ".join(providers)
    return reverse_providers

def store_reverse_providers():

    G=packages.get_graph()
    names=packages.pkg_names(with_summary=False)
    names=set(packages.pkg_names(with_summary=False))
    nodes=set([str(node) for node in G.nodes()])
    nodes-names
    virt=nodes-names
    len(virt)
    rprov = get_reverse_providers(virt)

    s=shelve.open("prov.db")
    s["Reverse Provider"]=rprov
    s.close()
