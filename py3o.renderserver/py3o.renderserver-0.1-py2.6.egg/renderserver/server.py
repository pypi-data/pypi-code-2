import logging
logging.basicConfig(level=logging.DEBUG)

from twisted.internet import reactor
from tgscheduler import scheduler

from pyf.transport.packets import Packet
from pyf.station import FlowServer
from pyf.station.utils import base64encoder, base64decoder, file_to_packets, packets_to_file
from pyjon.utils import get_secure_filename
from pyjon.utils import create_function

import os
import sys
import time
import optparse
#from py3o.renderers.pyuno import Convertor, formats
from py3o.renderers.juno import Convertor, formats

def render(header, flow, callback, soffice_host, soffice_port):
    input_filename = get_secure_filename()
    output_filename = get_secure_filename()

    packets_to_file(flow, input_filename, callback)
    format = formats[header.target_format.upper()]

    convertor = Convertor(soffice_host, soffice_port)
    convertor.convert(input_filename, output_filename, format)
        
    return output_filename

def dispatcher(flow, client=None, soffice_host=None, soffice_port=None):
    header = flow.next()

    if header.action == 'render':
        callback = lambda key, value, **kwargs: client.message(
                Packet(dict(type='appinfo', key=key, value=value, **kwargs)))

        if header.target_format.upper() in formats.iterkeys():
            output_filename = render(header, base64decoder(flow), callback,
                    soffice_host, soffice_port
                    )

        else:
            raise ValueError, "Unsupported format %s" % header.target_format
        
        callback("render_status", "ok", filename=output_filename)
        for data in base64encoder(
                file_to_packets(open(output_filename, 'rb'))):
            client.message(data)

        client.success("Process ended successfully")
        os.unlink(output_filename)

    else:
        raise ValueError, "Unsupported action %s" % header.action

    logging.info("end of flow...")


def cmd_line_server():
    optparser = optparse.OptionParser()

    optparser.add_option(
        "-a", "--sofficehost",
        dest="soffice_host",
        help="specify the open office hostname/ip address ADDR",
        metavar="ADDR",
        default="127.0.0.1")

    optparser.add_option(
        "-p", "--sofficeport",
        dest="soffice_port",
        help="specify the open office port PORT",
        metavar="PORT",
        default="8997")

    optparser.add_option(
        "-l", "--listenport",
        dest="listen_port",
        help="specify the PORT on which our service will listen",
        metavar="PORT",
        default=8994)

    optparser.add_option(
        "-d", "--driver",
        dest="driver",
        help="choose a driver between juno & pyuno",
        default='juno')

    optparser.add_option(
        "-j", "--java",
        dest="javalib",
        help="choose a jvm.dll/jvm.so to use if you are using the juno driver",
        default=None)

    optparser.add_option(
        "-m", "--maxmem",
        dest="maxmem",
        help="how much memory to give to the JVM if you are using juno driver, default is 150Mb",
        default=150)

    (options, args) = optparser.parse_args()

    if os.name in ('nt', 'os2', 'ce'):
        # on windows we expect to find OO in the registry
        base_ooregkey = '''SOFTWARE\\OpenOffice.org\\OpenOffice.org'''

        import _winreg
        # TODO: make sure that we do not explode in flight when the key is not present...
        # TODO: maybe we could use something else than just LOCAL_MACHINE ?
        base_key = _winreg.HKEY_LOCAL_MACHINE
        try:
            key = _winreg.OpenKey(base_key, base_ooregkey)
            # first entry should be 2.3 or something similar
            version = _winreg.EnumKey(key, 0)

            #_winreg.CloseKey(key)
            key = _winreg.OpenKey(base_key, "%s\\%s" % (base_ooregkey, version))

        except WindowsError:
            # some error occured:
            # Open Office is not installed on this machine!
            raise ValueError('OpenOffice is not installed on this Windows host')

        soffice_bin, key_type = _winreg.QueryValueEx(key, 'Path')
        soffice_dir = os.path.dirname(soffice_bin)
        soffice_rootdir = os.path.split(soffice_dir)[0]

        # add to search path for uno import!
        sys.path.insert(0, soffice_dir)

        if options.javalib is None and options.driver == 'juno':
            # we need java for juno support so we try to find it ourselves
            try:
                base_java_key = '''SOFTWARE\\JavaSoft\\Java Runtime Environment'''
                key = _winreg.OpenKey(base_key, base_java_key)
                numversions = _winreg.QueryInfoKey(key)[0]
                last_version = _winreg.EnumKey(key, numversions - 1) 
                if numversions > 1:
                    logging.warning('Multiple Java versions found, using the highest: %s' % last_version)

                javakey = _winreg.OpenKey(base_key, "%s\\%s" % (base_java_key, last_version))
                jvm, key_type = _winreg.QueryValueEx(javakey, 'RuntimeLib')

            except WindowsError:
                # some error occured:
                # Java is not (correctly?) installed on this machine!
                raise ValueError('Java is not installed on this Windows host')

        else:
            # we should test if the given library path points to something real
            jvm = options.javalib

    else:
        # TODO: detect OOo home
        # for now, hard-code stuff where it is on CentOS 5.5 x86_64 with OOo3.1
        soffice_rootdir = '/usr/lib64/openoffice.org'

        if options.javalib is None and options.driver == 'juno':
            # TODO: detect java home
            # for now, hard-code stuff where it is on CentOS 5.5 x86_64 with OpenJDK6
            jvm = '/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64/jre/lib/amd64/server/libjvm.so'

        else:
            # we should test if the given library path points to something real
            jvm = options.javalib


    if options.driver == 'juno':
        from py3o.renderers.juno import start_jvm
        start_jvm(jvm, soffice_rootdir, int(options.maxmem))

    scheduler.start_scheduler()

    factory = FlowServer(create_function(dispatcher,
                kwargs=dict(
                        soffice_host=options.soffice_host,
                        soffice_port=options.soffice_port)))

    reactor.listenTCP(int(options.listen_port), factory)
    scheduler.add_single_task(reactor.run,
                              kw=dict(installSignalHandlers=0),
                              initialdelay=0)

    while True:
        time.sleep(1)


