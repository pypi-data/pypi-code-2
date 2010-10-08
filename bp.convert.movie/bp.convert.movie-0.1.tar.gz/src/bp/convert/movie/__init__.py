#!/usr/bin/env python2.6
# encoding: utf-8
"""
__init__.py

Created by disko on 2010-08-29.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import cmdln
import handbrake
import sys



# IMPLEMENTATION

class BPConvertMovie(cmdln.Cmdln):
    
    name = "bp_convert_movie"
    
    @cmdln.alias("p")
    @cmdln.option("-d", "--debug",      action="store_true", help="print debug information")
    @cmdln.option("-v", "--verbose",    action="store_true", help="include the preset settings in output")
    def do_list_presets(self, subcmd, opts):
        """${cmd_name}: list available conversion presets
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
        
        presets = handbrake.Handbrake().presets
        for preset_group in presets:
            print preset_group + "\n" + "="*len(preset_group)
            for preset in presets[preset_group]:
                if opts.verbose:
                    preset_description = "(%s)" % presets[preset_group][preset]
                else:
                    preset_description = ""
                print " ", preset, preset_description
            print
        
    
    @cmdln.alias("c")
    @cmdln.option("-d", "--debug",      action="store_true", help="print debug information")
    @cmdln.option("-v", "--verbose",    action="store_true", help="print extra information")
    def do_convert(self, subcmd, opts, preset="Normal", *paths):
        """${cmd_name}: convert a movie file using the given preset.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        for path in paths:
            cmd_stdout = subprocess.Popen([HANDBRAKE, "--preset", preset, "-i", '"%s"' % path, "-o", '"%s.mp4"' % path], stdout=subprocess.PIPE).stdout
            for l in cmd_stdout:
                print l
        
        return
    


def main():
    """main entry point"""
    
    bcm = BPConvertMovie()
    sys.exit(bcm.main())


if __name__ == '__main__':
    main()
