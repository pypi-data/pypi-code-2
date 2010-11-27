#!/usr/bin/env python
import sys
import os

try:
  from optparse import OptionParser
  import StringIO
  import datetime
except ImportError, e:
  print 'file', __file__ ,e
  sys.exit(1)

try:
  from yapbib import biblist
  import query_ads.query_ads as ads
except ImportError, e:
  print 'Import Error', __file__ ,e
  sys.exit(1)

# usuarios={
#   'Einstein':{'nombre':"Einstein,A.",'mail':'mymail@mydomain.org'},
#   }
# check_strict_list= ['Sanchez',u'S\xe1nchez','Suarez', u'Su\xe1rez']  # Nombres comunes, que solo se agregaran si pasan el siguiente test
# check_strict_cond=[('affiliation', 'Bariloche',True)]

# def check_conditions(item,who,what):
#   """Check conditions on some authors (who) and only keep them if the condition 'what' is true"""
#   autores = [ k[1] for k in item['author']] # Last Name of all authors
  
#   keep_item=True
#   for aut in who:  # A quienes controlamos
#     if aut in autores:  keep_item=False # Tenemos que controlarlos
#   if keep_item:    return True  # No hay que controlarlos

#   for w in what:
#     if item.has_key(w[0]) != w[2]: # No existe el campo requerido (affiliation)
#       return False

#     for aut in who:  # A quienes controlamos
#       try:
#         j=autores.index(aut) 
#         keep_item= False
#       except:
#         continue
#       if (item[w[0]][j].find(w[1]) !=-1 ) == w[2]:
#         return True
#   return keep_item

def main():
  '''Retrieve papers list'''
  # Declara algunas variables
  autores="Einstein,A;Schrodinger,E"
  thisyear= datetime.date.today().year

  #########################################################################
  parser = OptionParser()

  parser.add_option("-o", "--output-file"
                    , help="write to FILE. Default: standard output", metavar="FILE", default='-')
  parser.add_option("-f", "--format", default=None
                    , help="format of output, possible values are: short, full, bibtex, tex, html, xml   DEFAULT= bib")

  parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False
                    , help="Give some informational messages.")

  parser.add_option("-b", "--start-year", default=str(thisyear),
                    help="Starting year as integer (4 digits)")
  parser.add_option("-e", "--end-year", default=str(thisyear),
                    help="Ending year as integer (4 digits)")

  parser.add_option("--year", default= None,
                    help="--year=y is a shortcut to '--start-year=y --end-year=y'")

  parser.add_option("--start-month", default='1',
                    help="Starting month as integer (Jan == 1, Dec == 12)")
  parser.add_option("--end-month", default='12',
                    help="Ending month as integer (Jan == 1, Dec == 12)")
  parser.add_option("--author", default=autores,
                    help="list of semicolon separated author names as last,f")
  parser.add_option("--author-logic", default='OR',
                    help="Logic to use to search for authors. Default: 'OR'. Use 'AND' to get only common (to all authors) articles")
  # parser.add_option("--affiliation", default='Bariloche',
  #                   help="affiliation words, any non-alpha-numeric character separates")
  parser.add_option("--proxy", default=None,
                    help="Proxy used to connect")

  parser.add_option("--advanced-options", default=None,
                    help="""Additional options supported by Harvard. They should be written as option1:value1;option2:value2,...  
                          To get a list of options use: '--help-advanced-options'""")

  parser.add_option("--help-advanced-options", action="store_true", default=False,
                    help="Show information on additional options supported by Harvard ADS site")

  parser.add_option("-d","--save-dump"
                    , help="Save (dump) the database IN INTERNAL FORM")

  parser.add_option("", "--sort", default='key'
                    , help="Sort the items according to the following fields, for instance to sort them accoding to year and then author we would use --sort=year,author. In the same example, to sort in reverse order we would use: --sort=year,author,reverse. DEFAULT: key.")

  (op, args) = parser.parse_args()
  
  if op.help_advanced_options != False:
    if op.verbose:
      print 'Complete list of possible options supported by Harvard:'
      for k,v in ads.all_param.iteritems():
        print '  %18s : %s'%(k,v)
    else:
      print 'The more important parameters are:'
      for k,v in ads.param_relevantes.iteritems():
        print '  %18s : %s'%(k,v)
      print '** To get a complete list use also --verbose **'
    return 1
  
  if op.proxy != None: conexion={'http_proxy': op.proxy}
  else: conexion= {}

  available_formats= {'s':'short','f':'full','t':'latex','b':'bibtex','h':'html','x':'xml'}

  output_file= op.output_file

  if op.format == None:    # Guess a format
    if output_file != '-':
      ext= os.path.splitext(output_file)[1][1]
      if ext in 'tbhx': formato=available_formats.get(ext)
      else: formato='bibtex'
    else: formato='bibtex'
  else:
    formato=available_formats.get(op.format[0].lower())

  #########################################################################################
  opciones={}
  opciones['start_year']=op.start_year
  opciones['end_year']= op.end_year
  if op.year != None:  opciones['start_year']=opciones['end_year']= op.year
    
  opciones['start_mon']=op.start_month
  opciones['end_mon']= op.end_month
  opciones['author']= op.author
  opciones['aut_logic']= op.author_logic
  if op.advanced_options != None:
    for o in op.advanced_options.split(';'):
      k,v= o.split(':')
      opciones[k]= v
  #########################################################################################
  # Create the List object
  b= biblist.BibList()
  #########################################################################################
  Query= ads.AdsQuery(connection=conexion,options=opciones)
  nabst,page= Query.query()
  if nabst < 0:
    print 'Error (%d), %s' %(nabst,page)
    sys.exit()
  else:
    if op.verbose:  print '%d items downloaded' %(nabst)
    
  # Load the results into the biblist object
  fi= StringIO.StringIO(page)
  n= b.import_ads(fi)
  if op.verbose:  print '# %d items downloaded, total number of items %d' %(n, len(b.ListItems))

  sortorder= op.sort.lower().split(',')
  if 'reverse' in sortorder:      reverse=True
  else: reverse= False
  if reverse: sortorder.remove('reverse')
  b.sort(sortorder,reverse=reverse)

  if op.save_dump != None:
    if op.verbose:
      print '# Saving database to %s...' %(op.save_dump)
    b.dump(op.save_dump)

  b.output(output_file, formato, op.verbose)

  


if __name__ == "__main__":
  main()


### Local Variables: 
### tab-width: 2
### END:
