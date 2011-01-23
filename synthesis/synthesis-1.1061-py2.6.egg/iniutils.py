import ConfigParser
# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import string
import sys

_ConfigDefault = {
    "database.dbms":            "mysql",
    "database.name":            "",
    "database.user":            "root",
    "database.password":        "",
    "database.host":            "127.0.0.1"
    }

def LoadConfig(file, config={}):
    """
    returns a dictionary with keys of the form
    <section>.<option> and the corresponding values
    """
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    
    for sec in cp.sections():
        name = string.lower(sec)
        for opt in cp.options(sec):
            config[name + "." + string.lower(opt)] = string.strip(
                cp.get(sec, opt))
    return config
    
if __name__=="__main__":
#    print LoadConfig("some.ini", _ConfigDefault)
    newConfig =  LoadConfig("fileConverter.ini", _ConfigDefault)
    #print newConfig
    #print DumpConfig("fileConverter.new.ini", newConfig)