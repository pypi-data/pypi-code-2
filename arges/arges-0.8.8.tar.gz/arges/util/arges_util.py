# -*- coding: latin-1 -*-


import strings
import files


import re
"""This file contains ARGES specific utilities"""



def add_execution_options(parser):
    parser.add_option("-t", "--test-file", 
                      dest = "test_file", 
                      help = "It's the test file that it's going to be processed. (mandatory)")
    
    parser.add_option("-d", "--data-file", 
                      dest = "data_file", 
                      help = "It's the data file that it's going to be used for the test file.\
If no data file is supplied, <test-file>.tdata will be used")
    
    parser.add_option("-r", "--rat-dir", 
                      dest = "rat_dir", 
                      help = "It's the directory where the log, test and data files will be written and looked up for.\
If no directory is supplied, the user's home directory will be used.")
    
    parser.set_defaults(generate = False)
    parser.add_option("-g", "--generate-tdata",
                      action = "store_true", 
                      dest = "generate", 
                      help = """Generates a .tdata file of the .tfile. 
                      The .tfile can be a tcase, ucase or tsuite.""" )

       
        
def get_only_one_value(param, section, params_list):
    """ 
        This method validates that only 1 value exists for a given param in 
        all params
    """
    
    value = None
    for params_dict in params_list:
        if strings.formatTestParameter(param) in params_dict:
            if value is None:
                value = params_dict[strings.formatTestParameter(param)]
            else:
                if value != params_dict[strings.formatTestParameter(param)]:
                    msg = "I'm sorry but there are multiple values for %s in section %s" % (param, section)
                    raise NameError, msg
    
    return value

    
def have_to_continue(line):
    return files.lineIsComment(line) or files.lineIsBlank(line) 


def replace_variables(line, 
                      parameters,
                      other_params,
                      logging, 
                      get_sect_par = lambda key: key.group().split(".")
                      ):
    """
        Given the parameter list, this function replace it's values
        by the previous parameters values.
        
        return True if the value has changed.
    """
    
    something_changed = False
    
    if line is None:
        return something_changed, line
    
    only_param_regex = re.compile("(\${\w+})")
    ext_param_regex = re.compile("\${\w+\.*\w*}\.\${\w+}")
    
    replaceable_values = "${}"
    
    
    original_value = line
    
    for key in only_param_regex.finditer(line):
        key_value = key.group()
        
        if strings.formatTestParameter(key_value) in parameters:
            value = parameters[strings.formatTestParameter(key_value)]
            line = line.replace(key_value, value)
        else:
            logging.info(" %s not found in local parameters" % key_value )
        
        if original_value != line:
            something_changed = True


    for key in ext_param_regex.finditer(line):
        section, param = get_sect_par(key)
        
        for c in replaceable_values:
            section = section.replace(c, "")
                        
        # I get the parameters from other section
        if section in other_params:
            ext_section_list_params = other_params[section]
        else:
            logging.info(" %s section not found" % section )
            
        value = get_only_one_value(param, section, ext_section_list_params)
        line = ext_param_regex.sub(value, line)
            
    return something_changed, line




def get_filled_config_parser(dst_tdata_filename, section):
    """ 
        This function fills a new SafeConfigParser with the contents of the dst_tdata_filename
        section.
    """
    data_file = open(dst_tdata_filename, "a+")
    
    p = SafeConfigParser()
    
    # This method is overriden because otherwise, it'll lowercase all the params.
    p.optionxform = lambda x: str(x)
    
    existing_params = set()
    
    try:
        p.readfp(data_file)
        if p.has_section(section):
            existing_params.update(p.options(section))
        else:
            p.add_section(section)

    except MissingSectionHeaderError:
        p.add_section(section)

    data_file.close()
    
    return p, existing_params
        
                