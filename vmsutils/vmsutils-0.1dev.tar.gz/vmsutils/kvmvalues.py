"""

This script show some free, or random values:

uuid: random
mac address: random
vnc port: first available top of 5900

"""

def values():
    """ The function"""

    ##############################
    # CONFIGURATION
    ##############################
    
    macprefix = "52:54"
    vncportbase = 5900
    
    ##############################
    # START OF SCRIPT
    ##############################
    
    from os import walk, path
    from random import randint
    from uuid import uuid1
    from xml.etree import ElementTree
    import libvirt
    
    intro = """
Values usable for a new Virtual Machine
---------------------------------------
    """
    
    out = ("\n%s\n" % intro.strip()).split('\n')
    
    
    ##############################
    # UUID
    ##############################
    
    out.append("uuid: %s" % uuid1())
    
    
    ##############################
    # MAC ADDRESS
    ##############################
    
    mac = [int(item,16) for item in macprefix.split(':')]
    mac.extend([randint(1,254) for i in range(len(mac),6)])
    out.append("mac address: %s" % ":".join(["%x" % item for item in mac]))
    
    
    ##############################
    # FIRST FREE VNC DISPLAY PORT
    ##############################
    
    # list all xml files into xmlroot
    vncports = []
    conn = libvirt.open('qemu:///system')
    active_domains = [conn.lookupByID(item) for item in conn.listDomainsID()]
    inactive_domains = [conn.lookupByName(item) for item in conn.listDefinedDomains()]
    
    for domain in active_domains + inactive_domains:
        xml = domain.XMLDesc(0) # why pass 0? good question
        tree = ElementTree.fromstring(xml)
        for graphic in tree.findall('devices/graphics'):
            if 'port' in graphic.attrib:
                vncports.append( int(graphic.attrib['port']) )
    
    # if we have a list of n unique element, and a list of n + 1 element,
    # the difference between the second by the first return at least one
    # element
    availables_port = set(range(vncportbase, vncportbase + len(vncports) + 2)).difference(vncports)
    availables_port = list(availables_port)
    availables_port.sort()
    out.append('vnc port: %i' % availables_port[0])
    
    ##############################
    # END OF SCRIPT
    ##############################
    
    out.append('')
    print "\n".join(out)
